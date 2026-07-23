#!/usr/bin/env python3
"""One-shot materializer for Brief 0013 staging payload."""
from __future__ import annotations

import base64
import hashlib
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PART_GLOB = "staging_payload.part*"
ARCHIVE_SHA256 = "67f5ae73d00c097343e9e749f31ec0c480d02211eae0d971642078f68265e718"
EXPECTED = {
    "artifacts/0013/reproduce_0013.py": "9c9af73a314261e173709f9123871026640b6a3095475d0e0e2cfbd4f00e6432",
    "artifacts/0013/kernel_ledger.json.xz.b64": "834215c9f241c4f1a3d796e5a012855fbe7156714dad55286649c107baf68cd5",
    "artifacts/0013/replay_report.json": "94b15982a970996128eb5a8538eb2764029df24d2d00199d755c4e1eb2b6a663",
    "responses/0013_instantiate_full_t9_scheduled_encounter_kernel.md": "aa1ba72002be46e710d982ffcf8e2f6064c8f5076d0bc130b5954e496b5fab22",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    staging = ROOT / "artifacts" / "0013"
    parts = sorted(staging.glob(PART_GLOB))
    if not parts:
        raise SystemExit("no staging payload parts")
    armored = b"".join(p.read_bytes() for p in parts)
    archive = base64.b64decode(armored.strip(), validate=True)
    if hashlib.sha256(archive).hexdigest() != ARCHIVE_SHA256:
        raise SystemExit("staging archive hash mismatch")
    with tempfile.TemporaryDirectory() as td:
        tar_path = Path(td) / "payload.tar.xz"
        tar_path.write_bytes(archive)
        with tarfile.open(tar_path, "r:xz") as tf:
            names = set(tf.getnames())
            if names != {"reproduce_0013.py", "final_response.md"}:
                raise SystemExit(f"unexpected payload members: {sorted(names)}")
            tf.extractall(td, filter="data")
        (staging / "reproduce_0013.py").write_bytes((Path(td) / "reproduce_0013.py").read_bytes())
        response_dir = ROOT / "responses"
        response_dir.mkdir(exist_ok=True)
        (response_dir / "0013_instantiate_full_t9_scheduled_encounter_kernel.md").write_bytes(
            (Path(td) / "final_response.md").read_bytes()
        )
    run("python3", "artifacts/0013/reproduce_0013.py", "--write",
        "artifacts/0013/kernel_ledger.json.xz.b64", "--report",
        "artifacts/0013/replay_report.json")
    run("python3", "artifacts/0013/reproduce_0013.py", "--verify",
        "artifacts/0013/kernel_ledger.json.xz.b64", "--verify-report",
        "artifacts/0013/replay_report.json")
    for rel, expected in EXPECTED.items():
        got = sha256(ROOT / rel)
        if got != expected:
            raise SystemExit(f"hash mismatch {rel}: {got} != {expected}")
    for p in parts:
        p.unlink()
    Path(__file__).unlink()
    print("Brief 0013 materialization and deterministic replay passed")


if __name__ == "__main__":
    main()
