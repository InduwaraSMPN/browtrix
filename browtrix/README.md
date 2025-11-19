# Browtrix

A full-stack monorepo for the Marketrix.ai project, combining a Next.js frontend and Python backend.

## 🏗️ Tech Stack

### Frontend
- **Next.js 16** - React framework with App Router
- **React 19** - Latest React with compiler optimizations
- **TypeScript** - Type-safe development
- **Tailwind CSS v4** - Modern utility-first CSS
- **shadcn/ui** - Beautiful, accessible UI components
- **TanStack Query** - Powerful data fetching and state management
- **TanStack Form** - Type-safe form handling
- **Zod** - Schema validation

### Backend
- **Python** - Backend runtime
- **uv** - Fast Python package manager
- **FastAPI** (or your framework) - Modern Python web framework

### Build System
- **Turborepo** - High-performance monorepo build system
- **Bun** - Fast JavaScript runtime and package manager

## 📁 Project Structure

```
browtrix/
├── apps/
│   ├── web/              # Next.js frontend application
│   │   ├── src/
│   │   │   ├── app/      # Next.js App Router pages
│   │   │   ├── components/ # React components
│   │   │   └── lib/      # Utility functions
│   │   ├── package.json
│   │   └── components.json # shadcn/ui configuration
│   │
│   └── server/           # Python backend application
│       ├── main.py       # Backend entry point
│       ├── pyproject.toml # Python dependencies
│       ├── uv.lock       # Locked dependencies
│       └── package.json  # For Turborepo integration
│
├── packages/             # Shared packages
│   └── config/           # Shared configuration
│
├── package.json          # Root package.json
├── turbo.json            # Turborepo configuration
└── bun.lock              # Locked JS dependencies
```

## 🚀 Getting Started

### Prerequisites

- **Bun** v1.3.0 or higher ([Install Bun](https://bun.sh))
- **Python** 3.x
- **uv** ([Install uv](https://github.com/astral-sh/uv))

### Installation

1. **Clone the repository:**
   ```bash
   cd /home/pasindui/Desktop/marketrix.ai/browtrix
   ```

2. **Install dependencies:**
   ```bash
   bun install
   ```

3. **Set up environment variables:**
   ```bash
   cp apps/web/.env.example apps/web/.env
   # Edit apps/web/.env with your configuration
   ```

### Development

**Start all services (frontend + backend):**
```bash
bun run dev
```

This will start:
- 🌐 **Frontend**: http://localhost:3001
- 🐍 **Backend**: Running via `uv run main.py`

**Start only the frontend:**
```bash
bun run dev:web
```

**Start only the backend:**
```bash
turbo -F server dev
```

### Building for Production

```bash
bun run build
```

## 📜 Available Scripts

| Command | Description |
|---------|-------------|
| `bun run dev` | Start all applications in development mode |
| `bun run dev:web` | Start only the web application |
| `bun run build` | Build all applications for production |
| `bun run check-types` | Type-check all TypeScript code |

## 🎨 Adding UI Components

This project uses **shadcn/ui**. To add new components:

```bash
cd apps/web
bunx --bun shadcn@latest add button
bunx --bun shadcn@latest add card
bunx --bun shadcn@latest add dialog
```

## 🔧 Troubleshooting

### Port 3001 already in use

If you see `EADDRINUSE: address already in use :::3001`:

1. **Find the process:**
   ```bash
   lsof -ti:3001
   ```

2. **Kill the process:**
   ```bash
   kill -9 $(lsof -ti:3001)
   ```

3. **Or use Ctrl+C** to stop the dev server gracefully

### Turborepo cache issues

Clear the Turborepo cache:
```bash
turbo clean
```

## 📝 Environment Variables

### Frontend (`apps/web/.env`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run type checking: `bun run check-types`
4. Submit a pull request

## 📄 License

[Your License Here]
