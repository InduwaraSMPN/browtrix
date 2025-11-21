# Browtrix

A powerful Model Context Protocol (MCP) server for browser automation, providing seamless integration between AI assistants and web browsers through a comprehensive set of tools for capturing, interacting with, and monitoring web pages. This monorepo includes both the MCP server and a modern web interface built with Next.js 15, React 19, and Tailwind CSS.

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

### Modern Web Interface
- **Real-time Communication**: Persistent WebSocket connection to the MCP server
- **Live Status Indicators**: Visual feedback for connection status
- **Dark/Light Theme Support**: Seamless theme switching with system preference detection
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Animated Components**: Smooth transitions and micro-interactions

## Development Stack

### Backend (Python MCP Server)
- **Framework**: FastMCP Model Context Protocol server
- **Web Framework**: FastAPI with automatic API documentation
- **ASGI Server**: Uvicorn for high-performance async operations
- **Validation**: Pydantic data validation with Python type annotations
- **Communication**: Real-time WebSocket connections
- **Logging**: Structured JSON logging with structlog
- **Package Manager**: uv or pip

### Frontend (Next.js Web App)
- **Framework**: Next.js 15 with App Router
- **UI Library**: React 19 with TypeScript
- **Styling**: Tailwind CSS 4.1.10
- **Components**: Radix UI primitives
- **State Management**: React Context API
- **Form Handling**: TanStack React Form
- **Animations**: Motion and tw-animate-css
- **Package Manager**: Bun 1.3.0

### Development Tools
- **Monorepo**: Turbo for efficient build system
- **Code Quality**: Biome for formatting and linting
- **Testing**: pytest for Python, built-in testing for Next.js
- **Type Safety**: TypeScript across frontend, Pydantic for backend

## Quick Start

