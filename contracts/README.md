# Datachain contracts (Hardhat 3)

Solidity sources and Hardhat tooling for on-chain anchoring (`ROADMAP.md`).

## Stack

- **Hardhat 3** with **`@nomicfoundation/hardhat-toolbox-viem`** (Viem + **Node.js `node:test`** for TypeScript tests).
- **`"type": "module"`** in `package.json` — Hardhat 3 expects an **ESM** Node project.

## Prerequisites

- **Node.js 22+** (Hardhat 3 baseline).

## Commands

From this directory:

```bash
npm install
npm run compile
npm test
```

Equivalent: `npx hardhat compile`, `npx hardhat test`.

## Dependency audits

After installing or bumping packages, run:

```bash
npm audit fix
```

Avoid **`npm audit fix --force`** unless you accept breaking upgrades across the toolchain. Review `npm audit` output periodically.

## Layout

| Path | Purpose |
| ---- | ------- |
| `contracts/` | `.sol` sources (Hardhat default inner folder) |
| `test/` | TypeScript tests (`node:test` + Viem) |
| `hardhat.config.ts` | Compiler and plugin config |
