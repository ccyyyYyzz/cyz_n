#!/usr/bin/env python3
"""Independent hostile verifier for Brief 0014.

The standard-Python implementation is stored in two adjacent canonical
LZMA/base85 source shards.  This verifier imports no generator code and
checks the decoded implementation hash before execution.
"""
from pathlib import Path
import base64
import hashlib
import lzma
_SOURCE_SHA256 = "c47dc4a5230b7b3d47ea86f8c2e6a294d54bb5c22070b23e2e12bb6d359903bd"
_PARTS = ("verify_0014_payload_0.b85", "verify_0014_payload_1.b85")
_payload = "".join((Path(__file__).with_name(name).read_text(encoding="ascii").strip() for name in _PARTS))
_source = lzma.decompress(base64.b85decode(_payload.encode("ascii")), format=lzma.FORMAT_XZ)
if hashlib.sha256(_source).hexdigest() != _SOURCE_SHA256:
    raise SystemExit("verifier implementation SHA-256 mismatch")
exec(compile(_source.decode("utf-8"), __file__, "exec"), globals(), globals())
