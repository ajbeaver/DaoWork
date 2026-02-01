# Threat Model and Economic Assumptions

This document defines the explicit threat model and economic assumptions for DaoWork.
It exists to prevent implicit design decisions from leaking into code and tests.

This document is intentionally conservative.

---

## Scope

This threat model applies **only** to the on-chain contract.
Off-chain executors, agents, and tooling are assumed to be replaceable and adversarial.

---

## Adversarial Assumptions

The system assumes:

- Any external actor may behave maliciously
- Any executor may lie, spam, or disappear
- Any participant may attempt to extract value dishonestly
- Collusion between executors is possible
- Network conditions may degrade or stall

The system does **not** assume honesty.

---

## Trusted Assumptions

The system assumes:

- Ethereum consensus eventually finalizes blocks
- Block timestamps are approximately monotonic
- ETH transfers execute as specified by the EVM
- Cryptographic hashes are collision resistant

No other trust assumptions are permitted.

---

## Allowed Failures

The following failures are acceptable and must not compromise safety:

- No executor claims a job
- Jobs expire without resolution
- Multiple conflicting claims are submitted
- Executors abandon jobs mid-process
- High gas prices reduce participation

These failures affect liveness, not correctness.

---

## Disallowed Failures

The following outcomes must never occur:

- Funds move before FINALIZED or EXPIRED
- A job finalizes without meeting acceptance policy
- A single actor forces consensus without stake
- Jobs change meaning after POSTED
- Terminal states are exited

Any of these constitute a critical bug.

---

## Economic Assumptions

- Executors are economically rational
- Staking discourages dishonest claims
- Rewards exceed expected execution cost
- Failed participation is cheaper than dishonest participation

The system does not rely on altruism.

---

## Spam and Griefing

Spam is mitigated by:

- Mandatory stake for claims
- Escrowed rewards for jobs
- Time-based expiration

Griefing that costs the attacker money is acceptable.

---

## Collusion

Collusion is expected.

Mitigations:

- Acceptance thresholds
- Stake-weighted consequences
- Open participation

The system tolerates collusion up to the configured threshold.

---

## Oracle Safety

The system does not rely on a single oracle.

Consensus emerges from:
- Independent claims
- Matching result hashes
- Economic alignment

Truth is defined by agreement, not correctness.

---

## Time-Based Risks

Risks:

- Delayed finalization
- Timestamp manipulation within bounds
- Executor latency

Mitigations:

- Explicit expiration times
- Deterministic resolution paths

---

## Non-Goals

The system explicitly does NOT attempt to:

- Guarantee job correctness
- Enforce semantic meaning
- Prevent all griefing
- Optimize for maximal throughput
- Replace legal or social processes

---

## Design Principle

If a threat requires the contract to understand job semantics to mitigate it,
the mitigation is invalid.

All safety must emerge from:
- State transitions
- Stake
- Time
- Finality

---

## Status

This document is foundational.
Tests and code must enforce these assumptions explicitly.
