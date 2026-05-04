# Datachain — Agent & Contributor Guide

This document orients human contributors and automated coding agents to the **Datachain** project: a decentralized, tamper-evident CCTV video management system. Use it together with `ROADMAP.md` for scope and sequencing.

## Operating principles (agent behavior)

- **Correctness over cleverness**: Prefer boring, readable solutions that are easy to maintain.
- **Smallest change that works**: Minimize blast radius; do not refactor adjacent code unless it meaningfully reduces risk for the requested change.
- **Smallest production-grade change**: A “thin slice” is the minimal step that is safe for **production-style** operation and aligned with the target architecture (FastAPI, PostgreSQL, IPFS/Pinata, Polygon, Next.js). Do not choose a lower-quality interim if a production-grade approach fits similar scope.
- **Leverage existing patterns**: Follow established project conventions before introducing new abstractions.
- **Prove it works**: “Seems right” is not done. Validate with tests, build, and lint per **Technology expectations** and **Testing expectations**, or record explicit manual verification steps when automation is not yet in place.
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
- Bake **verification** into the plan (tests, lint, build, testnet checks)—not as an afterthought.
- If new information invalidates the plan: stop, revise the plan, then continue.

### Human-in-the-loop checkpoints (maintainer approval)

For **complex or multi-step** work—anything that would trigger **Plan mode** above, multi-epic slices, or other non-trivial changes—agents must use **phase gates** so the maintainer can confirm shared understanding before the next chunk of implementation.

**At each checkpoint:**

- Summarize what was completed, what you propose next, key assumptions, risks, and how to verify the current state (tests, commands, or manual checks).

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
- Land work in small verifiable increments: implement → test → verify → expand.
- When the stack supports it, keep risky behavior behind feature flags or configuration switches.
- Do not trade away production quality for thinness. If two options are similarly scoped, prefer the one closer to the target architecture and stronger operational behavior (retries, timeouts, clear failure modes for IPFS and Web3).
- If a slice deliberately uses a temporary shortcut, document why, define an explicit follow-up in the same plan, and do not call the work “done” until the quality gap is closed.

### Definition of done

A task is complete when:

- Behavior matches acceptance criteria.
- Tests, lint, and build pass for affected packages—or there is a documented reason they were not run (for example CI not yet enabled) and manual verification is recorded.
- Code follows **Naming conventions** and is readable.
- **Documentation** is updated when warranted (see **Documentation updates** below).
- A verification story exists: what changed and how we know it works.
- **Dependency and migration hygiene** for the slice: Python dependency changes include updated `requirements.txt` or the project’s chosen lockfile strategy and are committed with the change; Node changes in `frontend/` or `contracts/` include updated lockfiles (`package-lock.json`, `pnpm-lock.yaml`, or npm/yarn equivalent—follow whichever the package uses) committed with the change; database model changes include Alembic migrations in the same slice where applicable.

### When blocked

- Ask exactly one targeted question.
- Provide a recommended default.
- State what would change based on a different answer.

### Documentation updates

Update README, `ROADMAP.md` (if epics or milestones materially shift), `.env.example`, or operator-facing notes when setup, environment variables, integration boundaries, or publicly observable API behavior changes. Epic 10 academic artifacts follow course rules and are out of scope unless the task explicitly includes them.

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
6. Follow **Git commits and attribution** for every commit and push.

## Out of scope unless explicitly requested

- Storing full video files on-chain.
- Mainnet deployment without explicit approval and security review.
- Legal admissibility claims beyond "integrity check as implemented."

---

For milestones and full story list, see `**ROADMAP.md`**.