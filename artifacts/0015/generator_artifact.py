#!/usr/bin/env python3
"""Generator artifact assembly for Brief 0015."""
from generator_model import *

def build_artifact(spec_path: Path, manifest_path: Path, dependency_root: Path) -> Dict[str, Any]:
    spec = load_json(spec_path)
    manifest = load_json(manifest_path)
    validate_constructor_spec(spec)
    spec_hash = canonical_sha256(spec)
    manifest_hash = canonical_sha256(manifest)
    if manifest.get("constructor_spec_sha256") != spec_hash:
        raise ConstructionError("control manifest is not bound to the supplied constructor specification")
    instances = []
    seen_ids = set()
    for control in manifest.get("controls", []):
        oid = control["opaque_id"]
        if oid in seen_ids:
            raise ConstructionError(f"duplicate opaque control id: {oid}")
        seen_ids.add(oid)
        instances.append(build_instance_record(spec, control["input"], oid, spec_hash, manifest_hash))
    dependencies = []
    for rel in spec["executable_dependencies"]:
        path = dependency_root / rel
        if not path.exists():
            raise ConstructionError(f"missing executable dependency: {rel}")
        dependencies.append({"path": rel, "normalized_lf_sha256": normalized_lf_sha256(path)})
    return {
        "schema_version": SCHEMA_VERSION,
        "generator_api_version": GENERATOR_API_VERSION,
        "process_type": spec["process_type"],
        "ctmc_export": spec["ctmc_export"],
        "classification": spec["classification"],
        "constructor_spec_path": "artifacts/0015/constructor_spec.json",
        "constructor_spec_sha256": spec_hash,
        "control_vector_manifest_path": "artifacts/0015/control_vector_manifest.json",
        "control_vector_manifest_sha256": manifest_hash,
        "constructor_program_sha256": canonical_sha256(spec["constructor_program"]),
        "executable_dependencies": dependencies,
        "instances": instances,
        "opaque_instance_ids_are_nonsemantic": True,
        "expanded_hash_stream_format": "section-name LF then canonical [key,value] records LF",
    }


def parse_metric_csv(text: str) -> List[str]:
    parts = [x.strip() for x in text.split(",") if x.strip()]
    if len(parts) != 9:
        raise ConstructionError("--metric-radii requires nine comma-separated exact fractions")
    for p in parts:
        parse_fraction(p)
    return parts

