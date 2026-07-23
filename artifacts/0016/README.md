# Brief 0016 executable probe

Run the deterministic probe and all regression tests from this directory's
repository root:

```text
python artifacts/0016/probe_0016.py --check
python -m unittest discover -s artifacts/0016 -p "test_*.py" -v
```

The first command writes
`artifacts/0016/source_to_return_kinematic_probe.json`.  The implementation
uses only the Python standard library.

The event rank is computed solely from the incoming local Jacobian
`[tau1, -tau2, relative_velocity]` through its symmetric 3-by-3 Gram matrix.
The fixed-scattering-axis regression test is intentionally a counterexample:
even when that axis is nonzero and normal to a straight opposite-winding
incoming span, declaring it does not change the incoming rank from two to
three.

This is a local theorem/probe artifact.  It does not supply a tangent
preparation, return law, anonymous response rank, or time/signature result.
The ball and box tables extend the Gaussian over supports containing zero
impact; that is a declared mathematical control, not a claim that the
large-impact source asymptotic is valid in the unresolved core.
