# Browtrix  MCP Server

A production-ready, enterprise-grade Model Context Protocol (MCP) server for browser automation with  features,  error handling, and comprehensive monitoring capabilities.

## 🚀 Features

### Core Capabilities
- ** HTML Snapshots** - Configurable snapshot options with wait mechanisms
- **Alert System** - Customizable confirmation alerts with timeout handling
- **Smart Popup Tools** - Input validation with multiple field types and regex patterns
- **Backward Compatibility** - Legacy tools maintained for existing integrations

### Architecture & Performance
- **Modular Design** - Clean separation of concerns with dedicated modules
- ** Connection Management** - Connection pooling, health monitoring, and automatic cleanup
- **Type-Safe Tools** - Pydantic models for input validation and structured responses
- **Resource Management** - Browser session tracking with usage analytics

### Monitoring & Observability
- **Health Check Endpoints** - `/health`, `/stats`, `/info` for monitoring
- **Structured Logging** - JSON-formatted logs with correlation IDs
- **Real-time Statistics** - Request metrics, success rates, and performance data
- **Usage Analytics** - Resource usage patterns and access frequency tracking

### Security & Reliability
- **Custom Exception Handling** - Specific error types for better debugging
- **Request Validation** - Comprehensive input validation and sanitization
- **Timeout Management** - Configurable timeouts with graceful degradation
- **Connection Limits** - Protection against resource exhaustion

## 📁 Architecture

```
src/browtrix_server/
├── core/
│   ├── __init__.py              # Core module exports
│   ├── tools/
│   │   ├── __init__.py          # Tool implementations
│   │   ├── base.py              # Base tool classes
│   │   ├── snapshot_tool.py     # HTML snapshot tools
│   │   ├── alert_tool.py        # Confirmation alert tools
│   │   └── popup_tool.py        # Input popup tools
│   ├── connection/
│   │   ├── __init__.py          # Connection management
│   │   ├── manager.py           #  connection manager
│   │   └── errors.py            # Custom exceptions
│   ├── types/
│   │   ├── __init__.py          # Type definitions
│   │   ├── requests.py          # Request models
│   │   └── responses.py         # Response models
│   └── resources.py             # Resource management system
├── _server.py           # Main  server
├── server.py                    # Legacy server (backward compatibility)
├── settings.py                  # Configuration management
└── connection_manager.py        # Original connection manager
```

## 🛠️ Installation

### Quick Start
```bash
# Install dependencies
cd browtrix/apps/server
uv sync

# Run  server
python -m browtrix_server.__main__

# Or use the CLI entry point
browtrix-
```

### Development Setup
```bash
# Install development dependencies
uv sync --dev

# Run tests
python test__server.py

# Type checking
ty check

# Linting
ruff check .
```

## 🔧 Configuration

### Environment Variables
```bash
# Server Configuration
BROWTRIX_HOST=0.0.0.0
BROWTRIX_PORT=8000
BROWTRIX_LOG_LEVEL=info

#  Features
BROWTRIX_MAX_CONNECTIONS=10
BROWTRIX_REQUEST_TIMEOUT=30.0
BROWTRIX_HEALTH_CHECK_INTERVAL=60.0
```

### Server Configuration
```python
from browtrix_server.__main__ import ServerConfig, BrowtrixServer

config = ServerConfig(
    host="0.0.0.0",
    port=8000,
    max_connections=10,
    request_timeout=30.0,
    enable_health_checks=True
)

server = BrowtrixServer(config)
```

## 🎯 API Reference

###  Tools

#### HTML Snapshot Tool
```python
#  version with options
browtrix_html_snapshot_(
    wait_for: Optional[str] = None,     # CSS selector to wait for
    full_page: bool = True,             # Capture full page
    wait_timeout: int = 10,             # Wait timeout (seconds)
    quality: int = 100                  # Snapshot quality (1-100)
) -> str

# Legacy version (backward compatible)
browtrix_html_snapshot(message: str = "") -> str
```

#### Confirmation Alert Tool
```python
#  version with options
browtrix_confirmation_alert_(
    message: str,                       # Alert message
    title: str = "Confirmation",        # Alert title
    timeout: int = 60                   # Timeout (seconds)
) -> bool

# Legacy version (backward compatible)
browtrix_confirmation_alert(message: str) -> bool
```

#### Question Popup Tool
```python
#  version with options
browtrix_question_popup_(
    question: str,                      # Question text
    title: str = "Input Required",      # Popup title
    input_type: str = "text",           # Input field type
    validation: str = "any"             # Validation type
) -> str

# Legacy version (backward compatible)
browtrix_question_popup(question: str) -> str
```

### Health Check Endpoints

