"""
Connection manager with  features for Browtrix.
"""

import asyncio
import json
import uuid
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
from fastapi import WebSocket
import structlog

from .errors import (
    BrowserConnectionError,
    BrowserTimeoutError,
    ValidationError,
)
from ..types.requests import BrowserRequest
from ..types.responses import BrowserResponse, ConnectionInfo, HealthCheckResponse
from ...settings import settings

logger = structlog.get_logger(__name__)


class ConnectionHealthMonitor:
    """Monitor connection health and detect stale connections."""

    def __init__(self, max_idle_time: float = 1800.0):
        self.max_idle_time = max_idle_time
        self.last_activity: Dict[str, datetime] = {}

    def update_activity(self, connection_id: str):
        """Update last activity timestamp for a connection."""
        self.last_activity[connection_id] = datetime.now(timezone.utc)

    def is_healthy(self, connection_id: str) -> bool:
        """Check if connection is still healthy."""
        if connection_id not in self.last_activity:
            return True  # New connections are considered healthy

        last_activity = self.last_activity[connection_id]
        return datetime.now(timezone.utc) - last_activity < timedelta(
            seconds=self.max_idle_time
        )

    def get_stale_connections(self) -> List[str]:
        """Get list of connections that are stale."""
        stale = []
        for connection_id, last_activity in self.last_activity.items():
            if datetime.now(timezone.utc) - last_activity > timedelta(
                seconds=self.max_idle_time
            ):
                stale.append(connection_id)
        return stale


