# Datachain backend

FastAPI service (Epic 1 scaffold). No database layer yet—that lands in Epic 2.

## Prerequisites

- Python **3.11+** (`python --version`)

## Virtual environment

### Windows (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

### macOS / Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Deactivate anytime: `deactivate`

## Run the API

From `backend/` with the venv activated:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- OpenAPI docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

Quick check:

```bash
curl -s http://127.0.0.1:8000/health
```

Expected: `{"status":"ok"}`

## Lint and format

From `backend/` with dev dependencies installed:

```bash
black .
flake8 .
```

CI-style check without writing files:

```bash
black --check .
flake8 .
```

