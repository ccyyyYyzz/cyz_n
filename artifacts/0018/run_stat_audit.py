#!/usr/bin/env python3
"""CLI for the frozen Brief 0018 controlled source audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import stat_audit_core as core
import statistical_audit as audit


DEFAULT_FULL_REPORT = Path(__file__).resolve().parent / "stat_audit_report.json"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run audit-k1-v1. The full profile executes the fixed 514-item "
            "statistical ledger; fast is non-authoritative structural replay."
        )
    )
    parser.add_argument(
        "--profile",
        choices=("full", "fast"),
        default="full",
        help="full is the only preregistered statistical acceptance profile",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "report path; full defaults beside this script, while fast writes "
            "only when an explicit path is supplied"
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate and compare strict semantic JSON without writing",
    )
    return parser.parse_args()


def resolve_output(arguments: argparse.Namespace) -> Path | None:
    if arguments.output is not None:
        return arguments.output.resolve()
    if arguments.profile == "full":
        return DEFAULT_FULL_REPORT
    return None


def main() -> int:
    arguments = parse_arguments()
    output = resolve_output(arguments)
    if arguments.check and output is None:
        raise SystemExit("--check requires --output for the fast profile")

    report = audit.build_report(arguments.profile)
    action: str
    if arguments.check:
        assert output is not None
        stored = core.load_strict_json(output)
        if not core.verify_semantic_hash(stored):
            raise SystemExit("stored report semantic SHA-256 is invalid")
        core.strict_report_compare(stored, report)
        action = "verified strict semantic JSON"
    elif output is not None:
        core.write_canonical_report(output, report)
        action = "wrote canonical report"
    else:
        action = "evaluated without writing"

    summary = {
        "action": action,
        "failed_gate_count": len(report["failed_gates"]),
        "output": None if output is None else output.as_posix(),
        "profile": arguments.profile,
        "semantic_sha256": report["semantic_sha256"],
        "status": report["status"],
    }
    print(
        json.dumps(
            summary,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    )
    return 0 if not report["failed_gates"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
