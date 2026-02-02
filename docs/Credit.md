# Credit System

This document freezes the design and behavior of the **account-level credit system** in DaoWork as of this commit.

## Purpose

The credit system exists to introduce **economic friction and commitment** at the job-posting entrypoint, while avoiding per-job escrow complexity.

Posting a job requires stake.
That stake becomes **withdrawable account credit**, not a refundable job deposit.

This design:
- discourages spam and griefing
- rewards long-term participation
- keeps job lifecycle logic simple
- keeps Solidity surface area small and auditable

## Core Invariants

The following rules are enforced by tests and must remain true unless intentionally changed:

1. Posting a job requires ETH.
2. Posting a job increases the poster’s credit by `msg.value`.
3. Credit is **account-level**, not job-level.
4. Credit is owned by the posting address.
5. Credit can be withdrawn only by its owner.
6. Credit cannot be withdrawn in excess of the available balance.
7. Withdrawing credit reduces stored credit and transfers ETH.
8. Job lifecycle is independent of credit withdrawal.

## Contract Semantics

### Job Creation

- `createJob` is `payable`
- `msg.value > 0` is required
- ETH sent is added to `credit[msg.sender]`
- Job creation does **not** lock or reserve funds per job

### Credit Withdrawal

- `withdraw(amount)`:
  - requires `credit[msg.sender] >= amount`
  - reduces credit before transferring ETH
  - transfers ETH to `msg.sender`
- No automatic refunds
- No implicit job-based withdrawals

## Non-Goals (Explicitly Out of Scope)

The following are intentionally **not implemented** at this stage:

- Job reward payouts
- Executor payments
- Slashing or penalties
- Credit reuse semantics
- Governance over credit
- Rate limits or minimum stake tiers

These may be layered later without invalidating the current model.

## Design Rationale

This system treats stake as **commitment capital**, not escrow.

Users signal seriousness by capitalizing their account.
Jobs are lifecycle objects, not financial containers.
Funds movement is explicit and opt-in.

This keeps the contract:
- small
- reviewable
- gas-predictable
- composable with future primitives

## Status

Frozen for alpha.
Any changes must update tests and this document.
