#!/usr/bin/env python3
"""Readable independent verifier launcher for Brief 0015."""
from verifier_hostile import *

def main(argv: Sequence[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description="Independent plain-Python hostile verifier for the registered Brief 0015 scheduled constructor. Imports no generator module.")
    parser.add_argument("--artifact",type=Path,default=Path(__file__).with_name("scheduled_kernel.json"))
    parser.add_argument("--spec",type=Path,default=Path(__file__).with_name("constructor_spec.json"))
    parser.add_argument("--manifest",type=Path,default=Path(__file__).with_name("control_vector_manifest.json"))
    parser.add_argument("--generator",type=Path,default=Path(__file__).with_name("generate_0015.py"))
    parser.add_argument("--dependency-root",type=Path,default=Path(__file__).resolve().parents[2])
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument("--baseline",action="store_true")
    mode.add_argument("--portability",action="store_true")
    mode.add_argument("--report",type=Path)
    parser.add_argument("--record",type=Path)
    parser.add_argument("--patch",type=Path)
    parser.add_argument("--patch-instance")
    parser.add_argument("--skip-regeneration",action="store_true")
    parser.add_argument("--baseline-record",type=Path,default=Path(__file__).with_name("baseline_report.json"))
    parser.add_argument("--portability-record",type=Path,default=Path(__file__).with_name("portability_report.json"))
    args=parser.parse_args(argv)
    try:
        patch=load_json(args.patch) if args.patch else None
        if args.portability:
            result=portability_check(args.dependency_root,args.artifact,args.spec,args.manifest,args.generator,Path(__file__))
        elif args.report:
            result=clean_tree_report(args.dependency_root,args.artifact,args.spec,args.manifest,args.generator,Path(__file__),args.baseline_record,args.portability_record)
            write_canonical_json(args.report,result)
        else:
            result=verify_full(args.artifact,args.spec,args.manifest,args.generator,args.dependency_root,patch,args.patch_instance,not args.skip_regeneration)
        if args.record:
            write_canonical_json(args.record,result)
        print(json.dumps(result,sort_keys=True,separators=(",",":"),ensure_ascii=False))
        return 0
    except VerificationError as exc:
        record={"status":"ERROR","error":exc.record()}
        if args.record:
            write_canonical_json(args.record,record)
        print(json.dumps(record,sort_keys=True,separators=(",",":"),ensure_ascii=False))
        return 2
    except Exception as exc:
        record={"status":"ERROR","error":{"code":"verifier_internal","message":repr(exc),"location":""}}
        if args.record:
            write_canonical_json(args.record,record)
        print(json.dumps(record,sort_keys=True,separators=(",",":"),ensure_ascii=False))
        return 3




if __name__ == "__main__":
    raise SystemExit(main())
