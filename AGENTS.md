# Agent Guide (toys/kindlesyncer)

This folder is a small Python CLI + helper scripts for converting Markdown to PDF and emailing PDFs to a Kindle address.

If a request involves planning/spec work, follow the repo-level OpenSpec instructions in `/Users/rshao/work/code_repos/personal/AGENTS.md`.

## Commands (Build/Lint/Test/Run)

This project is Python-only; there is no build step and no linter configured.

- Setup venv + deps
  - `python3 -m venv venv`
  - `source venv/bin/activate`
  - `python3 -m pip install -r requirements.txt`

- Run (processes markdown files from `MARKDOWN_FOLDER`, default `./src`)
  - `source venv/bin/activate && python3 kindlesyncer.py`

- Tests
  - `source venv/bin/activate && python3 -m pytest -q`

- Single test (pytest)
  - Single file: `python3 -m pytest path/to/test_file.py -q`
  - Single test: `python3 -m pytest path/to/test_file.py::TestClass::test_name -q`
  - Name filter: `python3 -m pytest -k "pattern" -q`

- Optional sanity checks (no lint config in repo)
  - Import/bytecode check: `python3 -m compileall -q .`

## Project Layout

- `kindlesyncer.py`: main CLI (Markdown -> HTML via pandoc -> PDF via weasyprint; optional Mermaid -> PNG via mmdc; then email PDF)
- `style.css`, `style_native.css`: CSS used during HTML/PDF generation
- `src/`: input Markdown drop folder (default)
- `src.bk/`: timestamped backups of processed Markdown
- `tools/`: optional utilities (LLM API, web scraper/search, screenshot utils)

## Helper Scripts

These scripts exist and are commonly used:

- `./md2pdf.sh [-k|--kindle] [-n|--native] <file.md>`
- `./send_pdf.sh <file.pdf>`
- `./send_to_kindle.sh <file.md>`

Notes:

- The shell scripts hardcode `SCRIPT_DIR=/Users/rshao/work/code_repos/kindlesyncer`.
  - In this repo checkout the path is typically `/Users/rshao/work/code_repos/personal/toys/kindlesyncer`.
  - If the scripts fail due to path mismatch, update `SCRIPT_DIR` (or stop using the scripts and run the Python entrypoints directly).

## Common Workflows

- Convert one Markdown to PDF (without emailing)
  - `source venv/bin/activate && python3 -c 'from kindlesyncer import convert_markdown_to_pdf; print(convert_markdown_to_pdf("./src/file.md"))'`

- Send one PDF (without conversion)
  - `source venv/bin/activate && python3 -c 'from kindlesyncer import KindleEmailSender; import sys; s=KindleEmailSender(); sys.exit(0 if s.send_pdf("./some.pdf") else 1)'`

Behavior notes (important for agents):

- `kindlesyncer.py` deletes the generated PDF after a successful send.
- After processing, Markdown files in `src/` are moved into `src.bk/<timestamp>/`.

## Runtime Dependencies

- Python deps: see `requirements.txt`.
- `weasyprint` is imported by `kindlesyncer.py` but may not be present unless installed; install it in the venv if you hit `ImportError`.
- External tools:
  - `pandoc` is required to convert Markdown -> HTML.
  - Mermaid diagrams: `mmdc` (mermaid-cli) is invoked by `kindlesyncer.py` when it finds ```mermaid blocks.
  - PDF rendering uses `weasyprint` and may require OS-level libraries.

## Configuration (.env)

`kindlesyncer.py` reads `.env` via `python-dotenv`.

- Required for sending email:
  - `SMTP_SERVER`
  - `SMTP_PORT`
  - `EMAIL_USER`
  - `EMAIL_PASSWORD`
  - `KINDLE_EMAIL`

SMTP note:

- `kindlesyncer.py` uses `smtplib.SMTP_SSL(...)`.
  - Use an SSL port (commonly `465`) for `SMTP_PORT`.
  - If you need STARTTLS (`587`), the code needs to be updated to use `smtplib.SMTP(...).starttls()`.

- Optional:
  - `MARKDOWN_FOLDER` (default `./src`)
  - `PDF_STYLE` (`kindle` or `native`; defaults to `kindle` in code)

Security:

- Never commit `.env` (it contains credentials).
- Avoid printing secrets to logs; redact tokens/passwords.

## Code Style Guidelines

Match existing conventions in `kindlesyncer.py` and keep diffs minimal.

- Imports
  - Order: stdlib, then third-party, then local.
  - Avoid wildcard imports; remove unused imports.

- Formatting
  - 4-space indentation.
  - Keep string quote style consistent within a file.
  - Prefer small focused functions; avoid huge try/except blocks around large sections when adding new code.

- Types
  - If you touch public functions or add new modules, add type hints.
  - Prefer explicit return types for non-trivial functions.

- Naming
  - Classes: `PascalCase` (e.g. `KindleEmailSender`).
  - Functions/vars: `snake_case`.
  - Constants: `UPPER_SNAKE_CASE`.

- Error handling
  - Don’t swallow exceptions silently.
  - For CLI flows: return a non-zero exit code on failure and log the actionable reason.
  - Prefer catching narrow exceptions when you know the failure mode; include context in the log message.
  - Avoid blanket `except Exception` around large blocks when you can add a small `try` close to the failure point.

- Logging
  - Use `logging` (already configured) rather than `print` for operational messages.
  - Keep stdout relatively clean if a command may be used in pipelines; put debug detail in logs.
  - Never log credentials; consider truncating file paths if they may contain sensitive info.

- Files / artifacts
  - Do not commit: `venv/`, `__pycache__/`, `.env`, `src.bk/`, `*.pdf` (unless intentionally tracked), Playwright browser caches.

- Shell scripts
  - Quote variables (`"$var"`), use `set -euo pipefail` if you make scripts more complex.
  - Prefer using this repo’s path (don’t introduce new hardcoded machine-specific paths).

## Cursor / Copilot Rules

- Cursor rules live in `.cursorrules`.
  - It is used as a Scratchpad + “Lessons learned”.
  - It contains tool commands (LLM/search/screenshot utils) and notes to ignore screenshot/LLM sections when no API key is configured.
  - If you learn a repo-specific gotcha while working here, add it to the `Lessons` section.
- Copilot: no `.github/copilot-instructions.md` in this folder.
