# Browtrix MCP Server

A powerful Model Context Protocol (MCP) server for browser automation that provides seamless integration between AI assistants and web browsers through a comprehensive set of tools for capturing, interacting with, and monitoring web pages. Built with FastAPI, Uvicorn, and Pydantic for high-performance async operations and robust type safety.

## Features

### Core Browser Automation Tools
- **HTML Snapshot Tool**: Capture complete HTML snapshots with advanced options for dynamic content
- **Confirmation Alert Tool**: Display modal dialogs for user confirmation and human-in-the-loop workflows
- **Question Popup Tool**: Collect validated user input through interactive modal forms

### Infrastructure & Monitoring
- **Real-time WebSocket Connections**: Manage multiple browser connections with connection pooling
- **Health Monitoring**: Comprehensive health checks and server statistics
- **Structured Logging**: JSON-based logging with detailed performance metrics
- **FastAPI Integration**: High-performance async HTTP server with automatic API documentation
- **Type Safety**: Full Pydantic validation and type hints throughout

## Development Stack

### Core Framework
- **Framework**: FastMCP Model Context Protocol server
- **Web Framework**: FastAPI with automatic API documentation
- **ASGI Server**: Uvicorn for high-performance async operations
- **Validation**: Pydantic data validation with Python type annotations
- **Communication**: Real-time WebSocket connections
- **Logging**: Structured JSON logging with structlog
- **Package Manager**: uv or pip

### Development Tools
- **Testing**: pytest with async support and coverage reporting
- **Type Checking**: typer for static type validation
- **Linting**: ruff for fast code linting and formatting
- **Dependencies**: pyproject.toml for modern Python packaging

## Quick Start

### Prerequisites
- Python 3.12+ or uv for package management
- Git for version control

### Installation

# Clone the repository
```bash
git clone https://github.com/InduwaraSMPN/browtrix.git
```
```bash
cd browtrix/apps/server
```

# Install dependencies with uv
```bash
uv install
```

# Or with pip
```bash
pip install -e .```

### Environment Variables

The server uses a comprehensive configuration system based on environment variables.

1. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```

2. Configure your environment variables in `.env`.

See [ENVIRONMENT.md](ENVIRONMENT.md) for a complete list of available configuration options.

### Development

# Start development server with uv
```bash
uv run python -m browtrix_server.__main__
```

# Or using npm script
```bash
npm run dev
```
# The server will be available at http://localhost:8000

### Production

# Start production server with uv
```bash
uv run python -m browtrix_server.__main__
```

# Or using npm script
```bash
npm run start
```

## Project Structure

```
src/browtrix_server/
├── __main__.py              # Entry point
├── server.py                # Main server implementation
├── settings.py              # Configuration settings
├── core/
│   ├── __init__.py
│   ├── connection/          # WebSocket connection management
│   ├── tools/               # MCP tool implementations
│   └── types/               # Type definitions
└── tests/                   # Test suite
```

## Available Scripts

- `dev` - Start development server on port 8000
- `start` - Start production server
- `test` - Run pytest test suite
- `check-types` - Type checking with typer
- `lint` - Code linting with ruff
- `lint-fix` - Auto-fix linting issues
- `format` - Code formatting with ruff

## MCP Integration

The Browtrix MCP server provides powerful browser automation tools:

### Available Tools

#### 1. HTML Snapshot (`html_snapshot`)
Captures a complete HTML snapshot of the current browser page with advanced rendering options.

**Parameters:**
- `wait_for` (optional): CSS selector to wait for before capturing
- `full_page` (default: true): Capture full page or just viewport
- `wait_timeout` (default: 10): Max wait time in seconds (1-60)
- `quality` (default: 100): Reserved for future screenshot functionality

**Use Cases:**
- Capturing dynamically-loaded content after AJAX requests
- Extracting full page HTML for analysis or archival
- Taking snapshots after specific elements render
- Monitoring page state changes over time

**Example:**
```python
# Wait for a data table to load before capturing
html_snapshot(
    wait_for='table.data-loaded',
    full_page=True,
    wait_timeout=15
)
```

#### 2. Confirmation Alert (`confirmation_alert`)
Displays a modal confirmation dialog requiring user interaction.

**Parameters:**
- `message` (required): Confirmation message to display
- `title` (default: "Confirmation"): Dialog title
- `timeout` (default: 60): Max wait time in seconds (5-300)

**Use Cases:**
- Confirming destructive actions before execution
- Requesting user approval in workflow steps
- Human-in-the-loop validation for AI automation
- Gathering explicit consent for data operations

**Example:**
```python
# Simple confirmation
confirmation_alert(
    message="Are you sure you want to delete these 42 files?",
    title="Delete Confirmation",
    timeout=30
)
```

#### 3. Question Popup (`question_popup`)
Displays an interactive input modal to collect validated user input.

**Parameters:**
- `question` (required): Question or prompt to display
- `title` (default: "Input Required"): Dialog title
- `input_type` (default: "text"): HTML input type (text, email, password, number)
- `validation` (default: "any"): Validation rule (any, email, number, url, regex)

**Use Cases:**
- Collecting user credentials during authentication
- Gathering configuration parameters (API keys, URLs)
- Requesting data for form auto-filling
- Human-in-the-loop data entry for AI workflows

**Example:**
```python
# Collect email address
question_popup(
    question="Enter your email address to receive notifications",
    title="Email Setup",
    input_type="email",
    validation="email"
)
```

## API Endpoints

### HTTP Endpoints
- `GET /health` - Health check endpoint
- `GET /stats` - Server statistics and metrics
- `GET /info` - Server information and capabilities
- `GET /mcp/*` - Model Context Protocol endpoints

### WebSocket Endpoint
- `WS /ws` - Real-time browser connection management

## Development Workflow

# Code quality checks: Lint code with ruff
```bash
npm run lint
```

# Code quality checks: Type checking with typer
```bash
npm run check-types
```

# Code quality checks: Format code with ruff
```bash
npm run format
```

# Development: Start development server
```bash
npm run dev
```

# Development: Run pytest test suite
```bash
npm run test
```

# Build validation: Run all tests with coverage
```bash
npm run test
```

## Testing

### Running Tests

# Run all tests
```bash
npm run test
```

# Or with uv directly
```bash
uv run pytest src/browtrix_server/tests
```

# Run with coverage
```bash
npm run test --cov=src/browtrix_server
```

### Test Structure
- Unit tests for individual tools and components
- Integration tests for API endpoints
- WebSocket connection testing
- Error handling and edge case validation

## Monitoring and Health

The server includes comprehensive monitoring:

### Health Endpoints
- `/health` - Server health status
- `/stats` - Server statistics and metrics
- `/info` - Server information and capabilities

### Logging
- Structured JSON logging with consistent format
- Request/response timing metrics
- Error tracking with full stack traces
- Connection lifecycle monitoring

### Performance Features
- **Async Operations**: High-performance async request handling
- **Connection Pooling**: Efficient WebSocket connection management
- **Structured Logging**: Optimized JSON logging for production
- **Health Monitoring**: Real-time server health checks

## Dependencies

### Core Dependencies
- `fastmcp>=2.13.1`: MCP server framework
- `fastapi>=0.110.0`: Web framework
- `uvicorn[standard]>=0.29.0`: ASGI server
- `websockets>=12.0`: WebSocket support
- `pydantic-settings>=2.0.0`: Settings management
- `aiohttp>=3.13.2`: HTTP client
- `structlog>=24.0.0`: Structured logging

### Development Dependencies
- `pytest>=9.0.1`: Testing framework
- `pytest-asyncio>=1.3.0`: Async testing support
- `ty>=0.0.1a27`: Type checking
- `ruff>=0.6.0`: Linting and formatting
- `pytest-cov>=7.0.0`: Coverage reporting
- `freezegun>=1.5.5`: Time mocking for tests

## Security Considerations

- Input validation using Pydantic models
- WebSocket connection limits and timeouts
- Sanitized HTML content handling
- Configurable request timeouts
- Error information sanitization in responses

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style
This project uses ruff for code formatting and linting. Ensure your code passes all checks:

```bash
npm run lint
```
```bash
npm run check-types
```

## Environment Setup

### Development Environment

# Install dependencies
```bash
uv install
```

# Start development server```bash
npm run dev
```

# Verify server health
```bash
curl http://localhost:8000/health
```

### Production Environment

# Start production server
```bash
npm run start
```

# Health check
```bash
curl http://localhost:8000/health
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../../LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Check the health endpoint for server status
- Review structured logs for debugging information
- Check the web application documentation for integration details