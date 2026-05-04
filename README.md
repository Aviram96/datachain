# Datachain

Decentralized, tamper-evident CCTV video management: video on IPFS, CIDs and metadata anchored on Polygon (testnet), PostgreSQL for queryable metadata, FastAPI for ingest/API, Next.js for the dashboard (including on-chain verification with ethers.js).

See `AGENTS.md` for contributor conventions and `ROADMAP.md` for epics.

## Repository layout (target monorepo)


| Path                 | Role                                                      |
| -------------------- | --------------------------------------------------------- |
| `frontend/`          | Next.js app (Epic 1 — scaffold in next checkpoint)        |
| `backend/`           | FastAPI app — see `backend/README.md`                     |
| `contracts/`         | Hardhat / Solidity (Epic 1 — scaffold in next checkpoint) |
| `docker-compose.yml` | Local PostgreSQL                                          |


## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose) for PostgreSQL
- **Node.js** LTS (for `frontend/` and `contracts/` — documented fully once those packages exist)
- **Python 3.11+** (for `backend/` — see `backend/README.md`)

## Local development — PostgreSQL (Epic 1)

Start the database:

```bash
docker compose up -d
```

Check health:

```bash
docker compose ps
```

Default connection (development only; change for real deployments):

- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `datachain`
- **User**: `datachain`
- **Password**: `datachain_dev`

Example URL for tools and future `DATABASE_URL`:

`postgresql://datachain:datachain_dev@localhost:5432/datachain`

Stop without removing data:

```bash
docker compose down
```

Remove the volume (wipes local DB data):

```bash
docker compose down -v
```

## Proof commands (Epic 1 — expanded per package)

After the remaining Epic 1 checkpoints land, you should be able to verify:


| Step        | Command / action                                                                                                     |
| ----------- | -------------------------------------------------------------------------------------------------------------------- |
| Database    | `docker compose up -d` then `docker compose ps`                                                                      |
| Backend API | From `backend/`: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` then `curl http://127.0.0.1:8000/health` |
| Frontend    | From `frontend/`: `npm run dev` (or project equivalent)                                                              |
| Contracts   | From `contracts/`: `npx hardhat compile`                                                                             |
| CI          | Push / open PR; GitHub Actions runs lint and tests                                                                   |


**Current checkpoint**: Postgres, root layout, and **backend** FastAPI scaffold. Frontend, contracts, and CI are added in subsequent Epic 1 steps.

## License

See `LICENSE`.