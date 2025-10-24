# JavaScript Pattern Definitions

## Entrypoints Detection
- **Express routes**: `app.get()`, `app.post()`, `router.get()`, `app.listen()`
- **Node.js HTTP server**: `http.createServer()`, `server.listen()`
- **API endpoints**: Functions with `req, res` parameters, route handlers
- **CLI tools**: `process.argv`, `commander.js` commands, `yargs` parsers
- **Event listeners**: `addEventListener()`, `on()` methods, `socket.on()`
- **Webpack entry points**: `main` property in webpack config, `index.js` files

## IO Operations Detection
- **Database reads**: `db.query()`, `collection.find()`, `SELECT` in template strings, ORM queries
- **Database writes**: `db.execute()`, `collection.insert()`, `UPDATE/INSERT/DELETE` operations
- **API calls**: `fetch()`, `axios.get()`, `XMLHttpRequest`, `$.ajax()`, `http.get()`
- **File reads**: `fs.readFile()`, `fs.readFileSync()`, `readFile()` with promises
- **File writes**: `fs.writeFile()`, `fs.writeFileSync()`, `writeFile()` with promises
- **Event emission**: `emit()`, `dispatchEvent()`, `socket.emit()`, custom event dispatchers
- **Local storage**: `localStorage.getItem()`, `sessionStorage.setItem()`, `IndexedDB`

## Error Detection
- **Exception handling**: `try/catch` blocks, `.catch()` chains, error callbacks
- **Error patterns**: `throw new Error()`, `console.error()`, error event handlers

## Tests Detection
- **Test functions**: `test()`, `it()`, `describe()` blocks, `QUnit.test()`
- **Assertions**: `expect()`, `assert`, `should` patterns, `chai` assertions
- **Fixtures**: `beforeEach()`, `afterEach()`, `beforeAll()`, `afterAll()`
- **Mocking**: `jest.mock()`, `sinon.stub()`, `spy` patterns

## Confidence Defaults
- **High confidence**: Explicit API calls, file operations, database queries with clear methods
- **Medium confidence**: Generic function calls, inferred operations through libraries
- **Low confidence**: Comments, variable assignments, generic method calls without context

## AST Cues
- **Function declarations**: `FunctionDeclaration`, `FunctionExpression`, `ArrowFunctionExpression`
- **Import/require**: `ImportDeclaration`, `CallExpression` with `require`
- **Variable declarations**: `VariableDeclaration` for configuration and dependency tracking
- **Call expressions**: `CallExpression` nodes for detecting IO operations
