# Environment Configuration Guide

## Overview

Browtrix MCP Server uses environment variables for all configuration. This makes it easy to deploy across different environments without code changes.

## Quick Start

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Modify values in `.env` as needed for your environment.

3. For local development overrides, create `.env.local` (this file is ignored by git).

## Configuration Categories

### 🖥️ Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Host address to bind the server to |
| `PORT` | `8000` | Port number for the server |
| `LOG_LEVEL` | `info` | Logging level (debug, info, warning, error) |

### 🔗 Connection Management

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_CONNECTIONS` | `10` | Maximum concurrent browser connections |
| `REQUEST_TIMEOUT` | `30.0` | Default request timeout in seconds |
| `ENABLE_HEALTH_CHECKS` | `true` | Enable/disable health check endpoints |

### 💓 Health Monitoring

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_IDLE_TIME` | `1800.0` | Maximum idle time before connection is stale (seconds) |
| `HEALTH_CHECK_INTERVAL` | `60.0` | Health check interval in seconds |

### 🛠️ Tool Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SNAPSHOT_DEFAULT_TIMEOUT` | `10` | Default snapshot wait timeout (seconds) |
| `SNAPSHOT_MAX_TIMEOUT` | `60` | Maximum snapshot wait timeout (seconds) |
| `ALERT_DEFAULT_TIMEOUT` | `60` | Default alert timeout (seconds) |
| `ALERT_MAX_TIMEOUT` | `300` | Maximum alert timeout (seconds) |

### 🔌 MCP Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_NAME` | `browtrix-server` | MCP server identifier |
| `MCP_SERVER_VERSION` | `1.0.0` | MCP server version |
| `MCP_TRANSPORT` | `sse` | Transport type (http, streamable-http, sse) |

### 🚀 Feature Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_METRICS` | `false` | Enable metrics collection |
| `ENABLE_CORS` | `true` | Enable CORS headers |
| `DEBUG_MODE` | `false` | Enable debug mode |

## Environment-Specific Configurations

### Development (.env.local)

```bash
# Faster feedback loops
PORT=8001
DEBUG_MODE=true
LOG_LEVEL=debug
REQUEST_TIMEOUT=10.0
ENABLE_METRICS=true
```

### Production

```bash
# Optimized for production
PORT=8000
DEBUG_MODE=false
LOG_LEVEL=info
MAX_CONNECTIONS=50
ENABLE_METRICS=true
```

### Railway/Cloud Deployment

```bash
# Railway provides PORT via environment
# Remove PORT from your .env file
HOST=0.0.0.0
MAX_CONNECTIONS=25
REQUEST_TIMEOUT=60.0
LOG_LEVEL=info
```

## Deployment Examples

### Railway

Set environment variables in Railway dashboard:
- Go to Settings → Environment Variables
- Add the variables you need
- Railway automatically provides `PORT`

### Render

Set environment variables in Render dashboard:
- Go to Service → Environment
- Add environment variables
- Render provides `PORT` automatically

### Docker

```dockerfile
# Dockerfile
ENV HOST=0.0.0.0
ENV PORT=8000
ENV MAX_CONNECTIONS=25
ENV LOG_LEVEL=info
```

### Docker Compose

```yaml
# docker-compose.yml
services:
  browtrix:
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - MAX_CONNECTIONS=25
      - LOG_LEVEL=info
      - DEBUG_MODE=false
```

## Validation

The server validates environment variables on startup:

- ✅ Valid values: Server starts normally
- ❌ Invalid values: Error message with guidance
- ⚠️ Missing values: Defaults are used

## Security Notes

- Never commit `.env` files to version control
- Use `.env.local` for local development secrets
- Use your hosting provider's secret management for production
- Review default timeouts for security implications

## Troubleshooting

### Port Already in Use
```bash
# Change port in .env
PORT=8001
```

### Connection Timeouts
```bash
# Increase timeouts for slow networks
REQUEST_TIMEOUT=60.0
SNAPSHOT_DEFAULT_TIMEOUT=30
```

### Debug Mode Issues
```bash
# Enable debug logging
DEBUG_MODE=true
LOG_LEVEL=debug
```

## Migration from Hardcoded Values

If upgrading from an older version with hardcoded values:

1. Copy `.env.example` to `.env`
2. Review default values match your previous configuration
3. Test locally before deploying
4. Update deployment environment variables

All hardcoded values have been replaced with environment variable defaults, so your existing configuration will continue to work without changes.