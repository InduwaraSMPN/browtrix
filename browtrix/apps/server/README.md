# Browtrix MCP Server

FastMCP-based Python backend server for the Browtrix application.

## Overview

This server provides MCP (Model Context Protocol) tools and services for the Browtrix browser automation platform. Built with FastMCP framework for high-performance HTTP-based tool execution.

## Requirements

- Python 3.13+
- uv (Python package manager)

## Installation

```bash
# Install dependencies
uv sync
```

## Development

Start the development server:

```bash
# Using npm script
npm run dev

# Or directly with uv
uv run python -m src.browtrix_server
```

The server will start on `http://0.0.0.0:8000` with HTTP transport enabled.

## Available Tools

### hello()
A simple greeting tool that returns "Hello from browtrix!"

```python
# Example usage
result = await hello()
# Returns: "Hello from browtrix!"
```

## Project Structure

```
server/
├── main.py          # Main FastMCP server application
├── pyproject.toml   # Python project configuration
├── package.json     # npm scripts for development
└── README.md        # This file
```

## Configuration

The server is configured to:
- Use HTTP transport on port 8000
- Bind to all interfaces (0.0.0.0)

## Adding New Tools

1. Define a new function with the `@mcp.tool()` decorator
2. Add proper docstring for tool documentation
3. Return structured data (JSON serializable)

Example:
```python
@mcp.tool()
def get_browser_info() -> dict:
    """Get current browser information"""
    return {
        "user_agent": "Browtrix/1.0",
        "version": "0.1.0"
    }
```

## Dependencies

- **fastmcp** (>=2.13.1): MCP server framework

## Scripts

- `npm run dev`: Start development server with auto-reload
- `npm run build`: Placeholder (Python backend doesn't require build)