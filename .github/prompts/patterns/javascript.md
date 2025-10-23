# Pattern Pack — JavaScript / TypeScript (Node + Browser)

## Entry Points
- `index.js`, `main.ts`, or `server.js`.
- CLI tools using `#!/usr/bin/env node`.

## Backend (Node / Express / Nest)
- `express()` app → `app.get|post|put|delete`.
- Controllers and routers; `require('./routes/...')`.
- Dependency: `package.json` scripts + `dependencies`.

## Frontend (Generic)
- Event handlers (`onClick`, `onSubmit`).
- API calls via `fetch` / `axios`.

## Data / Config
- `.env`, `process.env`, `config.ts`.
- `dotenv.config()` usage.

## Tests
- Jest, Mocha, Cypress, Playwright → `describe`, `it`, `test`.

## Security Smells
- Direct string concatenation in SQL queries.
- `innerHTML` injection without sanitization.
- API keys embedded in source.
