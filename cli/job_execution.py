# job_execution.py
import json
from dataclasses import dataclass
from typing import Any, Dict

from eth_utils import keccak


def canonical_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_receipt(spec_obj: Dict[str, Any], solution_obj: Dict[str, Any]) -> str:
    """
    receipt = keccak256( canonical_json(spec) || "|" || canonical_json(solution) )

    The tool does NOT interpret semantics.
    It only hashes what the user provides.
    """
    blob = (canonical_json(spec_obj) + "|" + canonical_json(solution_obj)).encode("utf-8")
    return "0x" + keccak(blob).hex()


@dataclass(frozen=True)
class SubmitResult:
    job_id: int
    tx_hash: str
    submitted_by: str
    receipt: str
    canonical_solution_json: str


def _receipt_hex_to_bytes32(receipt_hex: str) -> bytes:
    if not isinstance(receipt_hex, str) or not receipt_hex.startswith("0x"):
        raise ValueError("receipt must be 0x-prefixed hex string")
    raw = bytes.fromhex(receipt_hex[2:])
    if len(raw) != 32:
        raise ValueError("receipt must be 32 bytes (bytes32)")
    return raw


def submit_work_onchain(*, w3, contract, account, job_id: int, receipt_hex: str) -> str:
    """
    Calls submitWork(job_id, bytes32(receipt)).
    Returns tx hash hex.
    """
    receipt_b32 = _receipt_hex_to_bytes32(receipt_hex)

    tx = contract.functions.submitWork(int(job_id), receipt_b32).build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": w3.eth.chain_id,
        }
    )
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return "0x" + tx_hash.hex()


def finalize_onchain(*, w3, contract, account, job_id: int) -> str:
    """
    Calls finalize(job_id).
    Returns tx hash hex.
    """
    tx = contract.functions.finalize(int(job_id)).build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": w3.eth.chain_id,
        }
    )
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return "0x" + tx_hash.hex()
