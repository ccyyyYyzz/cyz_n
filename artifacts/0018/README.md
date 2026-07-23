# Brief 0018 source and event-contract controls

This directory contains two independent reference implementations for
Brief 0018:

1. a standard-library sampler for the zero-level-matched finite-\(K\)
   quadratic source; and
2. a rank-blind, total event-record contract for the later certified
   encounter solver.

Together they close the source measure and downstream record type within the
declared audit model.  They do **not** solve world-sheet roots, estimate
physical event masses, or select \(3+1\).

Run from the repository root:

```text
python artifacts/0018/microcanonical_source.py
python artifacts/0018/microcanonical_source.py --check
python artifacts/0018/event_contract.py
python artifacts/0018/event_contract.py --check
python -m unittest discover -s artifacts/0018 -p "test_*.py" -v
```

Both reports use strict parsed-JSON replay.  Duplicate keys, non-finite
numbers and type changes such as `true -> 1` are rejected, and LF/CRLF
checkout conversion does not change semantic comparison.

## Exact source control

`source_registry.json` is the only registered source cell used by both the
production sampler and the independent statistical audit.  It fixes

\[
\ell_s=1,\quad T_F=\frac1{2\pi},\quad L_w=16\pi,\quad M=T_FL_w=8,
\quad K=1,\quad E_\perp=2,
\]

\[
P_{\rm tot}=(4,4,0,\ldots,0),\qquad
L_0=\cdots=L_7=8,\quad L_8=L_w,\quad |w|=1,
\]

with winding axis \(8\) and orientations \(+1,-1\).  Validation enforces both
\(T_F=1/(2\pi\ell_s^2)\) and \(L_w=|w|L_8\), using the registered binary64
values.  This makes the audit cell internally consistent with the stated F1
convention; it is still a software-and-measure audit cell, not a cosmological
preparation or selection result.

The source registry samples the single ambient delta--Liouville
measure, not an arbitrary mixture and not a source conditioned on encounter
rank or validity.  With

\[
M=T_FL_w,\qquad d=16K,\qquad
E_*=E_\perp-\frac{\|P_{\rm tot}\|^2}{4M},
\]

and

\[
z_{in}^{L,R}=\sqrt{2M}\,k_nc_{in}^{L,R},
\]

the constrained energy shares obey

\[
\left(\frac{s_0}{E_*},\frac{s_1}{E_*},\frac{s_2}{E_*}\right)
\sim\operatorname{Dirichlet}(4,16K-1,16K-1)
\]

at \(\mathcal P_{\sigma,1}=\mathcal P_{\sigma,2}=0\).

The principal implementation uses independent integer-shape Gamma variables,
five independent sphere directions, and normalized Haar
\(Q_{\rm rel}\in T_\perp^8\).  The translation gauge is
\(Q_2=0,\ Q_1=Q_{\rm rel}\).  An algorithmically independent hierarchical
Beta control uses integer order statistics rather than the Gamma primitive.

The coefficient generator uses a registered 52-bit midpoint map strictly
inside \((0,1)\), named source substreams and a deterministic
90-digit-decimal/fixed-Taylor math layer.  The resulting source samples and
report are bitwise replayable on the tested Windows and Linux Python
runtimes, while retaining algorithm and coefficient fingerprints.

The source-draw identity covers the source schema, seed, sampler/math versions
and `source_draw_registry`; it excludes event thresholds, rank tolerance,
reaction data and source-validity thresholds.  Every failed validity
predicate is retained as `source_invalid`; no replacement is drawn.
Serialized samples are checked against a strict support schema, and their
polynomial constraints are re-evaluated exactly by interpreting each
IEEE-754 binary64 value as its dyadic rational.

The nonzero-world-sheet-momentum density is recorded only as a later scope:

\[
p(s_0,s_1,s_2)\propto
s_0^3\prod_i
\left(\frac{s_i^2-\pi_i^2}{4}\right)^{8K-1}
\delta(s_0+s_1+s_2-E_*),
\]

with \(s_i\ge|\pi_i|\) and
\(E_*>|\pi_1|+|\pi_2|\).  It is not sampled here.

## Total event-record contract

`event_record.schema.json` is a Draft 2020-12 shape contract.
`event_contract.py` supplies the cross-field semantics that ordinary JSON
Schema cannot express:

- deterministic primary precedence and exactly one mass row;
- finite-window censoring versus complete-time-domain no entry;
- strict outer overshoot before re-arming;
- outcome-conditional solver-certificate references;
- finite unordered and implicit positive-dimensional clusters;
- unresolved rank carrying no fabricated normal dimension, projector, frame,
  \(b\), or \(\ell\);
- certified-rank-two seven-dimensional normal-fiber controls; and
- episode merger/split/secondary-contact flags consistent with lineage.

The primary outcomes, in precedence order, are:

```text
source_invalid
left_censored_active_episode
torus_branch_ambiguous
ambiguous_tie
numerically_unresolved
no_entry_proved
right_censored_no_entry
right_censored_active_episode
tie_cluster
degenerate_spatial_minimum
grazing_entry
regular_first_entry
```

`ambiguous_tie` means root coverage is complete and only exact
equality/order of the earliest isolated candidates remains undecided.  A
possible missing or order-relevant unresolved root is
`numerically_unresolved`.  Complete ties retain the full unordered cluster;
no lexicographic scalar representative is physically authoritative.

The hysteresis contract uses

\[
T_{\rm out}
=\inf\{t>T_{\rm in}:\rho(t)>r_{\rm out}\}.
\]

An outer tangent touch does not re-arm.  Further inner contacts while active
remain marks of the same episode; a new episode becomes eligible only after
certified strict overshoot.

## Scope boundary

The controls do not establish:

- a unique cosmological or quantum F1 preparation;
- validity of the quadratic graph approximation as a continuum model;
- exhaustive first-entry, image or singular-root coverage;
- recurrence or a global all-time no-entry bound;
- a physical regular/exceptional event-mass ledger;
- an event-conditioned rank or singular-value law;
- a continuum limit, visible \(3+1\), cone, signature or time direction.

The next gate is a replayable interval-arithmetic solver with gap-free box and
image coverage, followed by the unconditioned finite-\(K\) population law.
