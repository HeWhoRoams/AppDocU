# Pattern Pack — React / Next.js / Front-End Components

## Entry Points
- `index.tsx` or `index.js` mounting `ReactDOM.render` / `createRoot`.
- Next.js: `pages/_app.tsx`, `app/layout.tsx`, `next.config.js`.

## Component Structure
- Functional components: `function ComponentName()` or `const X = () =>`.
- Class components: `extends React.Component`.
- Hooks: `useState`, `useEffect`, `useContext`, `useReducer`.

## State & Data Flow
- Context providers, Redux slices, Zustand or Recoil stores.
- `props` / `state` mappings; `useEffect` network calls.

## API / Integration
- `fetch`, `axios`, GraphQL queries.
- API endpoints from `/api/*` or environment configs.

## Testing
- React Testing Library: `render`, `screen.getByText`.
- Cypress / Playwright for e2e: `cy.visit`, `cy.get`.

## Security / UX Smells
- Direct `dangerouslySetInnerHTML`.
- Missing error boundaries.
- Unvalidated form inputs.
- Hardcoded secrets in `.env.local`.

## Build / Config
- `vite.config.js`, `webpack.config.js`, `next.config.js`.
- Environment variables: `NEXT_PUBLIC_*`, `REACT_APP_*`.

## Secret Management Guidance:
- `.env.local` is allowed only for local development and must be listed in `.gitignore` (never committed).
- Store production secrets in CI/CD or secret managers (e.g., GitHub Actions/Secrets, AWS Secrets Manager/Parameter Store, HashiCorp Vault).
- Inject secrets via CI/CD or the deployment platform at runtime; never commit production secrets to `.env` files (including `.env.production`). `.env.production` is only appropriate for local build configuration, not for storing real secrets.
- Next.js note: `NEXT_PUBLIC_*` is for build-time/public values; true runtime secrets must be injected from the environment at runtime and never stored in `.env` files.
- Rotate secrets regularly and restrict their scope.
- Never log secrets in application code.
- Use tools like `dotenv-safe` or environment variable validation to fail fast when required variables are missing.