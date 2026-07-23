#!/usr/bin/env python3
"""Readable standard-Python generator launcher for Brief 0015."""
from generator_artifact import *

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plain standard-Python constructor interpreter for Brief 0015; emits a scheduled Markov-renewal artifact and never receives a response rank.")
    parser.add_argument("--spec", type=Path, default=Path(__file__).with_name("constructor_spec.json"))
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("control_vector_manifest.json"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("scheduled_kernel.json"))
    parser.add_argument("--verifier", type=Path, default=Path(__file__).with_name("verify_0015.py"), help="compatibility path; executable dependency set is read from the registered specification")
    parser.add_argument("--dependency-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--metric-radii", help="optional arbitrary exact nine-metric input, comma separated")
    parser.add_argument("--frame-arity", type=int)
    parser.add_argument("--opaque-id", default="opaque_cli_instance")
    parser.add_argument("--single-output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.metric_radii is not None:
            spec = load_json(args.spec)
            manifest = load_json(args.manifest)
            validate_constructor_spec(spec)
            if args.frame_arity is None:
                raise ConstructionError("--frame-arity is required with --metric-radii")
            template = dict(manifest["controls"][0]["input"])
            template["metric_radii"] = parse_metric_csv(args.metric_radii)
            template["frame_arity"] = args.frame_arity
            spec_hash = canonical_sha256(spec)
            manifest_hash = canonical_sha256(manifest)
            record = build_instance_record(spec, template, args.opaque_id, spec_hash, manifest_hash)
            out = args.single_output or args.output
            write_canonical_json(out, {"schema_version": "cyz-0015-single-instance-v1", "instance": record})
        else:
            artifact = build_artifact(args.spec, args.manifest, args.dependency_root)
            write_canonical_json(args.output, artifact)
        return 0
    except (ConstructionError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "ERROR", "code": "generator_error", "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2




if __name__ == "__main__":
    raise SystemExit(main())
