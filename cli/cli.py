# cli.py
import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv
from eth_account import Account
from web3 import Web3

import job_creation
import job_execution


DEFAULT_DB = Path("./daowork.db")
DEFAULT_JOB_JSON = Path("./job.json")


def die(msg: str) -> None:
    print("error:", msg, file=sys.stderr)
    sys.exit(1)


def load_env() -> Tuple[str, str, str]:
    load_dotenv()
    rpc = os.getenv("RPC_URL")
    pk = os.getenv("PRIVATE_KEY")
    addr = os.getenv("CONTRACT_ADDRESS") or os.getenv("DAO_WORK_ADDRESS")
    if not rpc or not pk or not addr:
        die("Missing RPC_URL, PRIVATE_KEY, or CONTRACT_ADDRESS/DAO_WORK_ADDRESS in .env")
    return rpc, pk, addr


def load_contract(w3: Web3, address: str):
    artifact_path = Path("../out/DaoWork.sol/DaoWork.json")
    if not artifact_path.exists():
        die("Missing ABI artifact at ../out/DaoWork.sol/DaoWork.json. Run `forge build` from repo root.")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=artifact["abi"])


def load_json_object(path: Path, *, label: str) -> Dict[str, Any]:
    if not path.exists():
        die(f"{label} not found: {path}")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{label} JSON parse error in {path}: {e}")
    if not isinstance(obj, dict):
        die(f"{label} must be a JSON object (top-level {{...}})")
    return obj


# ---------------- DB ----------------

def db_init(db_path: Path) -> None:
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode=WAL;")

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY,
            created_at INTEGER NOT NULL,
            created_by TEXT NOT NULL,
            stake_wei INTEGER NOT NULL,
            spec_hash TEXT NOT NULL,
            spec_json TEXT NOT NULL,
            state TEXT NOT NULL,
            last_tx TEXT
        );
        """
    )

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            submitted_at INTEGER NOT NULL,
            submitted_by TEXT NOT NULL,
            receipt TEXT NOT NULL,
            solution_json TEXT NOT NULL,
            tx_hash TEXT
        );
        """
    )

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS validations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            validated_at INTEGER NOT NULL,
            validator_id TEXT NOT NULL,
            claimed_receipt TEXT NOT NULL,
            computed_receipt TEXT NOT NULL,
            ok INTEGER NOT NULL,
            solution_json TEXT NOT NULL,
            note TEXT
        );
        """
    )

    con.commit()
    con.close()


def db_insert_job(
    db_path: Path,
    *,
    job_id: int,
    created_by: str,
    stake_wei: int,
    spec_hash: str,
    canonical_spec_json: str,
    tx_hash: str,
) -> None:
    con = sqlite3.connect(db_path)
    con.execute(
        """
        INSERT OR REPLACE INTO jobs(job_id, created_at, created_by, stake_wei, spec_hash, spec_json, state, last_tx)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            int(job_id),
            int(time.time()),
            created_by,
            int(stake_wei),
            spec_hash,
            canonical_spec_json,
            "created",
            tx_hash,
        ),
    )
    con.commit()
    con.close()


def db_get_job(db_path: Path, job_id: int) -> Optional[Dict[str, Any]]:
    con = sqlite3.connect(db_path)
    row = con.execute(
        "SELECT job_id, created_by, stake_wei, spec_hash, spec_json, state, last_tx FROM jobs WHERE job_id=?",
        (int(job_id),),
    ).fetchone()
    con.close()

    if not row:
        return None

    return {
        "job_id": row[0],
        "created_by": row[1],
        "stake_wei": row[2],
        "spec_hash": row[3],
        "spec": json.loads(row[4]),
        "state": row[5],
        "last_tx": row[6],
    }


def db_update_job_state(db_path: Path, job_id: int, state: str, last_tx: Optional[str]) -> None:
    con = sqlite3.connect(db_path)
    con.execute(
        "UPDATE jobs SET state=?, last_tx=? WHERE job_id=?",
        (state, last_tx, int(job_id)),
    )
    con.commit()
    con.close()


def db_list_jobs(db_path: Path, state: Optional[str]) -> list:
    con = sqlite3.connect(db_path)
    if state:
        rows = con.execute(
            "SELECT job_id, state, created_by, stake_wei, spec_hash FROM jobs WHERE state=? ORDER BY job_id",
            (state,),
        ).fetchall()
    else:
        rows = con.execute(
            "SELECT job_id, state, created_by, stake_wei, spec_hash FROM jobs ORDER BY job_id"
        ).fetchall()
    con.close()
    return rows


def db_add_submission(
    db_path: Path,
    *,
    job_id: int,
    submitted_by: str,
    receipt: str,
    canonical_solution_json: str,
    tx_hash: Optional[str],
) -> None:
    con = sqlite3.connect(db_path)
    con.execute(
        """
        INSERT INTO submissions(job_id, submitted_at, submitted_by, receipt, solution_json, tx_hash)
        VALUES(?, ?, ?, ?, ?, ?)
        """,
        (
            int(job_id),
            int(time.time()),
            submitted_by,
            receipt,
            canonical_solution_json,
            tx_hash,
        ),
    )
    con.commit()
    con.close()


