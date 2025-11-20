# How to Add Browtrix MCP Server to MCP Clients

This guide shows you how to connect to the Browtrix MCP server. **Note: This is an HTTP MCP server with SSE transport.**

## Quick Start

### 1. Start the Server

First, start the Browtrix MCP server:

```bash
# Navigate to the server directory
cd /home/pasindui/Desktop/marketrix.ai/browtrix/apps/server

# Install dependencies
uv sync

# Start the server (runs on http://localhost:8000 by default)
uv run python -m browtrix_server.__main__
```

### 2. Verify Server is Running

Test that the server is accessible:

```bash
# Check health endpoint
curl http://localhost:8000/health

# Should return: {"status": "healthy", ...}
```

## MCP Client Configuration

**Important**: This is an HTTP MCP server, so you need to connect via HTTP/SSE, not as a subprocess.

### Using Direct HTTP/SSE Connection

Most MCP clients support HTTP/SSE connection. Configure them to connect to:

```
http://localhost:8000/
```

### For MCP Clients that Need URL Configuration

If your MCP client asks for a server URL, use:

```
http://localhost:8000/
```

### For Claude Desktop/Claude Code (Advanced)

For clients that need a custom configuration, you might need to use a proxy or middleware:

```json
{
  "mcpServers": {
    "browtrix": {
      "command": "python",
      "args": ["-m", "http.server", "8001"],
      "cwd": "/tmp"
    }
  }
}
```

**Note**: You may need custom MCP client support for HTTP/SSE servers, or use a proxy tool.

## Available Tools

Once connected to the server, these tools are available:

### 1. `browtrix_html_snapshot`
Capture HTML snapshots of web pages.

**Parameters:**
- `wait_for` (optional): CSS selector to wait for before capturing
- `full_page` (optional): Capture full page (default: true)
- `wait_timeout` (optional): Wait timeout in seconds (default: 10)
- `quality` (optional): Snapshot quality 1-100 (default: 100)

**Example usage:**
```python
# When connected via HTTP/SSE
html_content = await browtrix_html_snapshot(
    wait_for=".main-content",
    full_page=True,
    quality=90
)
```

### 2. `browtrix_confirmation_alert`
Display confirmation alerts to users.

**Parameters:**
- `message`: Alert message text
- `title` (optional): Alert title (default: "Confirmation")
- `timeout` (optional): Timeout in seconds (default: 60)

**Example usage:**
```python
confirmed = await browtrix_confirmation_alert(
    message="Do you want to proceed?",
    title="Confirm Action",
    timeout=30
)
```

### 3. `browtrix_question_popup`
Display input dialogs for user input.

**Parameters:**
- `question`: Question or prompt text
- `title` (optional): Popup title (default: "Input Required")
- `input_type` (optional): Input field type (default: "text")
- `validation` (optional): Validation type (default: "any")

**Example usage:**
```python
user_input = await browtrix_question_popup(
    question="Enter your email:",
    title="Email Input",
    input_type="email",
    validation="email"
)
```

## Server Management

### Check Server Status

```bash
# Health check
curl http://localhost:8000/health

# Statistics
curl http://localhost:8000/stats

# Server info
curl http://localhost:8000/info
```

### Custom Configuration

Change the server port:
```bash
export BROWTRIX_PORT=8080
uv run python -m browtrix_server.__main__
```

Change the server host:
```bash
export BROWTRIX_HOST=0.0.0.0  # Listen on all interfaces
uv run python -m browtrix_server.__main__
```

## Development Setup

### Install Development Dependencies

```bash
cd /home/pasindui/Desktop/marketrix.ai/browtrix/apps/server
uv sync --dev
```

### Run Tests

```bash
uv run python test_mcp_server.py
```

### Check Available Tools

```bash
# The server exposes MCP tools at the root path
curl http://localhost:8000/
```

## Troubleshooting

### Server Won't Start

1. Check if port 8000 is available:
```bash
lsof -i :8000
```

2. Ensure dependencies are installed:
```bash
uv sync
```

3. Check for Python errors:
```bash
uv run python -m browtrix_server.__main__
```

### Client Can't Connect

1. **Verify server is running**: `curl http://localhost:8000/health`
2. **Check firewall settings**: Ensure port 8000 is accessible
3. **Confirm HTTP/SSE support**: Your MCP client must support HTTP/SSE transport
4. **Check client logs**: Look for connection or transport errors

### Tools Not Available

1. **Verify server health**: `curl http://localhost:8000/health`
2. **Check server logs**: Look for tool registration errors
3. **Restart server and client**: Sometimes a fresh start helps

### MCP Client Doesn't Support HTTP/SSE

If your MCP client only supports subprocess-based servers:

1. **Check client documentation**: Many modern clients support HTTP/SSE
2. **Use a proxy**: Some tools can wrap HTTP servers as subprocess servers
3. **Request feature**: Ask the MCP client maintainers to add HTTP/SSE support

## Production Deployment

### Using Process Manager

**Systemd service example:**
```ini
[Unit]
Description=Browtrix MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/pasindui/Desktop/marketrix.ai/browtrix/apps/server
ExecStart=/usr/bin/uv run python -m browtrix_server.__main__
Restart=always

[Install]
WantedBy=multi-user.target
```

### Using Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "browtrix_server.__main__"]
```

### Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Considerations

1. **Network Access**: By default, server listens on localhost only
2. **Firewall**: Configure firewall rules for production
3. **HTTPS**: Use reverse proxy with SSL for production
4. **Authentication**: Consider adding auth if needed

---

**Need Help?**
- Check server logs and health endpoints
- Ensure your MCP client supports HTTP/SSE transport
- Verify server is running and accessible
