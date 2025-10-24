# Python Pattern Definitions

## Entrypoints Detection
- **Function decorators**: `@app.route()`, `@api.route()`, `@blueprint.route()` - HTTP endpoints
- **Flask routes**: `app.add_url_rule()`, `route()` calls
- **Django views**: Functions with `request` parameter, class-based views
- **CLI commands**: `@click.command()`, `argparse` argument parsers
- **Background jobs**: `@celery.task`, `@periodic_task`, `schedule` decorators

## IO Operations Detection
- **Database reads**: `cursor.execute()`, `SELECT` statements, ORM queries (`.filter()`, `.get()`, `.all()`) — patterns target SQLAlchemy and Django ORM. Other ORMs use different method names:
	- Tortoise ORM: `.get()`, `.filter()`, `.all()` for reads; `.create()`, `.update()`, `.delete()` for writes
	- Peewee: `.select()`, `.get()`, `.where()` for reads; `.create()`, `.save()`, `.delete_instance()` for writes
	- Pony ORM: `.select()`, `.get()`, `.find()` for reads; `.create()`, `.set()`, `.remove()` for writes
- **Database writes**: `cursor.execute()` with `INSERT/UPDATE/DELETE`, ORM saves (`.save()`, `.create()`, `.delete()`) — see above for ORM-specific write methods
- **API calls**: `requests.get()`, `requests.post()`, `urllib.request`, `httpx` calls
- **File reads**: `open()`, `read()`, `readlines()`, `json.load()`, `csv.reader()`
- **File writes**: `open()` with write mode, `write()`, `writelines()`, `json.dump()`, `csv.writer()`
- **Event emission**: `emit()`, `publish()`, `send()` calls to message queues


## Error Detection
- **Exception handling**: `try/except` blocks, custom exception classes
- **Error patterns**: `raise` statements, error logging with `logging.error()`

## Async/await and modern Python
- **Async function definitions**: `async def` for coroutine functions
- **Await expressions**: `await` usage for asynchronous IO and operations
- **Async context managers**: `async with` blocks
- **Async iterators**: `async for` loops
- **Common async libraries/usages**: `asyncio.create_task`, `asyncio.run`, event-loop patterns, `aiohttp`/async clients, async DB drivers
- **AST cues**: `ast.AsyncFunctionDef`, `ast.Await`, `ast.AsyncWith`, `ast.AsyncFor`
- **Confidence**: Explicit `await`/async library calls are HIGH confidence for IO; inferred async patterns (e.g., event-loop setup, async context usage) are MEDIUM confidence.

## Tests Detection
- **Test functions**: `test_*` prefix, `*_test` suffix, `unittest.TestCase` methods
- **Fixtures**: `@pytest.fixture`, `setUp()`, `tearDown()` methods
- **Assertions**: `assert` statements, `self.assertEqual()`, `pytest` assertions

## Confidence Defaults
- **High confidence**: Explicit SQL statements, `requests` calls, `open()` with mode
- **Medium confidence**: Generic method calls, inferred database operations
- **Low confidence**: Comments, variable assignments without clear context

## AST Cues
- **Function definitions**: `ast.FunctionDef` with decorators and parameters
- **Import statements**: `ast.Import`, `ast.ImportFrom` for dependency mapping
- **Call expressions**: `ast.Call` nodes for detecting IO operations
- **Assignments**: `ast.Assign` for variable tracking and configuration
