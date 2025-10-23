# Pattern Pack — JavaScript / TypeScript (Node + Browser)

## Entry Points
- `index.js`, `main.ts`, or `server.js`.
- CLI tools using `#!/usr/bin/env node`.

## Backend (Node / Express / Nest)
- `express()` app → `app.get|post|put|delete`.
- Middleware: error handlers (`app.use(errorHandler)`), request logging (`morgan`, custom middleware), authentication/authorization (`passport`, `jwt`, custom middleware).
- Explicit routing: `app.use(router)`, controller organization (`controllers/`, `routes/`).
- Controllers and routers; `require('./routes/...')`.
- Dependency: `package.json` scripts + `dependencies`.

## Frontend (Generic)
- Component structure: reusable/composable modules, conventions per framework (e.g., React functional components, Vue single-file components).
- State management: Redux, Zustand, Context API, or framework-specific solutions (Vuex, Pinia, Angular services).
 Centralized API client: single service or `api.js`/`api.ts` with error handling and retries.
 Event handlers (`onClick`, `onSubmit`).
 API calls via `fetch` / `axios`.
 Dependency: `package.json` scripts + `dependencies`.

## Frontend (Generic)
 Component structure: reusable/composable modules (e.g., React functional components with hooks, Vue single-file components (SFCs)), conventions per framework.
 State management: Redux, Zustand, Context API, or framework-specific solutions (Vuex, Pinia, Angular services).
## Tests
- Unit tests: libraries, utils, helpers (e.g., Jest, Mocha, Vitest)
- Integration tests: API routes, service interactions
- E2E tests: user workflows (e.g., Cypress, Playwright)
- File placement: colocated with source, in `test/` or `__tests__/` directories

## Security Smells
- Direct string concatenation in SQL queries.
- `innerHTML` injection without sanitization.
- API keys embedded in source.
