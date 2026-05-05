# AGENTS.md

## Architecture

- No framework — uses Python's `http.server`. Router table in `server.py:27`.
- Handlers in `handlers/` (not `api/` as README claims). Each handler file exports functions called by the router.
- Frontend is static HTML/CSS/JS in `frontend/`, served directly by `server.py`.
- SQLite database auto-creates in `instance/fres.db` on server start.

## Environment

- `.env` is auto-loaded by `server.py:11-18` — no `python-dotenv` needed.
- Required vars: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL`.
- Copy `.env.example` to `.env` and add your API key.

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py  # runs on http://127.0.0.1:5000
```

## Vercel Deployment

- Deploy to Render.com using the Python (Flask) preset.
- Set environment variables in Render dashboard.
- Database is auto-initialized on first deploy.

## Defaults

- Default admin: `admin` / `admin123` — change immediately.
- Password hashing: SHA-256 (see `db.py:17`).

## Notes

- No tests, linting, or typechecking configured.
- `.gitignore` excludes `instance/*.db` and `.env`.
