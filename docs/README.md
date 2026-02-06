# DaoWork

DaoWork is a **minimal, composable coordination primitive** for decentralized work.
It is not a DAO framework, not a task marketplace, and not an automation platform.

It is a *cryptographic trust anchor* for coordinating work between untrusted entities.

This project exists to answer a simple question:

> How do you request, perform, verify, and finalize work **without trusting any single party**, while keeping the work itself off‑chain?

---

## What DaoWork Is

DaoWork consists of three layers:

1. **An on‑chain contract**
2. **A reference CLI**
3. **An off‑chain data layer (user‑controlled)**

Each layer is deliberately dumb, scoped, and replaceable.

### 1. The Contract (The Primitive)

The contract does exactly four things:

• Accepts a stake and creates a job identifier  
• Accepts a cryptographic receipt for submitted work  
• Tracks finalization state  
• Enforces simple rules around who can do what and when  

The contract **never knows what the job is**.
It never sees the job spec.
It never sees the solution.
It never evaluates correctness.

On‑chain, the only meaningful data is:

• ETH value (stake)  
• job_id (internal counter)  
• bytes32 hashes (receipts)  

Everything else is intentionally excluded.

This maximizes information entropy and minimizes attack surface.

---

### 2. The CLI (A Reference Interface)

The Python CLI is **not the product**.
It is a *demonstration of how to safely interact with the contract*.

The CLI:

• Canonicalizes JSON deterministically  
• Hashes job specs and solutions  
• Submits and verifies receipts  
• Mirrors state locally for humans and agents  

The CLI never solves jobs.
It never interprets job meaning.
It never enforces business logic.

It only performs **mechanical transformations**.

Any agent, service, or UI can replace it.

---

### 3. The Off‑Chain Data Layer (User‑Owned)

All meaningful data lives off‑chain:

• Job specifications  
• Solutions  
• Validation artifacts  

This data can live:

• Locally
• Encrypted
• On IPFS
• In a database
• In cold storage
• Behind access control
• Shared selectively

The chain only stores **opaque commitments**.

Without the off‑chain data, the on‑chain state is useless.

This follows Shannon’s information model:
we maximize secrecy by minimizing public information.

---

## What DaoWork Is Not

DaoWork is not:

• A task solver  
• An automation engine  
• A voting DAO  
• A marketplace  
• A Web3 app UI  
• A trustless oracle  

Those systems can be built *on top* of DaoWork.

DaoWork exists below them.

---

## Why This Matters

Most DAOs today coordinate work using:

• Discord messages  
• Google Docs  
• GitHub issues  
• Manual trust  

The blockchain is often only used for payouts or voting.

DaoWork flips this model.

The blockchain becomes the **coordination spine**:
a neutral, immutable record that enforces order without learning content.

Humans and agents operate at the edge.

---

## Security Model (High Level)

• On‑chain data is content‑free  
• Job meaning is never revealed publicly  
• Hashes act as commitments, not disclosures  
• Off‑chain secrecy is preserved by design  
• Trust is minimized, not eliminated  

If the off‑chain data leaks, the system degrades gracefully.
If the chain is observed, no information is revealed.

---

## Intended Use Cases

• Open‑source maintenance DAOs  
• Agent‑driven infrastructure monitoring  
• Adversarial work coordination  
• Grant verification systems  
• DAO‑internal task routing  
• Trust‑minimized collaboration  

---

## Philosophy

DaoWork is intentionally boring.

It favors:

• Fewer features  
• Smaller surfaces  
• Explicit responsibility boundaries  
• Mechanical determinism  

The goal is not to replace humans.
The goal is to prevent humans from becoming single points of failure.

---

## Status

DaoWork is complete as a **primitive**.

Future work lives *on top* of it, not inside it.

If this contract never changes again, 
