# Datachain — Agent & Contributor Guide

This document orients human contributors and automated coding agents to the **Datachain** project: a decentralized, tamper-evident CCTV video management system. Use it together with `ROADMAP.md` for scope and sequencing.

## Operating principles (agent behavior)

- **Correctness over cleverness**: Prefer boring, readable solutions that are easy to maintain.
- **Smallest change that works**: Minimize blast radius; do not refactor adjacent code unless it meaningfully reduces risk for the requested change.
- **Smallest production-grade change**: A “thin slice” is the minimal step that is safe for **production-style** operation and aligned with the target architecture (FastAPI, PostgreSQL, IPFS/Pinata, Polygon, Next.js). Do not choose a lower-quality interim if a production-grade approach fits similar scope.
- **Leverage existing patterns**: Follow established project conventions before introducing new abstractions.
- **Prove it works**: Humans and **CI** should validate changes with tests, lint, and build per **Technology expectations** and **Testing expectations** when that pipeline exists. Until then, rely on **review**, **compiler/typecheck in the IDE**, and **manual runs** the maintainer chooses.
- **No automated verification in agent sessions (default)**: Automated coding agents must **not** run project verification commands in the shell by default—no **`npm run lint` / `build`**, **`docker run … npm`**, **`pytest`**, **`hardhat test`**, and similar—because agent environments are often incomplete or slow and this becomes a bottleneck. **Trust** the maintainer’s local tooling and the **future CI workflow** (Epic 1) instead. You may **suggest** optional commands for the maintainer to run locally; only run checks yourself if the maintainer **explicitly** asks you to execute them in that session.
- **Prefer manual steps over Docker in agent sessions**: Before using **Docker** only to get `npm`, `node`, or Python tools working in the agent shell, **stop** and **recommend** that the maintainer run the equivalent on their machine (for example `cd frontend && npm install`). Use Docker in-session only when the maintainer requests it or when the task is **about** containerized workflows.
- **Be explicit about uncertainty**: If something cannot be verified here, say so and propose the safest next step.
- **Read before write**: Before editing, locate the authoritative source (existing module, pattern, migration, or test).
- **Control scope creep**: If work surfaces deeper issues, fix only what the task requires; track follow-ups as TODOs or ticket notes.
- **Human-in-the-loop on complex work**: For multi-step or plan-mode tasks, pause at logical checkpoints for maintainer review and **explicit approval** before the next chunk—see **Human-in-the-loop checkpoints** under **Agent workflow** (unless the maintainer waives this for a session).

## Agent workflow

### Plan mode (default for non-trivial work)

Enter structured planning for work that involves:

- Three or more steps or multi-file edits
- Architectural decisions or new patterns
- Production-impacting behavior (authentication, anchoring, integrity verification, storage pipeline)
- Ambiguous requirements

When planning:

- Restate the goal and acceptance criteria.
- Locate existing implementation and patterns under `frontend/`, `backend/`, and `contracts/` as they exist in this monorepo.
- Design the minimal approach with key decisions stated explicitly; name the bar for **security**, **reliability**, **operability**, and readiness for real-world use, consistent with `ROADMAP.md`.
- Note what **humans or CI** will verify (tests, lint, build, testnet checks) once the pipeline exists—not as an afterthought.
- If new information invalidates the plan: stop, revise the plan, then continue.

### Human-in-the-loop checkpoints (maintainer approval)

For **complex or multi-step** work—anything that would trigger **Plan mode** above, multi-epic slices, or other non-trivial changes—agents must use **phase gates** so the maintainer can confirm shared understanding before the next chunk of implementation.

**At each checkpoint:**

- Summarize what was completed, what you propose next, key assumptions, risks, and **what the maintainer may want to run locally** (optional commands)—not long automated agent-side verification runs unless they asked for those runs in-session.

**Gating rule:**

- Do **not** start the next major sub-task until the maintainer gives **explicit approval** (for example: “go ahead”, “approved”, or an equivalent unambiguous signal).
- If the maintainer asks for changes, revise the plan or implementation and **wait for approval again** before proceeding past the next gate.