### Prerequisites
- Python 3.12+ or uv for package management
- Node.js 20+ or Bun 1.3.0+
- Git for version control

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/InduwaraSMPN/browtrix.git
   ```
   ```bash
   cd browtrix
   ```

2. Install Node.js dependencies
   ```bash
   bun install
   ```

3. Install Python dependencies
   ```bash
   cd apps/server
   ```
   ```bash
   uv sync
   ```
   ```bash
   cd ../..
   ```

4. Set environment variables
   ```bash
   cp apps/server/.env.example apps/server/.env
   ```
   ```bash
   cp apps/web/.env.example apps/web/.env
   ```

### Environment Variables

The server uses a comprehensive configuration system based on environment variables.

1. Copy the example configuration:
   ```bash
   cp apps/server/.env.example apps/server/.env
   ```

2. Configure your environment variables in `apps/server/.env`.

See [apps/server/ENVIRONMENT.md](apps/server/ENVIRONMENT.md) for a complete list of available configuration options.

For the web application:
```env
NEXT_PUBLIC_BROWTRIX_MCP_WS_URL=ws://localhost:8000/ws
```

### Development

1. Start all services (server on port 8000, web app on port 3001)
   ```bash
   bun run dev
   ```

2. Start individual services: Web application
   ```bash
   bun run dev:web
   ```

3. Start individual services: MCP server
   ```bash
   bun run dev:server
   ```

### Production

1. Build all applications for production
   ```bash
   bun run build
   ```

2. Start production servers
   ```bash
   bun run start
   ```

## Project Structure

```
browtrix/
├── apps/
│   ├── server/                    # Python MCP server with FastAPI
│   │   ├── src/browtrix_server/   # Server implementation
│   │   │   ├── core/              # Core functionality
│   │   │   │   ├── connection/    # WebSocket connection management
│   │   │   │   ├── tools/         # MCP tool implementations
│   │   │   │   └── types/         # Type definitions
│   │   │   └── tests/             # Test suite
│   │   └── pyproject.toml         # Python dependencies
│   └── web/                       # Next.js web interface
│       ├── src/
│       │   ├── app/               # Next.js App Router
│       │   │   ├── api/           # API routes
│       │   │   ├── docs/          # Documentation pages
│       │   │   └── page.tsx       # Home page
│       │   ├── components/        # Reusable UI components
│       │   │   ├── overlay/       # Background effects
│       │   │   ├── theme/         # Theme management
│       │   │   └── ui/            # Base UI components
│       │   └── lib/               # Utility libraries
│       └── package.json           # Node.js dependencies
├── packages/
│   └── config/                    # Shared configuration
└── package.json                   # Root package configuration
```

## Available Scripts

### Root Level Scripts
- `dev` - Start all development services
- `build` - Build all packages and applications
- `check-types` - Type checking across the monorepo
- `lint` - Lint all code

### Web Application Scripts (`apps/web`)
- `dev` - Start development server on port 3001
- `build` - Build production application
- `start` - Start production server
- `check` - Run Biome code formatting and linting
- `check-types` - TypeScript type checking

### Server Scripts (`apps/server`)
- `dev` - Start Python MCP server on port 8000
- `test` - Run pytest test suite
- `check-types` - Type checking with typer
- `lint` - Code linting with ruff
- `lint-fix` - Auto-fix linting issues
- `format` - Code formatting with ruff

## MCP Integration

The Browtrix ecosystem provides powerful browser automation tools through the Model Context Protocol:

### Available Tools

#### 1. HTML Snapshot (`html_snapshot`)
Captures complete HTML snapshots with advanced rendering options.
- **wait_for** (optional): CSS selector to wait for before capturing
- **full_page** (default: true): Capture full page or viewport only
- **wait_timeout** (default: 10s): Maximum wait time for element
- **quality** (default: 100): Reserved for future screenshot functionality

**Use Cases:**
- Capturing dynamically-loaded content after AJAX requests
- Extracting full page HTML for analysis or archival
- Taking snapshots after specific elements render
- Monitoring page state changes over time

#### 2. Confirmation Alert (`confirmation_alert`)
Displays modal confirmation dialogs requiring user interaction.
- **message** (required): Confirmation message (max 1000 chars)
- **title** (default: "Confirmation"): Dialog title
- **timeout** (default: 60s): Maximum wait time (5-300s)

**Use Cases:**
- Confirming destructive actions before execution
- Requesting user approval in workflow steps
- Human-in-the-loop validation for AI automation
- Gathering explicit consent for data operations

#### 3. Question Popup (`question_popup`)
Collects validated user input through interactive modal forms.
- **question** (required): Input prompt (max 1000 chars)
- **title** (default: "Input Required"): Dialog title
- **input_type** (default: "text"): HTML input type (text, email, password, number)
- **validation** (default: "any"): Validation rule (any, email, number, url, regex)

**Use Cases:**
- Collecting user credentials during authentication
- Gathering configuration parameters (API keys, URLs)
- Requesting data for form auto-filling
- Human-in-the-loop data entry for AI workflows

## API Endpoints

### HTTP Endpoints
- `GET /health` - Health check endpoint
- `GET /stats` - Server statistics and metrics
- `GET /info` - Server information and capabilities
- `GET /mcp/*` - Model Context Protocol endpoints

### WebSocket Endpoint
- `WS /ws` - Real-time browser connection management

## Development Workflow

1. Lint all code
   ```bash
   bun run lint
   ```

2. TypeScript validation across monorepo
   ```bash
   bun run check-types
   ```

3. Start all development services
   ```bash
   bun run dev
   ```

4. Start web app only
   ```bash
   bun run dev:web
   ```

5. Start server only
   ```bash
   bun run dev:server
   ```

6. Build all applications
   ```bash
   bun run build
   ```

## Testing

### Running Tests

1. Run Python server tests
   ```bash
   cd apps/server
   ```
   ```bash
   bun run test
   ```

2. Run with coverage
   ```bash
   bun run test --cov=src/browtrix_server
   ```

### Test Structure
- Unit tests for individual tools and components
- Integration tests for API endpoints
- WebSocket connection testing
- Error handling and edge case validation

## Monitoring and Health

The application includes comprehensive monitoring:

### Server Health
- `/health` - Server health status
- `/stats` - Server statistics and metrics
- WebSocket connection monitoring
- Error boundary handling

### Web Application Health
- `/api/health` - Application health status
- Connection status indicator in UI
- Real-time connection monitoring
- Performance metrics

### Logging
- Structured JSON logging with consistent format
- Request/response timing metrics
- Error tracking with full stack traces
- Connection lifecycle monitoring

## Security Considerations

- Input validation using Pydantic models and React safeguards
- WebSocket connection limits and timeouts
- Sanitized HTML content handling
- Configurable request timeouts
- Content Security Policy headers
- XSS protection through React's built-in safeguards

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style
This project uses Biome for code formatting and linting. Ensure your code passes all checks:

```bash
bun run lint
```
```bash
bun run check-types
```

## Environment Setup

### Development Environment

1. Install dependencies
   ```bash
   bun install
   ```

2. Start development servers
   ```bash
   bun run dev
   ```

3. Verify server connection
   ```bash
   curl http://localhost:8000/health
   ```

4. Verify web application
   ```bash
   curl http://localhost:3001/api/health
   ```

### Production Environment

1. Build production bundles
   ```bash
   bun run build
   ```

2. Start production servers
   ```bash
   bun run start
   ```

3. Health checks
   ```bash
   curl http://localhost:8000/health
   ```
   ```bash
   curl http://localhost:3001/api/health
   ```

## Browser Compatibility

### Web Application
- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

### Performance Features
- **React Compiler**: Optimized component rendering
- **Typed Routes**: Faster route resolution
- **Code Splitting**: Automatic bundle optimization
- **Image Optimization**: Next.js built-in image handling
- **CSS Optimization**: Tailwind CSS purging in production

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Check the [documentation](./docs/)
- Review the MCP server [API documentation](./apps/server)
- Check health endpoints for service status