#### GET /health
Returns server health status:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600.0,
  "connections": 2,
  "last_activity": "2025-11-19T21:40:00Z",
  "components": {
    "connections": "up",
    "websocket": "up",
    "request_queue": "up"
  }
}
```

#### GET /stats
Returns detailed server statistics:
```json
{
  "total_connections": 2,
  "active_requests": 1,
  "total_requests": 156,
  "successful_requests": 148,
  "failed_requests": 8,
  "success_rate": 94.87,
  "average_response_time": 0.234,
  "pending_requests": ["req_abc123"],
  "connection_info": [...]
}
```

#### GET /info
Returns server information and features:
```json
{
  "name": "Browtrix  MCP Server",
  "version": "1.0.0",
  "description": " Model Context Protocol server for browser automation",
  "features": [
    " HTML snapshots",
    "Configurable alerts and popups",
    "Health monitoring",
    "Connection pooling",
    "Structured logging",
    "Backward compatibility"
  ],
  "timestamp": "2025-11-19T21:40:00Z"
}
```

## 🔍 WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected to Browtrix  Server');
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
};
```

### Request Format
```json
{
  "id": "req_abc123",
  "type": "GET_SNAPSHOT",
  "wait_for": ".content",
  "full_page": true,
  "timeout": 30.0
}
```

### Response Format
```json
{
  "id": "req_abc123",
  "success": true,
  "data": {
    "html_content": "<!DOCTYPE html>...",
    "page_url": "https://example.com",
    "page_title": "Example Page",
    "content_size": 45672
  },
  "execution_time_ms": 145.6
}
```

## 🧪 Testing

### Run Test Suite
```bash
# Test  server functionality
python test__server.py

# Expected output:
# 🧪 Testing  Browtrix Server...
# 
# 1. Testing server initialization...
# ✅ Server initialized successfully
# 
# 2. Testing connection manager...
# ✅  connection manager created
# 
# 3. Testing health check...
# ✅ Health status: healthy
# 
# 4. Testing statistics...
# ✅ Statistics retrieved: 0 connections
# 
# 5. Testing tool registration...
# ✅ Tool registered: browtrix_html_snapshot_
# ✅ Tool registered: browtrix_confirmation_alert_
# ✅ Tool registered: browtrix_question_popup_
# ✅ Tool registered: browtrix_html_snapshot
# ✅ Tool registered: browtrix_confirmation_alert
# ✅ Tool registered: browtrix_question_popup
# 
# 📊 Total tools registered: 6
# 
# 6. Testing resource management...
# ✅ Test resource created: res_xyz789
# ✅ Resource stats: 1 resources
# 
# 🎉 All tests completed successfully!
```

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "browtrix_server.__main__"]
```

### Production Configuration
```python
# Production server configuration
config = ServerConfig(
    host="0.0.0.0",
    port=8000,
    max_connections=50,          # Higher connection limit
    request_timeout=60.0,        # Extended timeout
    enable_health_checks=True    # Enable monitoring
)

server = BrowtrixServer(config)
```

### Health Check Integration
```bash
# Docker health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

## 📊 Monitoring

### Metrics Available
- **Connection Metrics** - Active connections, connection health
- **Request Metrics** - Total requests, success rate, response times
- **Tool Usage** - Most used tools, execution times
- **Resource Metrics** - Browser session count, resource utilization
- **System Health** - Server uptime, component status

### Logging
Structured JSON logging with the following fields:
- `timestamp` - ISO format timestamp
- `level` - Log level (INFO, WARNING, ERROR)
- `logger` - Logger name
- `event` - Event type
- `request_id` - Correlation ID for request tracking
- `connection_id` - Connection identifier
- `tool_name` - Tool being executed
- Additional context-specific fields

## 🔧 Troubleshooting

### Common Issues

#### Connection Refused
```bash
# Check if server is running
curl http://localhost:8000/health

# Verify port is not in use
lsof -i :8000
```

#### Tool Execution Timeout
- Increase timeout in tool configuration
- Check browser connection status
- Verify WebSocket connectivity

#### Memory Usage
- Monitor connection count via `/stats` endpoint
- Adjust `max_connections` configuration
- Enable resource cleanup

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Server will now output detailed debug logs
```

## 🤝 Contributing

### Development Setup
1. Install development dependencies: `uv sync --dev`
2. Run tests: `python test__server.py`
3. Check code quality: `ruff check . && ty check`
4. Follow the existing code patterns and architecture

### Adding New Tools
1. Create tool class inheriting from `BaseBrowtrixTool`
2. Add request/response models in `core/types/`
3. Register tool in  server
4. Add tests and documentation

## 📄 License

This project is part of the Browtrix ecosystem. See the main project license for details.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section above
- Review server logs for detailed error information
- Use health check endpoints for system diagnostics
- Monitor statistics endpoint for performance insights

---

** Browtrix Server v1.0.0** - Production-ready MCP server with enterprise features
