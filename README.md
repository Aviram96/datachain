# 📹 Datachain
**Cryptographically Secured Hybrid CCTV Video Management System**

Datachain is a Web2/Web3 hybrid monorepo that captures CCTV video streams, chunks them, uploads them to IPFS, and anchors the cryptographic hashes to the Polygon Amoy testnet to guarantee video integrity and prevent tampering.

## 🏗 Architecture
- **Frontend:** Next.js (App Router), TailwindCSS, ethers.js v6
- **Backend:** Python (FastAPI), SQLAlchemy, Web3.py
- **Smart Contracts:** Solidity ^0.8.20, Hardhat (Polygon Amoy Testnet)
- **Database/DevOps:** PostgreSQL 15 (Docker)

## 📂 Monorepo Structure
- `/frontend` - Next.js user interface and Web3 integrations.
- `/backend` - FastAPI server handling video chunking (FFmpeg), IPFS uploads (Pinata), and metadata.
- `/contracts` - Hardhat environment for compiling and deploying the `Datachain.sol` smart contract.

## 🚀 Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.10+)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 1. Start the Database
```bash
docker-compose up -d
```

### 2. Start the Backend
```bash
cd backend
# Activate your virtual environment (Windows: .\venv\Scripts\activate)
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Smart Contracts
```bash
cd contracts
npm install
npx hardhat compile
# Deploy to local node or Amoy testnet
npx hardhat run scripts/deploy.js --network amoy
```

---

### PART 3: Initializing Git & Committing

**CRITICAL WARNING:** When you run `create-next-app`, it automatically initializes a hidden `.git` folder *inside* the `frontend` directory. Because we are building a monorepo, we want the Git repository at the **root** level. If we don't delete the frontend's `.git` folder first, Git will treat the frontend as a weird "submodule" and it will cause you headaches.

Run these exact commands in your **PowerShell terminal from the root folder** (`datachain-monorepo>`):

```powershell
# 1. Delete the nested Next.js Git repository (if it exists)
Remove-Item -Recurse -Force frontend\.git -ErrorAction SilentlyContinue

# 2. Initialize Git at the monorepo root
git init

# 3. Rename the default branch to 'main'
git branch -M main

# 4. Stage all your boilerplate files
git add .

# 5. Create your initial commit
git commit -m "chore: initial datachain monorepo boilerplate"
```