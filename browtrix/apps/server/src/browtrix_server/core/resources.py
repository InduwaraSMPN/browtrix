"""
Resource management system for Browtrix server.
"""

import asyncio
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import structlog

logger = structlog.get_logger(__name__)


class BrowserResource(BaseModel):
    """Represents a browser resource or session."""

    resource_id: str = Field(default_factory=lambda: str(uuid4()))
    resource_type: str = "browser_session"
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class ResourceManager:
    """Manages browser resources and sessions."""

    def __init__(self, max_resources: int = 100, cleanup_interval: int = 3600):
        self.max_resources = max_resources
        self.cleanup_interval = cleanup_interval
        self.resources: Dict[str, BrowserResource] = {}
        self.access_patterns: Dict[str, List[datetime]] = {}
        self._cleanup_task = None
        self._start_time = datetime.now(timezone.utc)

    async def create_resource(
        self,
        resource_type: str = "browser_session",
        name: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BrowserResource:
        """Create a new browser resource."""

        # Clean up if at capacity
        if len(self.resources) >= self.max_resources:
            await self._cleanup_old_resources()

        resource = BrowserResource(
            resource_type=resource_type,
            name=name,
            data=data or {},
            metadata=metadata or {},
        )

        self.resources[resource.resource_id] = resource
        self.access_patterns[resource.resource_id] = [datetime.now(timezone.utc)]

        logger.info(
            "Resource created",
            resource_id=resource.resource_id,
            resource_type=resource_type,
            name=name,
        )

        return resource

    def get_resource(self, resource_id: str) -> Optional[BrowserResource]:
        """Get a resource by ID and update access time."""
        resource = self.resources.get(resource_id)
        if resource and resource.is_active:
            resource.last_accessed = datetime.now(timezone.utc)

            # Record access pattern
            if resource_id not in self.access_patterns:
                self.access_patterns[resource_id] = []
            self.access_patterns[resource_id].append(datetime.now(timezone.utc))

            # Keep only last 100 access records
            if len(self.access_patterns[resource_id]) > 100:
                self.access_patterns[resource_id] = self.access_patterns[resource_id][
                    -100:
                ]

        return resource

    def update_resource(
        self,
        resource_id: str,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update resource data and metadata."""
        resource = self.resources.get(resource_id)
        if not resource or not resource.is_active:
            return False

        if data:
            resource.data.update(data)
        if metadata:
            resource.metadata.update(metadata)

        resource.last_accessed = datetime.now(timezone.utc)

        logger.debug("Resource updated", resource_id=resource_id)
        return True

    def delete_resource(self, resource_id: str) -> bool:
        """Delete a resource."""
        if resource_id in self.resources:
            self.resources[resource_id].is_active = False
            self.resources[resource_id].last_accessed = datetime.now(timezone.utc)
            self.access_patterns.pop(resource_id, None)

            logger.info("Resource deactivated", resource_id=resource_id)
            return True

        return False

    def list_resources(
        self,
        resource_type: Optional[str] = None,
        active_only: bool = True,
        limit: Optional[int] = None,
    ) -> List[BrowserResource]:
        """List resources with optional filtering."""
        resources = []

        for resource in self.resources.values():
            if active_only and not resource.is_active:
                continue
            if resource_type and resource.resource_type != resource_type:
                continue

            resources.append(resource)

        # Sort by last accessed
        resources.sort(key=lambda r: r.last_accessed, reverse=True)

        if limit:
            resources = resources[:limit]

        return resources

    def get_resource_stats(self) -> Dict[str, Any]:
        """Get resource usage statistics."""
        now = datetime.now(timezone.utc)
        uptime = now - self._start_time

        # Calculate access frequency
        access_frequencies = {}
        for resource_id, accesses in self.access_patterns.items():
            recent_accesses = [
                access for access in accesses if now - access < timedelta(hours=24)
            ]
            access_frequencies[resource_id] = len(recent_accesses)

        # Resource type distribution
        type_distribution = {}
        for resource in self.resources.values():
            if resource.is_active:
                resource_type = resource.resource_type
                type_distribution[resource_type] = (
                    type_distribution.get(resource_type, 0) + 1
                )

        return {
            "total_resources": len(self.resources),
            "active_resources": len(
                [r for r in self.resources.values() if r.is_active]
            ),
            "resource_types": type_distribution,
            "uptime_hours": uptime.total_seconds() / 3600,
            "average_access_frequency": (
                sum(access_frequencies.values()) / max(len(access_frequencies), 1)
            ),
            "most_accessed_resource": (
                max(access_frequencies.items(), key=lambda x: x[1])[0]
                if access_frequencies
                else None
            ),
            "least_accessed_resource": (
                min(access_frequencies.items(), key=lambda x: x[1])[0]
                if access_frequencies
                else None
            ),
        }

    async def _cleanup_old_resources(self):
        """Clean up old inactive resources."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        inactive_resources = [
            resource_id
            for resource_id, resource in self.resources.items()
            if (not resource.is_active or resource.last_accessed < cutoff_time)
        ]

        for resource_id in inactive_resources:
            del self.resources[resource_id]
            self.access_patterns.pop(resource_id, None)

        if inactive_resources:
            logger.info("Cleaned up old resources", count=len(inactive_resources))

    def get_resource_usage_patterns(self, hours: int = 24) -> Dict[str, Any]:
        """Get resource usage patterns for the specified time period."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        active_resources = [
            resource
            for resource in self.resources.values()
            if resource.last_accessed >= cutoff_time
        ]

        # Hourly usage distribution
        hourly_usage = {}
        for hour in range(24):
            hourly_usage[hour] = 0

        for accesses in self.access_patterns.values():
            for access_time in accesses:
                if access_time >= cutoff_time:
                    hour = access_time.hour
                    hourly_usage[hour] += 1

        return {
            "resources_used_in_period": len(active_resources),
            "peak_hour": max(hourly_usage.items(), key=lambda x: x[1])[0],
            "lowest_hour": min(hourly_usage.items(), key=lambda x: x[1])[0],
            "hourly_distribution": hourly_usage,
            "average_resources_per_hour": sum(hourly_usage.values()) / 24,
        }

    async def start_cleanup_task(self):
        """Start background cleanup task."""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup_task(self):
        """Stop background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_old_resources()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Resource cleanup error", error=str(e), exc_info=True)


# Global resource manager instance
_resource_manager: Optional[ResourceManager] = None


def get_resource_manager() -> ResourceManager:
    """Get or create global resource manager."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


class BrowserStateResource:
    """MCP resource for browser state information."""

    def __init__(self, resource_manager: ResourceManager):
        self.resource_manager = resource_manager

    async def list_browser_sessions(self) -> List[Dict[str, Any]]:
        """List all active browser sessions."""
        sessions = self.resource_manager.list_resources(
            "browser_session", active_only=True
        )
        return [
            {
                "session_id": session.resource_id,
                "name": session.name,
                "created_at": session.created_at.isoformat(),
                "last_accessed": session.last_accessed.isoformat(),
                "data_keys": list(session.data.keys()),
                "metadata": session.metadata,
            }
            for session in sessions
        ]

    async def get_browser_session_info(
        self, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information about a browser session."""
        session = self.resource_manager.get_resource(session_id)
        if not session:
            return None

        usage_patterns = self.resource_manager.get_resource_usage_patterns()

        return {
            "session_id": session.resource_id,
            "name": session.name,
            "created_at": session.created_at.isoformat(),
            "last_accessed": session.last_accessed.isoformat(),
            "data": session.data,
            "metadata": session.metadata,
            "is_active": session.is_active,
            "resource_stats": self.resource_manager.get_resource_stats(),
            "usage_patterns": usage_patterns,
        }
