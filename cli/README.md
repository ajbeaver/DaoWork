# DaoWork CLI

This directory contains a **reference CLI implementation** for interacting with the DaoWork smart contract.

The CLI is **not the product**.  
It is a thin, explicit, human-readable interface over the on-chain primitive.

Its purpose is to:
- Demonstrate correct usage of the contract
- Act as a manual coordination tool
- Serve as a baseline for agents or higher-level systems

Nothing in this CLI understands, interprets, or solves jobs.

---

## What This CLI Does

The CLI performs only four categories of actions:

1. **Create jobs**
   - Reads a canonical `job.json`
   - Hashes it deterministically
   - Stakes ETH and creates a job on-chain
   - Mirrors metadata locally in SQLite

2. **Submit solutions**
   - Reads a `solution.json`
   - Computes a receipt hash from `(job_spec, solution)`
   - Optionally submits that receipt on-chain

3. **Validate submissions**
   - Recomputes a receipt from `(job_spec, solution)`
   - Compares it to a claimed receipt
   - Records validation results locally

4. **Finalize jobs**
   - Calls `finalize(job_id)` on-chain
   - Releases funds according to contract logic

The CLI never:
- Solves jobs
- Interprets job meaning
- Enforces correctness beyond hashing
- Automates decision-making

---

## Files You Will See

```
cli/
├── cli.py                # Main CLI entrypoint
├── job_creation.py       # Canonical job hashing + on-chain creation
├── job_execution.py      # Receipt computation + submit/finalize calls
├── job_template.json     # Empty canonical job spec template
├── job.json              # User-filled job spec (ignored by git)
├── solution_*.json       # Example solutions (ignored by git)
├── daowork.db            # Local SQLite mirror (ignored by git)
└── requirements.txt
```

Only templates and code are committed.
Runtime artifacts are intentionally local.

---

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=YOUR_PRIVATE_KEY
CONTRACT_ADDRESS=DEPLOYED_CONTRACT_ADDRESS
```

Run a local chain (example):

```bash
anvil
```

Deploy the contract using Foundry from the repo root.

---

## Canonical Job Spec

Jobs are defined entirely off-chain.

Start from `job_template.json`, copy to `job.json`, and fill it out.

Important rules:
- All keys must be lowercase
- JSON must be valid
- Any byte change changes the hash
- The contract never sees this data

Example workflow:
```bash
cp job_template.json job.json
```

Edit `job.json` manually.

---

## Common Commands

Create a job:

```bash
python cli.py create --stake-wei 1000000000000000000
```

List known jobs:

```bash
python cli.py list
```

Submit a solution:

```bash
python cli.py submit 0 --solution solution_executor00.json --send
```

Validate a submission:

```bash
python cli.py validate 0 \
  --solution solution_validator00.json \
  --claimed-receipt 0x... \
  --validator-id validator00
```

Finalize a job:

```bash
python cli.py finalize 0
```

---

## Database

The SQLite database is a **local mirror**, not a source of truth.

It stores:
- Job specs
- Solution JSON
- Validation records
- Transaction hashes

The chain is the arbiter.
The database is coordination memory.

You can inspect it manually with:

```bash
sqlite3 daowork.db
```

---

## Mental Model

Think of this CLI as:

> a wrench for tightening cryptographic bolts

It is intentionally manual.
It is intentionally boring.
It is intentionally correct.

Agents, automation, encryption layers, and coordination logic all belong **above** this layer.

---

## Future Use

This CLI can be:
- Wrapped by agents
- Replaced by a GUI
- Used headless
- Used manually forever

The contract does not care.

That is the point.

