# DaoWork

**Status: Archived proof of concept**

DaoWork is an experimental Ethereum project exploring trust-minimized coordination of off-chain work.

The original question behind the project was simple:

> How can two parties coordinate work, commit to an agreement, and record its completion without relying entirely on mutual trust?

DaoWork explored using Ethereum as a neutral coordination layer while keeping the actual work itself off-chain.

This repository contains the original prototype. It is preserved as a learning project and design experiment rather than a production-ready protocol.

## The Idea

Most useful work cannot or should not happen on-chain.

Source code, documents, research, infrastructure changes, datasets, and other work products are usually better handled by normal off-chain systems. Ethereum can still provide useful guarantees around the agreement itself.

The prototype explored separating those concerns:

```text
off-chain
─────────────────────────────

job specification
work artifact
validation
human / agent execution

             │
             │ cryptographic commitments
             ▼

on-chain
─────────────────────────────

job identity
participants
ETH
submission receipt
state transitions
```

The intention was for Ethereum to act as a coordination and settlement primitive rather than an execution environment for the work itself.

## Prototype Architecture

The project contains two primary components.

### Solidity contract

`src/DaoWork.sol` implements a minimal job lifecycle.

A creator can create a job by sending ETH.

A worker can submit a `bytes32` receipt representing work performed off-chain.

The job creator can finalize a submitted job.

The contract also tracks account credit and allows withdrawals.

The Solidity implementation was deliberately small while I learned Foundry, Solidity state, mappings, payable functions, authorization, and contract testing.

### Python CLI

The `cli/` directory contains a Web3.py reference client.

It experiments with:

- deterministic JSON canonicalization
- Keccak hashing of job specifications and solutions
- locally signed Ethereum transactions
- contract interaction through Web3.py
- local SQLite state
- submission receipt generation and validation

The CLI treats the blockchain as the authoritative coordination layer while retaining richer job information locally.

## Original Model

The intended conceptual lifecycle was roughly:

```text
Creator
   │
   │ define work
   │ fund reward
   ▼
 Job Created
   │
   │ work occurs off-chain
   ▼
Work Submitted
   │
   │ cryptographic receipt
   ▼
 Verification
   │
   ▼
Settlement
```

An early version of the design included independent validators who could verify that submitted work met the job requirements.

That design eventually exposed the most interesting problem in the project.

## The Unresolved Problem: Verification

Ethereum is very good at proving things such as:

- which account performed an action
- whether funds were escrowed
- whether a particular hash was committed
- whether a state transition occurred
- whether a signature is valid
- whether contract-defined rules were followed

Ethereum cannot generically determine whether arbitrary off-chain work is correct.

It cannot determine whether a spreadsheet is accurate, a program satisfies an informal requirement, a research report is useful, or a design meets someone's expectations.

That leaves a fundamental question:

> How can arbitrary work be verified and fairly settled between mutually untrusted parties?

Possible approaches include deterministic tests, independent attestations, validator quorums, trusted execution environments, cryptographic proofs, optimistic challenge systems, and human arbitration.

None provides a universal solution.

The prototype originally treated a third-party validator as the answer. Further exploration made it clear that verification itself is a much larger protocol problem and should not be hidden behind a single trusted role.

## Known Limitations

This implementation should not be interpreted as a secure escrow or production work protocol.

In particular, the prototype does not fully implement the economic model described by the original concept.

The job specification hash is calculated by the Python client but is not committed to the Solidity contract.

ETH supplied during job creation becomes credit associated with the creator rather than a true worker escrow.

Finalization changes job state but does not transfer a reward to the submitting worker.

The contract does not record the worker responsible for a submission.

The first submitted receipt occupies the only submission slot, which creates obvious griefing and coordination problems.

The verification mechanism remains mostly off-chain and trust-based.

These limitations are part of why the implementation has been archived rather than incrementally extended.

## Why Keep It?

DaoWork was useful as a learning project even though I ultimately chose not to continue developing the protocol.

It was my first serious attempt to connect:

```text
Solidity
   ↕
Ethereum / EVM
   ↕
Web3.py
   ↕
off-chain application state
```

Working on it helped clarify an architectural distinction that continues to influence my later work:

> Blockchains are often more useful as systems of authority, identity, commitment, and provenance than as places where the work itself should execute.

The project also led to broader questions around autonomous software agents, delegated authority, cryptographic identity, attestations, provenance, and how agents can safely perform externally verifiable actions.

Those problems are more relevant to the direction of my current work than building a generalized marketplace for distributed human labor.

## Repository Status

DaoWork is archived conceptually.

The repository remains public as:

- a proof of concept
- a record of my early Solidity and Web3.py work
- documentation of an architectural experiment
- an example of a project whose design questions became more valuable than its implementation

It is not maintained as production software and should not be used to custody real funds.

## Development

The Solidity project uses [Foundry](https://book.getfoundry.sh/).

Build:

```bash
forge build
```

Run tests:

```bash
forge test
```

The Python reference client is under `cli/`.

Its dependencies are listed in:

```text
cli/requirements.txt
```

The project was primarily developed and tested against a local Anvil chain.

## License

MIT License.

Copyright (c) 2026 AJ Beaver
