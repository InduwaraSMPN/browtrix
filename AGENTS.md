# Agent Guidelines for Marketrix.ai

## Build/Lint/Test Commands

### Web App (Next.js)
- `cd browtrix/apps/web && bun run dev` - Start development server on port 3001
- `cd browtrix/apps/web && bun run build` - Build production bundle
- `cd browtrix/apps/web && bun run start` - Start production server

### Backend (Python)
- `cd browtrix/apps/server && bun run dev` - Run Python backend with uv
- `cd browtrix/apps/server && uv run python -m src.browtrix_server` - Direct Python execution

### Monorepo (Turbo)
- `cd browtrix && bun run dev` - Run all apps in development
- `cd browtrix && bun run build` - Build all apps
- `cd browtrix && bun run check-types` - Type check all apps
- `cd browtrix && bun run dev:web` - Run only web app
- `cd browtrix && bun run dev:native` - Run only native apps

## Code Style Guidelines

### TypeScript/React
- Use strict TypeScript configuration with `strict: true`
- Follow shadcn/ui component patterns using `class-variance-authority` for variants
- Use `cn()` utility from `@/lib/utils` for className merging (clsx + tailwind-merge)
- Import order: React → libraries → local imports → `@/` aliases
- Use functional components with TypeScript interfaces
- Component naming: PascalCase for components, camelCase for functions
- File naming: kebab-case for files, PascalCase for components

### Styling
- Use Tailwind CSS with shadcn/ui design system
- Component variants defined with `cva()` from class-variance-authority
- Use CSS variables for theming (dark mode support)
- Follow "new-york" style from shadcn/ui configuration

### Python
- Use Python 3.13+ (specified in pyproject.toml)
- Follow FastMCP framework conventions
- Use `uv` for dependency management

### General
- No explicit linting configured - rely on TypeScript strict mode
- No test framework configured - add tests as needed
- Use Bun as package manager
- Turbo for monorepo orchestration
- React Compiler enabled for performance optimization