Treat this rhythm as **part of the workflow**, not optional—unless the maintainer clearly opts out for a specific session (for example: “no checkpoints; run through Epic 1 in one pass”).

This complements **When blocked** (one targeted question during work); checkpoints are for **review between chunks** of larger work.

### Sub-agent exploration protocol

Use read-only sub-agents proactively for broad or ambiguous discovery to reduce context pressure and allow parallel investigation.

**When to use**

- Multi-file architecture analysis across docs and code
- Cross-cutting impact (security, SQL schema contracts, alignment with `ROADMAP.md`)
- Large search or pattern exploration where one pass may miss edge cases

**How to use**

- Launch several parallel read-only explorations, each with a narrow scope.
- Ask each for findings, missing pieces, contradictions, and concrete file targets.
- Synthesize results in the parent thread before making edits.
- Keep implementation in the parent agent unless delegation is clearly safer.

**Guardrails**

- Do not treat sub-agent output as final architecture without checking **Operating principles** and `ROADMAP.md`.
- Prefer smallest-change recommendations.
- Record assumptions and unresolved risks explicitly in the plan.

### Incremental delivery

- Prefer thin vertical slices over big-bang changes.
- Land work in small reviewable increments: implement → maintainer/CI verify when ready → expand.
- When the stack supports it, keep risky behavior behind feature flags or configuration switches.
- Do not trade away production quality for thinness. If two options are similarly scoped, prefer the one closer to the target architecture and stronger operational behavior (retries, timeouts, clear failure modes for IPFS and Web3).
- If a slice deliberately uses a temporary shortcut, document why, define an explicit follow-up in the same plan, and do not call the work “done” until the quality gap is closed.

### Definition of done

A task is complete when:

- Behavior matches acceptance criteria.
- **Humans**: when practical, run lint/tests/build locally or rely on **CI** once enabled. **Agents** do not need to prove green builds in-session unless the maintainer explicitly requested those runs; state what should be checked and where (package README, CI job).
- Code follows **Naming conventions** and is readable.
- **Documentation** is updated when warranted (see **Documentation updates** below).
- A short **completion note** exists: what changed, where it lives, and what to run locally or in CI when ready.
- **Dependency and migration hygiene** for the slice: Python dependency changes include updated `requirements.txt` or the project’s chosen lockfile strategy and are committed with the change; Node changes in `frontend/` or `contracts/` include updated lockfiles (`package-lock.json`, `pnpm-lock.yaml`, or npm/yarn equivalent—follow whichever the package uses) committed with the change; database model changes include Alembic migrations in the same slice where applicable.

### When blocked

- Ask exactly one targeted question.
- Provide a recommended default.
- State what would change based on a different answer.

### Documentation updates

Update README, `ROADMAP.md`, `.env.example`, or operator-facing notes when setup, environment variables, integration boundaries, or publicly observable API behavior changes. Epic 10 academic artifacts follow course rules and are out of scope unless the task explicitly includes them.

**Roadmap consistency**: When a change completes a roadmap task or materially advances an epic (for example Epic 1 checklist items), **update the relevant epic in `ROADMAP.md`**—especially task **Status** / progress fields—so the file matches what the repo can do. If the epic has no status column yet, add or adjust a short **Progress note** instead.

**Task completion (agents)**: After finishing a requested task or checkpoint, **notify the maintainer** in your response: what changed, where it lives, **optional commands** they can run locally (if helpful), and **which `ROADMAP.md` (or other doc) lines were updated** (if any).

**Plain-language technology notes (project book)**: When a change introduces a **new** technology to the codebase (framework, major library, infrastructure component, blockchain tool, or storage integration), extend **AGENTS.md → Plain-language technology guide (project book)** with a **new short subsection** in the same style as existing entries:

1. **What it is** — explain in everyday language, as if to a reader who is not a developer; spell out acronyms on first use.
2. **Why Datachain uses it** — tie to the product goal (integrity, evidence, operability, security, or team workflow).
3. **Where it shows up** — repo paths, services, or docs (for example `backend/`, `docker-compose.yml`).

Do not duplicate long vendor marketing; stay factual and reusable for coursework or a **project book** chapter. If the technology is only planned on the roadmap and not yet in the repo, say so and keep the entry brief or add it only when the code lands.

## Naming conventions (directive)

**Contributors and automated agents must follow these conventions** for new files, symbols, and identifiers. When touching existing code, **match the surrounding style**; when adding new modules, **default to the rules below**.

### Repository and documentation files

- Use `**AGENTS.md`** (this file), `**README.md`**, and `**ROADMAP.md`** at the repo root—uppercase primary entry docs are the project standard.
- Other markdown in `docs/` or similar: `**UPPER_SNAKE_CASE.md**` or `**kebab-case.md**`—pick one pattern per folder and stay consistent.

### Frontend (`frontend/`) — TypeScript, React, Next.js


| Kind                          | Convention                  | Examples                                |
| ----------------------------- | --------------------------- | --------------------------------------- |
| React components (files)      | `PascalCase.tsx`            | `VideoCard.tsx`, `CameraGrid.tsx`       |
| Non-component modules (files) | `camelCase.ts`              | `useAuth.ts`, `apiClient.ts`            |
| App Router special files      | Next.js defaults            | `page.tsx`, `layout.tsx`, `loading.tsx` |
| Route segment folders         | `kebab-case` (URL-readable) | `my-videos/`, `verify-integrity/`       |
| Variables, functions, hooks   | `camelCase`                 | `fetchCameras`, `isVerified`            |
| React components (symbols)    | `PascalCase`                | `function VideoPlayer()`                |
| Constants (module-level)      | `SCREAMING_SNAKE_CASE`      | `MAX_PAGE_SIZE`                         |
| Types and interfaces          | `PascalCase`                | `type VideoRecord`, `interface Camera`  |


### Backend (`backend/`) — Python

Follow **PEP 8** (Black/Flake8 align with this).


| Kind                         | Convention             | Examples                               |
| ---------------------------- | ---------------------- | -------------------------------------- |
| Modules (files)              | `snake_case.py`        | `video_processor.py`, `routes/auth.py` |
| Packages (directories)       | `snake_case`           | `app/`, `services/`                    |
| Functions, variables, params | `snake_case`           | `anchor_cid_on_chain`, `user_id`       |
| Classes                      | `PascalCase`           | `class VideoRecord`                    |
| “Private” helpers            | Leading underscore     | `_hash_password`                       |
| Constants                    | `SCREAMING_SNAKE_CASE` | `CHUNK_DURATION_SECONDS`               |


### Database (SQLAlchemy / PostgreSQL)

- **Table names**: `snake_case`, typically plural — `users`, `cameras`, `video_records`.
- **Column names**: `snake_case` — `created_at`, `ipfs_cid`, `tx_hash`.

### Smart contracts (`contracts/`) — Solidity


| Kind                           | Convention                              | Examples                        |
| ------------------------------ | --------------------------------------- | ------------------------------- |
| Contract files                 | `PascalCase.sol` matching contract name | `Datachain.sol`                 |
| Contracts                      | `PascalCase`                            | `contract Datachain`            |
| Functions, state vars (public) | `camelCase` is typical                  | `function anchorVideoHash(...)` |


### Hardhat / Node scripts

- Scripts and tests: `**camelCase.ts`** or `**kebab-case.ts`**—mirror Hardhat examples in-repo once established; stay consistent within `contracts/`.

### Environment variables

- `**SCREAMING_SNAKE_CASE`** — `DATABASE_URL`, `PINATA_JWT`, `POLYGON_RPC_URL`.

---

## Product summary

