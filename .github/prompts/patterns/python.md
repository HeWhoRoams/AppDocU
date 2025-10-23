# Pattern Pack — Python

## Entry Points
- `if __name__ == "__main__":` blocks.
- `manage.py` (Django) or CLI runners (`click`, `typer`, `argparse`).

## Web / Frameworks
- Flask: `@app.route`, `Flask(__name__)`, `app.run`.
- Django: `urlpatterns`, `views.py`, `models.py`, `settings.py`.
- FastAPI: `APIRouter`, `@app.get|post`, `BaseModel`.
- Async/await: `async def`, `await`, `asyncio`, `async with`, `async for`.
- Type hints: `from typing import ...`, function annotations (`def foo(x: int) -> str:`), variable annotations (`x: List[int] = []`).
- Dataclasses: `@dataclass`, `from dataclasses import dataclass`.

## Data Access
- `sqlalchemy`, `pymongo`, `psycopg2`, `sqlite3` usage.

## Configuration
- `os.getenv`, `dotenv`, `pydantic.BaseSettings`.
- `.env`, `config.py`, `settings.py`.

## Tests
- `pytest`, `unittest`, `nose`.
- Test discovery: `test_*.py`, `*_test.py`.

## Security Smells
 - SQL injection: `cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")`, `query = "SELECT ..." % user_input`
 - NoSQL/command injection: `db.find({"name": user_input})` (unsanitized), `os.system(user_input)`
 - Template injection: `render_template_string(user_input)`
- Hardcoded credentials.
- `eval()` / `exec()` with user input.
- Missing `escape()` in templating or weak crypto (`md5`).
