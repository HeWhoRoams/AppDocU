# Pattern Pack — Python

## Entry Points
- `if __name__ == "__main__":` blocks.
- `manage.py` (Django) or CLI runners (`click`, `typer`, `argparse`).

## Web / Frameworks
- Flask: `@app.route`, `Flask(__name__)`, `app.run`.
- Django: `urlpatterns`, `views.py`, `models.py`, `settings.py`.
- FastAPI: `APIRouter`, `@app.get|post`, `BaseModel`.

## Data Access
- `sqlalchemy`, `pymongo`, `psycopg2`, `sqlite3` usage.

## Configuration
- `os.getenv`, `dotenv`, `pydantic.BaseSettings`.
- `.env`, `config.py`, `settings.py`.

## Tests
- `pytest`, `unittest`, `nose`.
- Test discovery: `test_*.py`, `*_test.py`.

## Security Smells
- Hardcoded credentials.
- `eval()` / `exec()` with user input.
- Missing `escape()` in templating or weak crypto (`md5`).
