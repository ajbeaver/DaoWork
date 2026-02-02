# DAO Job State Machine

This document defines a minimal, auditable, and buildable state machine for a DAO-based job execution system.
It is designed to be referenced during Solidity implementation and extended without changing core assumptions.

---

## Core Assumptions

- The contract never interprets job semantics
- The contract enforces authority, time, stake, and payment only
- All meaning and execution happens off-chain
- Adversarial behavior is assumed at all times

If any of these assumptions break, the design is invalid.

---

## Job Identity

Each job is uniquely identified by:

```
jobId = hash(spec || parameters || nonce)
```

- `spec` is never stored on-chain
- The contract only ever sees `jobId`
- Changing the spec creates a new job
- Jobs are immutable once posted

---

## Job States

Conceptual states:

1. NONEXISTENT (implicit)
2. POSTED
3. CLAIMED
4. FINALIZED
5. EXPIRED

Stored states:

- POSTED
- CLAIMED
- FINALIZED
- EXPIRED

---

## Job Data Model (On-Chain)

For each `jobId`:

- poster: address
- reward: uint256 (escrowed)
- stakeRequired: uint256
- acceptanceThreshold: uint256
- postedAt: uint256
- expiresAt: uint256
- state: enum
- claimCount: uint256 (optional)
- finalizedResultHash: bytes32 (optional)

The contract does NOT store:
- job spec
- inputs
- outputs
- meaning

---

## Claim Data Model

Each claim consists of:

- claimant: address
- resultHash: bytes32
- stake: uint256
- timestamp: uint256

Claims are keyed by `(jobId, claimant)`.

---

## State Transitions

### NONEXISTENT â POSTED

Triggered by: `postJob(...)`

Requirements:
- Caller authorized
- reward > 0
- expiresAt > now
- jobId does not exist

Effects:
- Job stored in POSTED
- Reward escrowed

---

### POSTED â CLAIMED

Triggered by: first `submitClaim(jobId, resultHash)`

Requirements:
- job.state == POSTED
- now < expiresAt
- stake >= stakeRequired

Effects:
- Claim stored
- job.state = CLAIMED
- claimCount += 1

---

### CLAIMED â CLAIMED (additional claims)

Triggered by: additional `submitClaim`

Requirements:
- job.state == CLAIMED
- now < expiresAt
- stake >= stakeRequired

Effects:
- Claim stored
- claimCount += 1

---

### CLAIMED â FINALIZED

Triggered when acceptance policy is met

Requirements:
- job.state == CLAIMED
- â¥ acceptanceThreshold matching resultHash values

Effects:
- job.state = FINALIZED
- finalizedResultHash set
- Reward distributed
- Stakes resolved

---

### POSTED â EXPIRED

Triggered by: `expireJob(jobId)` or lazy evaluation

Requirements:
- job.state == POSTED
- now >= expiresAt

Effects:
- job.state = EXPIRED
- Reward resolved per policy

---

### CLAIMED â EXPIRED

Triggered by: `expireJob(jobId)`

Requirements:
- job.state == CLAIMED
- now >= expiresAt
- acceptance policy unmet

Effects:
- job.state = EXPIRED
- Stakes resolved
- Reward resolved

---

## Terminal States

FINALIZED and EXPIRED are terminal.

- No further claims allowed
- No state changes permitted
- Any interaction must revert

---

## Critical Invariants

- Funds move only on FINALIZED or EXPIRED
- Jobs are immutable once POSTED
- All claims require stake
- No unilateral finalization unless policy allows
- Timeouts resolve deterministically

---

## Design Rationale

- Minimal state surface
- No unbounded loops
- No semantic interpretation
- Fully auditable
- Complexity pushed off-chain

This is an ideal Solidity workload.

---

## Future Extensions (Off-Chain)

- Agent networks
- CI/CD execution
- Monitoring jobs
- Legal and compliance workflows
- DAO self-operation

All extensions reuse this exact contract.

---

## Status

This document is considered **foundational**.
All future design must stack on top of it without modifying core assumptions.