- **Problem**: Centralized CCTV storage is vulnerable to silent edits, deletion, and unauthorized access; tampered footage loses evidentiary value.
- **Approach**: Hybrid **Web2 + Web3**: video blobs live on **IPFS** (e.g., via Pinata); **cryptographic CIDs** and metadata are **anchored on-chain** (Solidity on Polygon testnet); **PostgreSQL** caches metadata for fast queries and dashboards.
- **Integrity model**: Any change to a stored segment changes its hash; comparison of **IPFS-retrieved content CID** vs **on-chain recorded CID** flags tampering.

## Architecture (data flow)

1. **Ingest**: Simulated or RTSP feed → FastAPI video processor → FFmpeg chunks (~1 minute per segment).
2. **Persist**: Upload chunk to IPFS → receive **CID** → Web3 transaction stores anchor (e.g., camera ID, timestamp, CID) → persist **CameraID, Timestamp, CID, TxHash** in PostgreSQL.
3. **Consume**: Next.js loads lists/filters from the API (DB); playback streams via **IPFS gateway** using CID; **Verify Integrity** compares chain record to DB/CID using **ethers.js** on the client.

Agents should preserve this separation: **large files off-chain**, **hashes and pointers on-chain**, **indexed metadata in SQL**.

## Expected monorepo layout (target)

Structure may evolve; prefer clear boundaries:

- `frontend/` — Next.js, Tailwind, auth UX, dashboards, video player, verification UI.
- `backend/` — FastAPI, SQLAlchemy models, Alembic migrations, video pipeline, Pinata, Web3.py.
- `contracts/` — Hardhat, Solidity (`Datachain.sol`), deploy scripts, Polygon Amoy.

Root-level **Docker Compose** for PostgreSQL (and optional local services) is part of DevOps setup.

## Plain-language technology guide (project book)

*Readable explanations of what we use and why—suitable for non-specialists and for reuse in a project book or report. Maintainers and agents should extend this section when new technologies land (see **Plain-language technology notes** under **Documentation updates**).*

### Git and GitHub

**What it is:** **Git** is a tool that records every saved version of your project over time, so you can see what changed, compare versions, and go back if something breaks. **GitHub** is a website (and service) that stores a copy of that history online and helps a team share work, review changes, and run automated checks later (for example continuous integration).

**Why Datachain uses it:** The system handles evidence-related data and a hybrid Web2/Web3 stack; we need an **audit trail of code changes**, safe collaboration, and a single place where the official version of the project lives.

**Where it shows up:** The whole repository; remote history on GitHub; branch workflow described implicitly by how you merge work.

### Markdown documentation (`README.md`, `ROADMAP.md`, `AGENTS.md`)

**What it is:** **Markdown** is a simple text format for writing structured documents (headings, lists, tables) that is easy to read as plain text and easy to publish on sites like GitHub.

**Why Datachain uses it:** Everyone—developers, reviewers, and course markers—needs a **single, honest description** of goals (`ROADMAP.md`), how to work on the repo (`AGENTS.md`), and how to run the project locally (`README.md`).

**Where it shows up:** Repository root files; agents keep `ROADMAP.md` status aligned with reality as work progresses.

### Monorepo (one repository, multiple packages)

**What it is:** Instead of many separate codebases, a **monorepo** keeps related parts of one product—here **frontend**, **backend**, and **smart contracts**—in **one Git repository** with clear folders.

**Why Datachain uses it:** The video dashboard, API, and on-chain anchoring are **one product**. One repo reduces version skew (for example API and UI expecting different things), simplifies issue tracking, and matches how small teams ship hybrid Web2/Web3 systems.

**Where it shows up:** Folders `frontend/`, `backend/`, `contracts/` at the repo root.

### Docker and Docker Compose

**What it is:** **Docker** packages an application and its dependencies so it runs the same way on different computers. **Docker Compose** is a small **declaration file** (our `docker-compose.yml`) that says “start these services with these settings”—for example one command brings up a database.

**Why Datachain uses it:** PostgreSQL is required for metadata and future user/camera/video tables. Compose gives every developer the **same database** locally without manual installation steps, which cuts “works on my machine” problems.

