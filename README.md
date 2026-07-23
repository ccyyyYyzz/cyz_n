# Visible spacetime research exchange

This public repository is the shared, versioned interface between the local
research agent and the browser-hosted GPT co-theorist for a long-term project:

> Why do restricted observers robustly recover a (3+1)-dimensional
> Lorentzian world?

It is not the full working repository.  It contains only self-contained public
research briefs, distilled responses, theorem state and decisions that another
reasoning system needs in order to continue the project without relying on a
private chat transcript.

## Layout

- `state/PROJECT_STATE.md` — current canonical claims, boundaries and active
  bottleneck;
- `briefs/` — numbered tasks sent to the GPT co-theorist;
- `responses/` — distilled responses, with provenance and verification status;
- `decisions/` — durable architecture choices and reversals.

## Exchange rule

1. A brief is committed before a new hard problem is sent.
2. GPT is asked to originate the strongest solution it can, not to review a
   manuscript.
3. GPT writes the returned argument directly into the matching response file
   through the connected GitHub capability. If direct main writes are not
   available, it opens a narrowly scoped pull request; downloadable attachments
   are fallback only.
4. Every adopted statement is independently proved locally or linked to a
   primary source; model output is never itself treated as evidence.
5. `state/PROJECT_STATE.md` is updated only when the evidence status changes.

The complete local project may contain simulations, manuscripts and private
working material that are intentionally absent here.

## Verifiable implementation artifacts

- [`artifacts/0019/`](artifacts/0019/) contains the Brief 0019 exact
  certificate foundation, source-separated replay, and the first
  source-bound physical result.  For registered source index 2, an exact
  symbolic-\(\pi\) closed-string lift and an outward-rounded Arb cover prove
  finite-window `right_censored_no_entry` on the true world-sheet quotient.
  The unconditioned source population, near-threshold first-entry branches
  and \(3+1\) selection dynamics remain open.
