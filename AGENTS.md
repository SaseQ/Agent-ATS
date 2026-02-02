# Repository Guidelines

## Project Structure & Module Organization
- `app.py` is the main Streamlit application with UI, API calls, and analysis logic.
- `requirements.txt` lists Python dependencies.
- `Dockerfile` builds a runnable container for local/demo use.
- `ai-docs/` holds internal reference notes (see `ai-docs/base.md`).
- `README.md` documents product goals, setup, and demo flow.

## Build, Test, and Development Commands
- `python -m venv .venv` and `source .venv/bin/activate` create/activate a virtualenv.
- `pip install -r requirements.txt` installs dependencies.
- `streamlit run app.py` starts the local app at `http://localhost:8501`.
- `docker build -t agent-ats .` builds a container image.
- `docker run --rm -p 8501:8501 --env-file .env agent-ats` runs the container.

## Coding Style & Naming Conventions
- Use 4-space indentation and follow PEP 8 for Python.
- Keep helper functions near the top of `app.py`; keep UI layout below setup.
- Naming: `snake_case` for functions/variables, `UPPER_SNAKE_CASE` for constants.
- Prefer small, pure helpers (see `trim_text`, `top_keywords`) and add type hints for new helpers.

## Testing Guidelines
- There is no automated test suite yet.
- Manual smoke checks: upload PDF/TXT, paste URL, and verify fallback when no API key is set.
- If adding tests, use `pytest` in a new `tests/` directory with `test_*.py` files.

## Commit & Pull Request Guidelines
- Commit messages are short and imperative (e.g., "Add README.md").
- PRs should include: a concise summary, steps to verify, and screenshots/GIFs for UI changes.
- Note any config or environment variable changes in the PR description.

## Configuration & Secrets
- `.env` should define `GEMINI_API_KEY` and optional `GEMINI_MODEL`.
- Do not commit real API keys; keep secrets local and update `README.md` if config changes.