**Where it shows up:** `docker-compose.yml` at the repo root; documented in `README.md`.

### PostgreSQL

**What it is:** **PostgreSQL** is a **relational database**: data is stored in tables with relationships (for example “this camera belongs to this user”). It is widely used when you need **reliable, queryable storage** with strong consistency.

**Why Datachain uses it:** Video **files** stay off-chain (IPFS), but the system still needs fast lists, filters, and joins—for users, cameras, CIDs, and transaction hashes. PostgreSQL is the **Web2 index** that makes the product usable day to day; the blockchain provides tamper-evidence, not spreadsheet-speed browsing.

**Where it shows up:** Defined for local dev via Docker Compose; future application schema will live in `backend/` (Epic 2 onward).

### Python

**What it is:** **Python** is a programming language known for clear syntax and a large ecosystem for **web services**, scripting, and integration with multimedia tools.

**Why Datachain uses it:** The **ingest and API layer** (FastAPI), future **FFmpeg** chunking, **IPFS** uploads, and **Web3** calls fit naturally in Python for a single backend service.

**Where it shows up:** `backend/` application code and tooling configuration.

### Virtual environments (`venv`)

**What it is:** A **virtual environment** is an **isolated folder** of Python packages for this project only, so different projects on the same laptop never fight over library versions.

**Why Datachain uses it:** Reproducible installs (“everyone runs the same FastAPI version”) and fewer mysterious errors when coursework deadlines approach.

**Where it shows up:** Documented in `backend/README.md` (create `backend/.venv`, activate, then install requirements).

### pip, `requirements.txt`, and `requirements-dev.txt`

**What it is:** **pip** is Python’s standard **package installer**. **`requirements.txt`** lists the libraries the **running app** needs; **`requirements-dev.txt`** adds **developer tools** (here: code formatters and linters) on top of the same base list.

**Why Datachain uses it:** Simple, transparent dependency listing that fits coursework and small teams; easy to review in Git diffs.

**Where it shows up:** `backend/requirements.txt`, `backend/requirements-dev.txt`.

### FastAPI

**What it is:** **FastAPI** is a Python framework for building **HTTP APIs** (URLs that return **JSON** for programs and browsers to consume). It emphasizes clear structure and automatic **interactive API docs** in the browser during development.

**Why Datachain uses it:** We need a **production-style API** for auth, cameras, video metadata, and pipeline control; FastAPI matches the stack described in the roadmap and pairs well with **async** operations for I/O-bound work (uploads, RPC calls) later.

**Where it shows up:** `backend/app/main.py` defines the app; more routes will be added in later epics.

### Uvicorn

**What it is:** **Uvicorn** is an **application server** that listens for network requests and runs the FastAPI application. Think of FastAPI as the **recipe** and Uvicorn as the **kitchen** that serves requests.

**Why Datachain uses it:** Standard, lightweight way to run FastAPI locally and in deployment; supports modern concurrent request handling.

**Where it shows up:** Started via the command in `backend/README.md` (`uvicorn app.main:app …`).

### Black

**What it is:** **Black** is an automatic **code formatter** for Python: it rewrites layout (indentation, line breaks) so all contributors’ code looks the same.

**Why Datachain uses it:** Saves debate about style and makes reviews focus on **behavior and security**, not spacing.

**Where it shows up:** Configured in `backend/pyproject.toml`; run from `backend/` per `backend/README.md`.

### Flake8

**What it is:** **Flake8** is a **linter**: it analyzes Python source for many common mistakes and style problems **without** running the program.

**Why Datachain uses it:** Catches issues early (unused imports, undefined names) in a project that will grow in surface area (auth, uploads, chain interactions).

**Where it shows up:** `backend/.flake8` and `backend/README.md`.

### Cursor project rules (`.cursor/rules`)

**What it is:** **Cursor** is an AI-assisted code editor. **Project rules** are short instructions stored in the repo so the assistant follows this project’s **AGENTS.md** habits (roadmap updates, Git policy, attribution).

