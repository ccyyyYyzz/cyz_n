from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "0015"
sys.path.insert(0, str(ARTIFACTS))

import verifier_core as core  # noqa: E402
import verifier_hostile as hostile  # noqa: E402


def main(names: list[str]) -> int:
    selected = names or [row[0] for row in hostile.MUTATIONS]
    failures: list[dict[str, str]] = []
    for index, name in enumerate(selected, 1):
        try:
            hostile.run_named_mutation(
                ROOT,
                ARTIFACTS / "scheduled_kernel.json",
                ARTIFACTS / "constructor_spec.json",
                ARTIFACTS / "control_vector_manifest.json",
                ARTIFACTS / "generate_0015.py",
                ARTIFACTS / "verify_0015.py",
                name,
            )
        except Exception as exc:
            code = (
                exc.code
                if isinstance(exc, core.VerificationError)
                else type(exc).__name__
            )
            failures.append(
                {"mutation": name, "code": code, "message": str(exc)}
            )
            print(
                f"{index}/{len(selected)} FAIL {name}: {code}: {exc}",
                flush=True,
            )
        else:
            print(
                f"{index}/{len(selected)} PASS {name}",
                flush=True,
            )
    print(json.dumps({"failures": failures}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
