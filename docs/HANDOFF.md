# Datachain — agent handoff

## Easiest: copy the whole prompt file

1. Open **`HANDOFF_PROMPT.txt`** in this folder (`docs/HANDOFF_PROMPT.txt`).
2. **Select all** (Ctrl+A) → **Copy** (Ctrl+C).
3. Paste into a **new Cursor chat** and add your specific instruction (e.g. “Implement Hardhat first”).

That `.txt` file contains **only** the handoff—no extra prose—so nothing else gets pasted by mistake.

---

## Or copy from between the markers below

Select **from** the line `<<< BEGIN HANDOFF PROMPT >>>` **through** the line `<<< END HANDOFF PROMPT >>>` (you may exclude those two marker lines if you prefer). Paste into a new chat.

<<< BEGIN HANDOFF PROMPT >>>

You are continuing work on **Datachain**: a decentralized, tamper-evident CCTV system — video on **IPFS**, anchors on **Polygon (testnet)**, metadata in **PostgreSQL**, **FastAPI** backend, **Next.js** frontend. **Do not store full video on-chain.**

**Workspace:** local clone of the **DataChain** monorepo (`frontend/`, `backend/`, `contracts/`, root `docker-compose.yml`).

**Active branch:** `feature/epic-1-2-foundation` (confirm with `git branch`).

### Mandatory reading before editing

1. **`AGENTS.md`** (repo root) — **Operating principles**, **Agent workflow**, **Documentation updates**, **Git commits and attribution**; plain-language tech in **`docs/PLAIN_LANGUAGE_TECHNOLOGY.md`**.
2. **`ROADMAP.md`** — Epic 1 table and **Status** column; keep it aligned with the repo when you finish tasks.

### Non-negotiable agent behavior

- **Do not** run default **automated verification** in the agent shell (long `npm run lint/build`, `docker run … npm`, `pytest`, etc.) **unless the maintainer explicitly asks** in that message. **Suggest** optional local commands; trust **IDE/compiler** and future **CI**.
- **Before using Docker** only to get Node/npm/Python in the agent shell, **prefer recommending manual steps** on the maintainer’s machine unless the task is container-specific or they asked for Docker.
- **Never** `git add` / `commit` / `push` **unless the maintainer explicitly requests** Git operations in that turn.
- **Human-in-the-loop:** for non-trivial / multi-step work, use checkpoints when the maintainer expects them.
- **Git attribution:** human author only; no Cursor co-author lines or tool marketing in commits.
- When you introduce **new** stack pieces, extend **`docs/PLAIN_LANGUAGE_TECHNOLOGY.md`** per **Plain-language technology notes** in **`AGENTS.md`**.
- After completing work: **notify** what changed, optional local commands, and **which docs** (especially **`ROADMAP.md`**) you updated.

### What’s already done (Epic 1 partial)

| Area        | State                                                                 |
| ----------- | --------------------------------------------------------------------- |
| **Postgres** | Root `docker-compose.yml`; root `README.md`                          |
| **Backend**  | `backend/` FastAPI `GET /health`, Black/Flake8, `backend/README.md`  |
| **Frontend** | `frontend/` Next.js 15, Tailwind, ESLint/Prettier, `/` and `/project-status`, `frontend/README.md`, `package-lock.json` |
| **Monorepo** | `contracts/` still needs **Hardhat** scaffold                         |
| **CI**       | **GitHub Actions** not added yet                                      |

**Milestone 1 (roadmap):** Epics **1 + 2**. Epic 1 is **not** closed until **Hardhat** + **CI** land (see `ROADMAP.md`).

### Next tasks (recommended order)

1. **Epic 1 — Hardhat:** scaffold `contracts/` (Hardhat + TypeScript, config, `npx hardhat compile` when Node/npm available). Update **`ROADMAP.md`**, **`README.md`** as needed; add plain-language entries in **`AGENTS.md`** for new tech.
2. **Epic 1 — CI:** `.github/workflows/` — frontend lint (and format check if appropriate), backend `black --check` + `flake8`, contracts compile/tests if present — minimal slice per `ROADMAP.md`.

(Maintainer may reverse order.)

### Maintainer environment (Windows)

- If PowerShell blocks `npm.ps1` (execution policy), use **`npm.cmd`**, **cmd.exe**, or adjust execution policy — see maintainer preference.
- **Node.js LTS** on PATH is required for local `npm`/`npx`.

### Your task

Complete the next **Epic 1** slice the maintainer specifies (**Hardhat** and/or **GitHub Actions**), following **`AGENTS.md`** and **`ROADMAP.md`**. Do **not** commit or push unless the maintainer explicitly asks.

<<< END HANDOFF PROMPT >>>