**Why Datachain uses it:** Keeps automated help aligned with **your** standards—not generic advice—especially for a graded or team project.

**Where it shows up:** `.cursor/rules/agents.mdc`; optional to cite in a project book as “team tooling,” not part of the runtime architecture.

### Next.js

**What it is:** **Next.js** is a **React**-based framework for building **web applications**. It handles **routing** (URLs and pages), **server and client components**, and **production builds** so you get a fast dashboard without wiring everything from scratch.

**Why Datachain uses it:** The product needs a **dashboard** (cameras, videos, verification UI). Next.js matches the roadmap and pairs well with **TypeScript** and **Tailwind** for a maintainable frontend.

**Where it shows up:** `frontend/` (App Router under `frontend/app/`).

### TypeScript

**What it is:** **TypeScript** is **JavaScript** with **static types**: the editor and compiler catch many mistakes (wrong property names, missing fields) before runtime.

**Why Datachain uses it:** As the UI grows, types reduce bugs in API shapes, props, and on-chain verification glue (**ethers.js** later).

**Where it shows up:** `frontend/**/*.tsx`, `frontend/tsconfig.json`.

### Tailwind CSS

**What it is:** **Tailwind CSS** is a **utility-first** styling system: you compose small classes (for example spacing, colors) in markup instead of writing large custom CSS files for every screen.

**Why Datachain uses it:** Fast, consistent UI for dashboards and forms; fits the **Next.js** stack in the roadmap.

**Where it shows up:** `frontend/app/globals.css`, `frontend/tailwind.config.ts`, class names in components.

### ESLint

**What it is:** **ESLint** checks **JavaScript/TypeScript** source for common mistakes and style rules (for example unused variables, risky patterns).

**Why Datachain uses it:** Keeps the React/Next codebase consistent and safer as features accumulate.

**Where it shows up:** `frontend/eslint.config.mjs`; run via `npm run lint` in `frontend/` (see `frontend/README.md`).

### Prettier

**What it is:** **Prettier** is an **opinionated formatter**: it rewrites layout (line breaks, quotes) so formatting is consistent across the team.

**Why Datachain uses it:** Less time debating style; diffs stay focused on behavior.

**Where it shows up:** `frontend/.prettierrc`, `npm run format` / `format:check` in `frontend/README.md`.

### Technologies on the roadmap but not fully in the repo yet

The product vision also relies on **Hardhat** and **Solidity** (smart contracts), **IPFS/Pinata** (video storage), **Polygon** (testnet anchoring), **ethers.js** (browser verification), **SQLAlchemy/Alembic** (database layer in code), and **FFmpeg** (video chunking). These will receive plain-language entries in this section **when they are implemented** in the repository, per **Plain-language technology notes** above.

## Technology expectations


| Area     | Stack                                                                  |
| -------- | ---------------------------------------------------------------------- |
| Frontend | Next.js, Tailwind CSS, ESLint, Prettier, ethers.js (verification)      |
| Backend  | Python 3.x, FastAPI, SQLAlchemy, Alembic, bcrypt, JWT, Web3.py, FFmpeg |
| Chain    | Hardhat, Solidity, Polygon Amoy testnet                                |
| Storage  | IPFS via Pinata SDK                                                    |
| Database | PostgreSQL                                                             |


## Code quality rules

- **Frontend**: ESLint + Prettier; consistent component and route structure.
- **Backend**: Black + Flake8; type hints where helpful; avoid blocking calls in async handlers without care.
- **CI**: GitHub Actions should run lint and tests on change (see Epic 1).

## Git commits and attribution (directive)

**Contributors and automated agents must keep Git history professional and human-attributed.**

- **Agents — no proactive Git operations**: Do **not** run `git add`, `git commit`, or `git push` unless the maintainer **explicitly** asks in that message (for example “commit and push”, “stage the listed files and commit”, or an equivalent clear instruction). Finishing implementation is **not** permission to commit. Wait for explicit Git instructions after the maintainer has reviewed.

