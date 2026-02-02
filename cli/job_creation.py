# job_creation.py
import json
import time
from dataclasses import dataclass
from typing import Any, Dict

from eth_utils import keccak


def canonical_json(obj: Dict[str, Any]) -> str:
    """
    Canonical JSON definition:
    - sorted keys
    - no whitespace ambiguity
    - UTF-8
    This is exactly what gets hashed.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def spec_hash_hex(spec_obj: Dict[str, Any]) -> str:
    """
    spec_hash = keccak256(canonical_json(spec))
    Returned as 0x-prefixed hex string.
    """
    blob = canonical_json(spec_obj).encode("utf-8")
    return "0x" + keccak(blob).hex()


@dataclass(frozen=True)
class CreateResult:
    job_id: int
    tx_hash: str
    stake_wei: int
    created_by: str
    created_at: int
    spec_hash: str
    canonical_spec_json: str


def create_job_onchain(*, w3, contract, account, stake_wei: int) -> tuple[int, str]:
    """
    Calls createJob{value: stake_wei}.
    Returns (job_id, tx_hash_hex).
    """
    tx = contract.functions.createJob().build_transaction(
        {
            "from": account.address,
            "value": int(stake_wei),
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": w3.eth.chain_id,
        }
    )
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    # nextJobId increments after creation, so job_id = nextJobId - 1
    next_id = contract.functions.nextJobId().call()
    job_id = int(next_id) - 1

    return job_id, "0x" + tx_hash.hex()


def create_job_canonical(*, w3, contract, account, stake_wei: int, spec_obj: Dict[str, Any]) -> CreateResult:
    """
    Primitive:
    - canonicalize spec
    - hash spec
    - anchor on-chain via createJob()
    Returns a single stable CreateResult object.
    """
    canon = canonical_json(spec_obj)
    h = "0x" + keccak(canon.encode("utf-8")).hex()

    job_id, tx_hex = create_job_onchain(
        w3=w3,
        contract=contract,
        account=account,
        stake_wei=stake_wei,
    )

    return CreateResult(
        job_id=job_id,
        tx_hash=tx_hex,
        stake_wei=int(stake_wei),
        created_by=account.address,
        created_at=int(time.time()),
        spec_hash=h,
        canonical_spec_json=canon,
    )