class ConnectionManager:
    """Manage browser connections with health monitoring and statistics."""

    def __init__(
        self,
        max_connections: Optional[int] = None,
        request_timeout: Optional[float] = None,
        health_check_interval: Optional[float] = None,
    ):
        # Use settings if not provided
        self.max_connections = (
            max_connections if max_connections is not None else settings.max_connections
        )
        self.request_timeout = (
            request_timeout if request_timeout is not None else settings.request_timeout
        )
        self.health_check_interval = (
            health_check_interval
            if health_check_interval is not None
            else settings.health_check_interval
        )

        # Connection tracking
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_info: Dict[str, ConnectionInfo] = {}
        self.pending_futures: Dict[str, asyncio.Future] = {}

        # Request tracking
        self.request_history: List[Dict[str, Any]] = []
        self.active_requests: Dict[str, BrowserRequest] = {}

        # Health monitoring
        self.health_monitor = ConnectionHealthMonitor(
            max_idle_time=settings.max_idle_time
        )
        self.start_time = time.time()

        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.average_response_time = 0.0

        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None):
        """Establish connection with tracking."""
        connection_id = str(uuid.uuid4())

        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008, reason="Connection limit reached")
            raise BrowserConnectionError(
                "Maximum connection limit reached", connection_state="rejected"
            )

        await websocket.accept()
        self.active_connections[connection_id] = websocket

        # Create connection info
        current_time = datetime.now(timezone.utc)
        connection_info = ConnectionInfo(
            connection_id=connection_id,
            browser_id=client_id,
            user_agent=websocket.headers.get("user-agent"),
            is_active=True,  # Mark as active immediately
            last_activity=current_time,  # Set initial activity
        )
        self.connection_info[connection_id] = connection_info
        self.health_monitor.update_activity(connection_id)

        logger.info(
            "New connection established",
            connection_id=connection_id,
            client_id=client_id,
            total_connections=len(self.active_connections),
        )

        return connection_id

    def disconnect(self, connection_id: str):
        """Disconnect and cleanup resources."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            self.health_monitor.last_activity.pop(connection_id, None)

            if connection_id in self.connection_info:
                self.connection_info[connection_id].is_active = False

        logger.info(
            "Connection disconnected",
            connection_id=connection_id,
            remaining_connections=len(self.active_connections),
        )

    async def send_request(
        self, request: BrowserRequest, connection_id: Optional[str] = None
    ) -> BrowserResponse:
        """Send request with error handling and retry logic."""
        if not self.active_connections:
            raise BrowserConnectionError(
                "No web client connected. Please open the web app."
            )

        # Select connection
        if connection_id:
            if connection_id not in self.active_connections:
                raise BrowserConnectionError(f"Connection {connection_id} not found")
            target_connection = connection_id
        else:
            # Use the most recently active connection
            target_connection = self._select_best_connection()

        websocket = self.active_connections[target_connection]
        future = asyncio.Future()
        self.pending_futures[request.id] = future
        self.active_requests[request.id] = request

        # Track statistics
        request_start_time = time.time()
        self.total_requests += 1

        try:
            # Send request
            request_data = request.model_dump()
            logger.info(
                "Sending WebSocket request",
                request_id=request.id,
                request_type=request.type,
                connection_id=target_connection,
                request_data=request_data,
            )
            await websocket.send_json(request_data)
            self.health_monitor.update_activity(target_connection)

            # Wait for response
            logger.info(
                "Waiting for response", request_id=request.id, timeout=request.timeout
            )
            response = await asyncio.wait_for(future, timeout=request.timeout)
            self.successful_requests += 1

            # Update statistics
            response_time = time.time() - request_start_time
            self._update_response_time_stats(response_time)

            return response

        except asyncio.TimeoutError:
            self.failed_requests += 1
            raise BrowserTimeoutError(
                f"Browser did not respond in {request.timeout}s",
                operation=request.type,
                timeout_duration=request.timeout,
            )
        except Exception as e:
            self.failed_requests += 1
            logger.error(
                "Request failed",
                request_id=request.id,
                connection_id=target_connection,
                error=str(e),
                exc_info=True,
            )
            raise
        finally:
            # Cleanup
            self.pending_futures.pop(request.id, None)
            self.active_requests.pop(request.id, None)
            self.request_history.append(
                {
                    "request_id": request.id,
                    "type": request.type,
                    "timestamp": datetime.now(timezone.utc),
                    "duration": time.time() - request_start_time,
                    "success": True if "response" in locals() else False,
                }
            )

            # Keep only last 1000 requests
            if len(self.request_history) > 1000:
                self.request_history = self.request_history[-1000:]

    def _select_best_connection(self) -> str:
        """Select the best available connection."""
        if not self.active_connections:
            raise BrowserConnectionError("No active connections available")

        # Find the most recently active healthy connection
        for connection_id, last_activity in reversed(
            list(self.health_monitor.last_activity.items())
        ):
            if (
                connection_id in self.active_connections
                and self.health_monitor.is_healthy(connection_id)
            ):
                return connection_id

        # Fallback to any active connection
        return list(self.active_connections.keys())[-1]

    async def handle_message(self, data: str, connection_id: str):
        """Handle incoming message with parsing."""
        try:
            message_data = json.loads(data)
            msg_type = message_data.get("type")
            req_id = message_data.get("id")

            logger.info(
                "Received WebSocket message",
                connection_id=connection_id,
                message_type=msg_type,
                request_id=req_id,
                message_data=message_data,
            )

            self.health_monitor.update_activity(connection_id)

            if req_id and req_id in self.pending_futures:
                future = self.pending_futures[req_id]

                if not future.done():
                    try:
                        # Validate response format
                        response = BrowserResponse(**message_data)
                        if not response.success:
                            future.set_exception(
                                BrowserConnectionError(
                                    response.error or "Unknown error from browser"
                                )
                            )
                        else:
                            future.set_result(response)
                    except Exception as e:
                        future.set_exception(
                            ValidationError(
                                "response",
                                message_data,
                                f"Invalid response format: {str(e)}",
                            )
                        )

                del self.pending_futures[req_id]
                logger.debug(
                    "Message processed",
                    request_id=req_id,
                    connection_id=connection_id,
                    type=msg_type,
                )
        except json.JSONDecodeError:
            logger.error(
                "Invalid JSON received",
                connection_id=connection_id,
                raw_data=data[:100] + "..." if len(data) > 100 else data,
            )
        except Exception as e:
            logger.error(
                "Error handling message",
                connection_id=connection_id,
                error=str(e),
                exc_info=True,
            )

    def get_health_status(self) -> HealthCheckResponse:
        """Get comprehensive health status."""
        current_time = datetime.now(timezone.utc)

        # Calculate uptime
        uptime_seconds = time.time() - self.start_time

        # Check connection health
        active_connections = len(self.active_connections)
        healthy_connections = sum(
            1
            for conn_id in self.active_connections.keys()
            if self.health_monitor.is_healthy(conn_id)
        )

        # Determine overall status
        if active_connections == 0:
            status = "degraded"
        elif healthy_connections < active_connections:
            status = "degraded"
        elif len(self.pending_futures) > 10:  # Too many pending requests
            status = "degraded"
        else:
            status = "healthy"

        return HealthCheckResponse(
            id=str(uuid.uuid4()),
            status=status,
            version="1.0.0",
            uptime_seconds=uptime_seconds,
            connections=active_connections,
            last_activity=max(
                (self.health_monitor.last_activity.values())
                if self.health_monitor.last_activity
                else [current_time]
            ),
            components={
                "connections": "up" if active_connections > 0 else "down",
                "websocket": "up",
                "request_queue": "up" if len(self.pending_futures) < 50 else "degraded",
            },
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics."""
        return {
            "total_connections": len(self.active_connections),
            "active_requests": len(self.pending_futures),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (
                self.successful_requests / max(self.total_requests, 1) * 100
            ),
            "average_response_time": self.average_response_time,
            "pending_requests": list(self.pending_futures.keys()),
            "connection_info": [
                info.model_dump(mode="json") for info in self.connection_info.values()
            ],
        }

    def _update_response_time_stats(self, response_time: float):
        """Update response time statistics."""
        if self.average_response_time == 0:
            self.average_response_time = response_time
        else:
            # Running average
            self.average_response_time = (self.average_response_time * 0.9) + (
                response_time * 0.1
            )

    async def start_health_monitoring(self):
        """Start background health monitoring tasks."""
        if not self._health_check_task:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_health_monitoring(self):
        """Stop background health monitoring tasks."""
        if self._health_check_task:
            self._health_check_task.cancel()
            self._health_check_task = None
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None

    async def _health_check_loop(self):
        """Background health check loop."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Health check error", error=str(e), exc_info=True)

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._cleanup_stale_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Cleanup error", error=str(e), exc_info=True)

    async def _perform_health_checks(self):
        """Perform health checks on connections."""
        stale_connections = self.health_monitor.get_stale_connections()

        for connection_id in stale_connections:
            logger.warning(
                "Cleaning up stale connection",
                connection_id=connection_id,
                idle_time=time.time()
                - self.health_monitor.last_activity[connection_id].timestamp()
                if hasattr(
                    self.health_monitor.last_activity[connection_id], "timestamp"
                )
                else "unknown",
            )
            self.disconnect(connection_id)

    async def _cleanup_stale_data(self):
        """Clean up stale data from history."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

        # Clean old requests
        self.request_history = [
            req for req in self.request_history if req["timestamp"] > cutoff_time
        ]

        # Clean old connection info
        current_time = datetime.now(timezone.utc)
        for conn_id in list(self.connection_info.keys()):
            info = self.connection_info[conn_id]
            if not info.is_active and current_time - info.connected_at > timedelta(
                hours=24
            ):
                del self.connection_info[conn_id]