def db_add_validation(
    db_path: Path,
    *,
    job_id: int,
    validator_id: str,
    claimed_receipt: str,
    computed_receipt: str,
    ok: bool,
    canonical_solution_json: str,
    note: str,
) -> None:
    con = sqlite3.connect(db_path)
    con.execute(
        """
        INSERT INTO validations(job_id, validated_at, validator_id, claimed_receipt, computed_receipt, ok, solution_json, note)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            int(job_id),
            int(time.time()),
            validator_id,
            claimed_receipt,
            computed_receipt,
            1 if ok else 0,
            canonical_solution_json,
            note,
        ),
    )
    con.commit()
    con.close()


# ---------------- Commands ----------------

def cmd_create(args, db_path: Path, w3: Web3, contract, account) -> None:
    spec_path = Path(args.job_json)
    spec_obj = load_json_object(spec_path, label="job spec")

    res = job_creation.create_job_canonical(
        w3=w3,
        contract=contract,
        account=account,
        stake_wei=args.stake_wei,
        spec_obj=spec_obj,
    )

    db_insert_job(
        db_path,
        job_id=res.job_id,
        created_by=res.created_by,
        stake_wei=res.stake_wei,
        spec_hash=res.spec_hash,
        canonical_spec_json=res.canonical_spec_json,
        tx_hash=res.tx_hash,
    )

    print("spec_hash:", res.spec_hash)
    print("job_id:", res.job_id)
    print("tx:", res.tx_hash)


def cmd_submit(args, db_path: Path, w3: Web3, contract, account) -> None:
    job = db_get_job(db_path, args.job_id)
    if not job:
        die("job not found in local db (you must have the spec locally)")

    solution_path = Path(args.solution_json)
    solution_obj = load_json_object(solution_path, label="solution")

    receipt = job_execution.compute_receipt(job["spec"], solution_obj)
    canon_solution = job_execution.canonical_json(solution_obj)

    print("receipt:", receipt)

    tx_hash: Optional[str] = None
    if args.send:
        tx_hash = job_execution.submit_work_onchain(
            w3=w3,
            contract=contract,
            account=account,
            job_id=args.job_id,
            receipt_hex=receipt,
        )
        db_update_job_state(db_path, args.job_id, "submitted", tx_hash)
        print("tx:", tx_hash)

    db_add_submission(
        db_path,
        job_id=args.job_id,
        submitted_by=account.address,
        receipt=receipt,
        canonical_solution_json=canon_solution,
        tx_hash=tx_hash,
    )


def cmd_validate(args, db_path: Path) -> None:
    job = db_get_job(db_path, args.job_id)
    if not job:
        die("job not found in local db (you must have the spec locally)")

    solution_path = Path(args.solution_json)
    solution_obj = load_json_object(solution_path, label="solution (for validation)")

    computed = job_execution.compute_receipt(job["spec"], solution_obj)
    canon_solution = job_execution.canonical_json(solution_obj)

    claimed = args.claimed_receipt
    ok = computed.lower() == claimed.lower()

    db_add_validation(
        db_path,
        job_id=args.job_id,
        validator_id=args.validator_id,
        claimed_receipt=claimed,
        computed_receipt=computed,
        ok=ok,
        canonical_solution_json=canon_solution,
        note=args.note or "",
    )

    print("computed:", computed)
    print("claimed :", claimed)
    print("ok:", ok)


def cmd_finalize(args, db_path: Path, w3: Web3, contract, account) -> None:
    tx = job_execution.finalize_onchain(
        w3=w3,
        contract=contract,
        account=account,
        job_id=args.job_id,
    )
    db_update_job_state(db_path, args.job_id, "finalized", tx)
    print("tx:", tx)


def main() -> None:
    p = argparse.ArgumentParser(prog="daowork")
    p.add_argument("--db", default=str(DEFAULT_DB), help="SQLite db path (default: ./daowork.db)")

    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="Hash job JSON + createJob{value} + mirror to db")
    c.add_argument("--stake-wei", type=int, required=True)
    c.add_argument("--job-json", default=str(DEFAULT_JOB_JSON), help="Path to job.json (default: ./job.json)")

    l = sub.add_parser("list", help="List jobs from local db")
    l.add_argument("--state", choices=["created", "submitted", "finalized"])

    sh = sub.add_parser("show", help="Show job record from local db")
    sh.add_argument("job_id", type=int)

    s = sub.add_parser("submit", help="Compute receipt(spec, solution) and optionally submitWork")
    s.add_argument("job_id", type=int)
    s.add_argument("--solution-json", required=True, help="Path to solution.json")
    s.add_argument("--send", action="store_true")

    v = sub.add_parser("validate", help="Recompute receipt from solution and compare to claimed receipt")
    v.add_argument("job_id", type=int)
    v.add_argument("--solution-json", required=True, help="Path to solution.json used for validation")
    v.add_argument("--claimed-receipt", required=True)
    v.add_argument("--validator-id", required=True)
    v.add_argument("--note")

    f = sub.add_parser("finalize", help="Finalize job on-chain (creator only)")
    f.add_argument("job_id", type=int)

    args = p.parse_args()
    db_path = Path(args.db)
    db_init(db_path)

    if args.cmd == "list":
        for row in db_list_jobs(db_path, getattr(args, "state", None)):
            print(*row)
        return

    if args.cmd == "show":
        job = db_get_job(db_path, args.job_id)
        if not job:
            die("job not found")
        print(json.dumps(job, indent=2, sort_keys=True))
        return

    # Chain-required commands
    rpc, pk, contract_addr = load_env()
    w3 = Web3(Web3.HTTPProvider(rpc))
    if not w3.is_connected():
        die("cannot connect to RPC_URL")

    account = Account.from_key(pk)
    contract = load_contract(w3, contract_addr)

    if args.cmd == "create":
        cmd_create(args, db_path, w3, contract, account)
    elif args.cmd == "submit":
        cmd_submit(args, db_path, w3, contract, account)
    elif args.cmd == "validate":
        cmd_validate(args, db_path)
    elif args.cmd == "finalize":
        cmd_finalize(args, db_path, w3, contract, account)
    else:
        die("unknown command")


if __name__ == "__main__":
    main()
