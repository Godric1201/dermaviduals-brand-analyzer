# Development Guide

This document explains how to work on the AI Brand Visibility / GEO Audit Tool locally.

## Project Layout

The Streamlit entrypoint remains in the repository root:

```text
app.py
```

Core application logic lives in the package:

```text
src/geo_audit/
```

Main module groups:

```text
src/geo_audit/
├── analysis_pipeline.py
├── analyzer.py
├── scoring.py
├── prompt_generator.py
├── brand_intelligence.py
├── geo_roadmap.py
├── markdown_report.py
├── report_generator.py
├── output_quality.py
└── ...
```

Tests are located in:

```text
tests/
```

Documentation assets are located in:

```text
docs/
```

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a local `.env` file from `.env.example`.

Windows PowerShell:

```powershell
copy .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Then set:

```env
OPENAI_API_KEY=your_api_key_here
```

Do not commit `.env`.

## Running the App

Start the Streamlit app:

```bash
streamlit run app.py
```

The app should open in the browser and show the audit setup interface.

## Running Tests

Run the full regression test suite:

```bash
python -m pytest tests -q
```

A healthy local run should pass all tests.

## Syntax Check

Run a basic syntax check:

```bash
python -m py_compile app.py
```

For package modules on Windows PowerShell:

```powershell
Get-ChildItem src\geo_audit\*.py | ForEach-Object { python -m py_compile $_.FullName }
```

## Development Notes

When modifying the project:

- Keep `app.py` as the root Streamlit entrypoint.
- Keep core logic inside `src/geo_audit/`.
- Avoid committing `.env`, generated reports, cache folders, or local artifacts.
- Update tests when changing scoring, report generation, or output validation behavior.
- Run the full test suite before pushing changes.
- Keep README screenshots and documentation aligned with user-facing behavior.

## Common Validation Checklist

Before committing:

```bash
python -m pytest tests -q
python -m py_compile app.py
```

Also verify manually:

```bash
streamlit run app.py
```

Expected checks:

- App opens successfully.
- Sidebar setup fields render.
- No import errors occur.
- Tests pass.

## Git Workflow

For larger refactors:

```bash
git checkout -b refactor/example-change
```

After validation:

```bash
git add .
git commit -m "Describe the change"
git push -u origin refactor/example-change
```

For small documentation or cleanup changes, committing directly to `main` is acceptable if the working tree is clean and tests pass.