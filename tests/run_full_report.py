from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "0015"


def main() -> int:
    process = subprocess.run(
        [
            sys.executable,
            "-I",
            str(ARTIFACTS / "verify_0015.py"),
            "--report",
            str(ARTIFACTS / "verification_report.json"),
            "--dependency-root",
            str(ROOT),
        ],
        capture_output=True,
        text=True,
        timeout=1800,
    )
    parsed = None
    for line in reversed(process.stdout.splitlines()):
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        break
    summary = {
        "exit_code": process.returncode,
        "status": parsed.get("status") if isinstance(parsed, dict) else None,
        "error": parsed.get("error") if isinstance(parsed, dict) else None,
        "mutation_count": (
            parsed.get("mutation_count")
            if isinstance(parsed, dict)
            else None
        ),
        "artifact_payload_sha256": (
            parsed.get("artifact_payload_sha256")
            if isinstance(parsed, dict)
            else None
        ),
        "stderr": process.stderr[-2000:],
    }
    check = None
    if process.returncode == 0:
        checked = subprocess.run(
            [
                sys.executable,
                "-I",
                str(ARTIFACTS / "verify_0015.py"),
                "--check-report",
                str(ARTIFACTS / "verification_report.json"),
                "--dependency-root",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        check_payload = None
        for line in reversed(checked.stdout.splitlines()):
            try:
                check_payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            break
        check = {
            "exit_code": checked.returncode,
            "status": (
                check_payload.get("status")
                if isinstance(check_payload, dict)
                else None
            ),
            "error": (
                check_payload.get("error")
                if isinstance(check_payload, dict)
                else None
            ),
            "verification_report_sha256": (
                check_payload.get("verification_report_sha256")
                if isinstance(check_payload, dict)
                else None
            ),
        }
        if checked.returncode != 0:
            process = checked
    summary["acceptance_check"] = check
    print(json.dumps(summary, sort_keys=True, ensure_ascii=False))
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
