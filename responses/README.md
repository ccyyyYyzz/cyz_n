# Response records

Each response file matches one numbered brief and uses this header:

```yaml
brief: 0001
source: browser-hosted GPT
captured: YYYY-MM-DD
status: raw | distilled | locally-verified | rejected
```

The body must separate:

- proposed definitions;
- theorem statements;
- proof obligations;
- counterexamples;
- locally adopted conclusions;
- unresolved or rejected claims.

Model prose is not evidence.  A response becomes `locally-verified` only after
its proof has been checked or its external claims have been traced to primary
sources.

