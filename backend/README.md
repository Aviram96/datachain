# Datachain backend

FastAPI service for Datachain. Epic 2 adds SQLAlchemy models and Alembic migrations.

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

## Environment variables

Create `backend/.env` (or export in your shell) based on `backend/.env.example`.

Required for DB-connected workflows:

```bash
DATABASE_URL=postgresql+psycopg://datachain:datachain_dev@localhost:5432/datachain
```

**JWT (Epic 3):** set **`JWT_SECRET_KEY`** to a long random string (for example `openssl rand -hex 32`). The API process exits on startup if it is missing or blank. Optional: **`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`** (default `60`, capped at one week).

**CORS (Epic 3 frontend):** optional **`CORS_ORIGINS`** comma-separated list (default `http://127.0.0.1:3000,http://localhost:3000`) so the Next.js app can call the API from the browser.

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

### Register a user (Epic 3, US-3.1)

With Postgres running and migrations applied:

```bash
curl -s -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"you@example.com\",\"password\":\"your-secure-pass\"}"
```

Expected on success: JSON with `id`, `email`, and `created_at`. Duplicate email returns HTTP **409**.

### Log in and call a protected route (Epic 3, US-3.3)

Set **`JWT_SECRET_KEY`** in your environment (see `backend/.env.example`); the app refuses to start without it.

```bash
curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"you@example.com\",\"password\":\"your-secure-pass\"}"
```

Expected on success: `{"access_token":"...","token_type":"bearer"}`. Wrong email or password returns HTTP **401** with the same error message (no user enumeration).

```bash
curl -s http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <paste_access_token_here>"
```

Expected on success: same shape as register response (`id`, `email`, `created_at`). Missing or invalid token returns HTTP **401**.

## Database migrations (Alembic)

From `backend/` with the venv activated:

```bash
# apply all migrations
alembic upgrade head

# create a new migration after model changes
alembic revision --autogenerate -m "describe change"

# rollback one migration
alembic downgrade -1
```

## Camera online/offline (US-4.6)

List and detail responses include a **`status`** field: `"online"` or `"offline"`. The API probes each camera’s **`stream_url`** on demand (not stored in the database):

- **Rule:** open a short **TCP connection** to the URL’s host and port. Success → **online**; timeout or connection error → **offline**.
- **Default ports** when omitted: `http` → 80, `https` → 443, `rtsp` → 554.
- **Not validated:** HTTP status codes, RTSP handshake, or whether a video stream is playable—only host reachability.
- **Timeout:** `CAMERA_PROBE_TIMEOUT_SECONDS` (default `2`, clamped 0.5–10). List endpoints probe cameras on the current page in parallel (up to 10 workers).

After changing `.env`, restart uvicorn; reload may not pick up new values.

## Simulated CCTV feed (Epic 5, slice 1)

Before chunking lands, you can **loop a local `.mp4` at real-time speed** as if it were a live camera feed. This uses **FFmpeg** on your machine (install separately; not a Python package).

**Prerequisites:** FFmpeg on `PATH` ([download](https://ffmpeg.org/download.html)).

From `backend/` with the venv activated:

```powershell
# Option A: explicit file
python scripts/simulate_cctv_feed.py --source C:\path\to\sample.mp4

# Option B: environment variable (see backend/.env.example)
$env:CCTV_SOURCE_MP4 = "C:\path\to\sample.mp4"
python scripts/simulate_cctv_feed.py
```

The process writes a continuous **MPEG-TS** stream to **stdout** (suitable for piping into the chunking step in the next slice). Press **Ctrl+C** to stop; the script terminates FFmpeg cleanly.

**Note:** Use a short sample clip for testing; the file loops forever until you stop the script.

## Video chunking (Epic 5, slice 2)

Split a local `.mp4` into **1-minute** segments written to **`backend/temp/`** (gitignored). Uses FFmpeg’s **segment muxer** with `-segment_time 60`.

From `backend/` with the venv activated:

```powershell
# One pass: chunk the whole file, then exit (good for short test clips)
python scripts/chunk_cctv_feed.py --source C:\path\to\sample.mp4

# Continuous CCTV-style loop: keeps chunking until Ctrl+C
python scripts/chunk_cctv_feed.py --source C:\path\to\sample.mp4 --loop
```

Output files: `backend/temp/chunk_000.mp4`, `chunk_001.mp4`, … (directory created automatically).

Optional flags: `--temp-dir DIR`, `--duration SECONDS` (default **60**), or env vars `CCTV_TEMP_DIR` / `CCTV_CHUNK_DURATION_SECONDS` (see `backend/.env.example`).

**Tip:** For a 2–3 minute sample without `--loop`, you should see 2–3 chunk files and the process exits on its own.

## Tests

From `backend/` with dev dependencies installed:

```bash
pytest -q
```

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

