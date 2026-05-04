# Datachain frontend

Next.js dashboard (Epic 1 scaffold): **App Router**, **TypeScript**,
**Tailwind CSS**, **ESLint**, **Prettier**.

## Prerequisites

- **Node.js** 20+ or 22+ (LTS recommended) and **npm**

## Install

```bash
cd frontend
npm install
```

## Scripts

| Command                | Purpose                   |
| ---------------------- | ------------------------- |
| `npm run dev`          | Dev server (Turbopack)    |
| `npm run build`        | Production build          |
| `npm run start`        | Run production build      |
| `npm run lint`         | ESLint                    |
| `npm run format`       | Prettier write            |
| `npm run format:check` | Prettier check (CI-style) |

Dev server defaults to
[http://127.0.0.1:3000](http://127.0.0.1:3000).

## Routes (scaffold)

- `/` — Home
- `/project-status` — Example secondary page (kebab-case segment)

## Proof (local)

```bash
npm run lint
npm run format:check
npm run build
```
