# React Pattern Definitions

## Entrypoints Detection
- **Component entrypoints**: `function App()`, `class App extends Component`, `export default` components
- **Route handlers**: `react-router` components, `<Route>`, `useRoutes()`, `Switch` components
- **Event handlers**: `onClick`, `onSubmit`, `onChange` props, event callback functions
- **Effect hooks**: `useEffect()` with API calls, `useLayoutEffect()` patterns
- **Custom hooks**: Functions starting with `use` that contain side effects

## IO Operations Detection
- **API calls**: `fetch()` in `useEffect`, `axios` calls in hooks, `graphql` queries
- **State persistence**: `localStorage` in `useEffect`, `sessionStorage`, `IndexedDB` operations
- **Form submissions**: `onSubmit` handlers with API calls, form data processing
- **WebSocket connections**: `useWebSocket` patterns, `socket.io-client` usage
- **File operations**: File upload handlers, `FileReader` API usage

## Error Detection
- **Error boundaries**: `componentDidCatch`, `getDerivedStateFromError`, error boundary components
- **Try/catch in effects**: Error handling in `useEffect` and custom hooks
- **Error states**: `setError` patterns, error message displays

## Tests Detection
- **React testing**: `render()` from `@testing-library/react` (recommended for new projects), `shallow()` from `enzyme` (legacy; migrate to @testing-library/react for future-proofing and improved compatibility)
- **Assertions**: `toBeInTheDocument()`, `toHaveTextContent()`, `toHaveBeenCalledWith()`
- **Mocking**: `jest.mock()`, `mockResolvedValue()`, API mock patterns
- **User interactions**: Prefer `userEvent` from `@testing-library/user-event` for simulating real user interactions; use `fireEvent` only for legacy code or low-level events. For enzyme users, consider upgrading to @testing-library/react and refactoring tests to use `userEvent` for more accurate interaction simulation.

## Confidence Defaults
- **High confidence**: Explicit API calls in effects, clear state operations
- **Medium confidence**: Generic function calls within components, inferred operations
- **Low confidence**: Props without clear usage, variable assignments in JSX

## JSX/AST Cues
- **Component definitions**: Function and class component patterns
- **JSX elements**: Component usage, prop passing, event binding
- **Hook usage**: `useState`, `useEffect`, `useContext`, `useReducer`, `useCallback`, `useMemo`, `useRef`, custom hooks
- **Context API patterns**: `useContext`, `Provider`/`Consumer` components, context value propagation
- **Import statements**: React imports, library usage, component imports
