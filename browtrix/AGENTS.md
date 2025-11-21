# Agent Guidelines for Browtrix

## Build/Lint/Test Commands

**Python (Server - browtrix/apps/server):**
- Run all tests: `cd browtrix/apps/server && uv run pytest`
- Run single test: `cd browtrix/apps/server && uv run pytest src/browtrix_server/tests/test_<name>.py`
- Run single test function: `cd browtrix/apps/server && uv run pytest src/browtrix_server/tests/test_<name>.py::test_<function>`
- Lint/format: `cd browtrix/apps/server && uv run ruff check --fix . && uv run ruff format .`
- Type check: Use `ruff` for linting (project uses Python 3.12+)

**TypeScript (Web - browtrix/apps/web):**
- Dev server: `cd browtrix/apps/web && bun run dev` (runs on port 3001)
- Build: `cd browtrix/apps/web && bun run build`
- Lint/format: `cd browtrix/apps/web && bun run check`
- Type check: `cd browtrix/apps/web && bun run check-types`

## Code Style Guidelines

**Python:**
- Use `structlog` for structured logging: `logger = structlog.get_logger(__name__)`
- Type hints: Use `from typing import` annotations for all function signatures
- Async: Prefer async/await for I/O operations (FastAPI, WebSocket, database)
- Imports: Standard library → Third-party → Local (use absolute imports from `.core`, `.settings`)
- Error handling: Raise custom exceptions from `.core.errors` (BrowserConnectionError, BrowserTimeoutError, ValidationError, ToolExecutionError)
- Docstrings: Use triple quotes for classes and public methods
- Naming: snake_case for functions/variables, PascalCase for classes
- Models: Use Pydantic `BaseModel` with `Field()` for validation and descriptions

**TypeScript/React:**
- Formatting: Tabs for indentation (per biome.json), double quotes
- Imports: Use `@/` path alias for src imports, organize imports automatically
- React: Use functional components with hooks ("use client" for client components)
- Types: Strict mode enabled, use explicit types (no implicit any)
- Naming: camelCase for functions/variables, PascalCase for components
- Styling: Tailwind CSS with template literals, use `className` prop
- State: Use React hooks (useState, useEffect, useContext) and TanStack Query for server state