- Do **not** add `Co-authored-by:` lines (or any trailer) that credit **Cursor**, **Cursor Agent**, or similar tooling as a commit co-author. Attribution belongs to the repository author unless they explicitly ask otherwise.
- Do **not** put marketing or tool branding in commits—avoid phrases such as **Made with Cursor**, **Generated with Cursor**, **Co-authored-by: Cursor**, or similar in the **subject** or **body**.
- Write commit messages like normal engineering commits: clear subject, optional body explaining *what* and *why*.
- Use the repository’s normal Git author identity (the configured user name and email). Do not override `--author` to a tool or bot identity unless the maintainer requests it.

If your editor can append co-author trailers to commits, disable that in the editor’s settings (for example, turn off **Git attribution** in Cursor) so commits stay under the human author only—no repo scripts or Git plumbing workarounds are required.

## Security and secrets

- **Never** commit private keys, Pinata JWTs, RPC URLs with embedded secrets, or production database URLs.
- Use environment variables and documented `.env.example` files per package.
- Passwords: **bcrypt** (or equivalent) before persistence; no plaintext passwords in logs.
- JWT: sensible expiry; frontend handles expiration with logout or refresh policy as specified in user stories.

## Domain entities (mental model)

- **User**: owns cameras and sessions; authenticated via JWT.
- **Camera**: belongs to a user; has display fields (name, IP/URL, location) and drives pipeline identity.
- **VideoRecord**: ties a **time window** to **CID**, **tx hash**, and camera; supports verification and Drive-like browsing.

## Feature boundaries

- **Camera CRUD** (Epic 4): REST API + UI grid, pagination, edit/delete, online/offline indicator (define probe semantics in implementation).
- **Pipeline** (Epic 5–6): chunking, temp storage, cleanup worker, IPFS upload with **retries**, chain anchor with **graceful Web3 errors**, then DB write.
- **Verification** (Epic 8): user-triggered; client reads contract with ethers.js; compare to API-provided CID; show verified vs tampered; link **TxHash** to Polygonscan.

## Testing expectations

- **Contracts**: Chai/Mocha (Hardhat) for storage semantics.
- **API**: PyTest for auth and camera CRUD.
- **Integration**: Script or test covering **IPFS upload → chain tx → DB row** (Epic 9).

Agents should add or update tests when changing behavior in those areas.

## Academic deliverables (Epic 10)

Documentation chapters and UML artifacts are project-book outputs. Code changes may reference diagrams in-repo if the team adds them; agents should not replace formal academic submission processes—coordinate with course requirements.

## Agent quick reference

1. Align work with **`ROADMAP.md`** and this file (**Operating principles**, **Agent workflow**).
2. Apply **Naming conventions** for new code; match surrounding patterns when editing existing files.
3. Prefer incremental, verifiable slices (**Incremental delivery**): schema with migrations, API changes with tests when present, env vars documented.
4. For complex work, use **Human-in-the-loop checkpoints**: pause for maintainer approval between major sub-tasks unless they waive it for the session.
5. For Web3/IPFS, fail clearly in logs, return safe errors to clients, and document configuration.
6. Follow **Git commits and attribution**: **never** commit or push unless the maintainer explicitly asks in that turn.
7. **No default automated verification**: do not run lint/test/build/npm/docker verification chains unless the maintainer explicitly asks; suggest optional local commands instead (see **No automated verification in agent sessions**).
8. **Keep `ROADMAP.md` honest**: when work completes roadmap tasks or advances an epic, update that epic’s status in `ROADMAP.md`; when you finish a maintainer-requested task, say so explicitly and list doc updates (see **Documentation updates**).
9. **Explain new tech for the project book**: when you introduce a new technology, add a matching subsection under **Plain-language technology guide (project book)** (see **Plain-language technology notes**).

## Out of scope unless explicitly requested

- Storing full video files on-chain.
- Mainnet deployment without explicit approval and security review.
- Legal admissibility claims beyond "integrity check as implemented."

---

For milestones and full story list, see **`ROADMAP.md`**.