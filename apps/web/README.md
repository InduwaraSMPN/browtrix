# Browtrix Web Application

A modern, responsive web application built with Next.js 15, React 19, and Tailwind CSS that provides a seamless interface for the Browtrix browser automation platform. This is the client-side component of the Browtrix ecosystem, offering real-time WebSocket communication with the MCP server and an elegant user experience.

## Features

### Real-time Communication
- **WebSocket Integration**: Persistent connection to the Browtrix MCP server
- **Live Status Indicators**: Visual feedback for connection status
- **Automatic Reconnection**: Resilient connection management with fallback

### Modern UI/UX
- **Dark/Light Theme Support**: Seamless theme switching with system preference detection
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Animated Components**: Smooth transitions and micro-interactions
- **Dotted Glow Background**: Stunning dynamic background effects

### Browser Automation Interface
- **HTML Snapshot Tool**: Capture page content with advanced options
- **Alert Dialogs**: Interactive confirmation prompts
- **Input Popups**: Collect validated user input
- **Real-time Tool Monitoring**: Track execution status and results

### Development Stack
- **Framework**: Next.js 15 with App Router
- **UI Library**: React 19 with TypeScript
- **Styling**: Tailwind CSS 4.1.10
- **Components**: Radix UI primitives
- **State Management**: React Context API
- **Form Handling**: TanStack React Form
- **Animations**: Motion and tw-animate-css
- **Package Manager**: Bun 1.3.0

## Quick Start

### Prerequisites
- Node.js 20+ or Bun 1.3.0+
- Active Browtrix MCP server instance

### Installation

```bash
# Clone the repository
git clone https://github.com/marketrix-ai/browtrix.git
cd browtrix/apps/web

# Install dependencies
bun install

# Set environment variables
cp .env.example .env.local
```

### Environment Variables

1. Copy the example configuration:
   ```bash
   cp .env.example .env.local
   ```

2. Configure your environment variables in `.env.local`:

```env
# API Server URL (for HTTP requests)
NEXT_PUBLIC_SERVER_URL=http://localhost:8000

# WebSocket URL for MCP server connection
NEXT_PUBLIC_BROWTRIX_MCP_WS_URL=ws://localhost:8000/ws
```

### Development

```bash
# Start development server
bun run dev

# The application will be available at http://localhost:3001
```

### Production

```bash
# Build for production
bun run build

# Start production server
bun run start
```

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── api/               # API routes
│   │   ├── health/        # Health check endpoint
│   │   ├── mcp/          # MCP server integration
│   │   └── tools/        # Tools API
│   ├── docs/             # Documentation pages
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Home page
├── components/           # Reusable UI components
│   ├── overlay/          # Background effects
│   ├── theme/           # Theme management
│   ├── text-effects/    # Typography animations
│   ├── loader/          # Loading components
│   └── ui/              # Base UI components
├── lib/                 # Utility libraries
│   ├── contexts/        # React contexts
│   └── utils/           # Helper functions
└── index.css           # Global styles
```

## Available Scripts

- `dev` - Start development server on port 3001
- `build` - Build production application
- `start` - Start production server
- `check` - Run Biome code formatting and linting
- `check-types` - TypeScript type checking

## Component Architecture

### Browtrix Context
The application uses a React Context (`BrowtrixContext`) to manage:
- WebSocket connection state
- Real-time message handling
- Connection status indicators
- Automatic reconnection logic

### Theme System
- `ThemeProvider` - Manages dark/light theme state
- `ModeToggle` - Theme switching component
- System preference detection with manual override

### UI Components
Based on Radix UI primitives with custom styling:
- Form inputs with validation
- Modal dialogs and alerts
- Dropdown menus
- Loading states
-

## Browser Compatibility

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Performance Features

- **React Compiler**: Optimized component rendering
- **Typed Routes**: Faster route resolution
- **Code Splitting**: Automatic bundle optimization
- **Image Optimization**: Next.js built-in image handling
- **CSS Optimization**: Tailwind CSS purging in production

## Development Workflow

```bash
# Code quality checks
bun run check          # Format and lint code
bun run check-types    # TypeScript validation

# Development
bun run dev            # Start dev server
bun run dev:web        # Shortcut for web app only

# Build validation
bun run build          # Production build
```

## MCP Integration

The web app connects to the Browtrix MCP server through WebSocket, providing:

### Real-time Features
- Live connection status monitoring
- Tool execution results
- Error handling and recovery
- Performance metrics

### Available Tools
1. **HTML Snapshot** (`html_snapshot`)
   - Capture full page or viewport
   - Wait for dynamic content
   - Configurable timeouts

2. **Confirmation Alert** (`confirmation_alert`)
   - Modal confirmation dialogs
   - Customizable messages and timeouts
   - User response tracking

3. **Question Popup** (`question_popup`)
   - Input collection with validation
   - Multiple input types (text, email, password, number)
   - Regex validation support

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style
This project uses Biome for code formatting and linting. Ensure your code passes all checks:

```bash
bun run check
```

## Environment Setup

### Development Environment
```bash
# Install dependencies
bun install

# Start development server
bun run dev

# Verify MCP server connection
curl http://localhost:8000/health
```

### Production Environment
```bash
# Build production bundle
bun run build

# Start production server
bun run start

# Health check
curl http://localhost:3001/api/health
```

## Monitoring and Health

The application includes several health endpoints:

- `/api/health` - Application health status
- Connection status indicator in UI
- WebSocket connection monitoring
- Error boundary handling

## Security Considerations

- WebSocket connections use configurable endpoints
- Input validation on all user interactions
- Content Security Policy headers
- XSS protection through React's built-in safeguards

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Check the [documentation](./docs)
- Review the MCP server [API documentation](../../apps/server)

---