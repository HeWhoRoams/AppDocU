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
