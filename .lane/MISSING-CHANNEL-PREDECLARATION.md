# Predeclaration: b523 Q1276 structural missing-channel audit

Date: 2026-08-23

## Frozen starting point

- source/evidence commit:
  `5e7c52319213f350f800b5269abfb9f8ad86fdcf`;
- exact circuit operations: `12,901,678`;
- exact circuit operations SHA-256:
  `d460c3968659b6bbbf5615268d73df210df55f9cd4cbca330de1ef960c6dd4c0`;
- exact-port model source SHA-256:
  `7f0373926fa313453f6e349703c3f89d63b6f7d52bf0bff94258479fe609bf42`;
- frozen calibration receipt SHA-256:
  `2e580159693cdbfedc09cb972c71672837e773ee219bb8facda1d6eb4448de37`.

The exact-port hypothesis is terminal `FAIL_MODEL`: evaluator/model aggregate
counts are `1048/1045`, with the only count differences at nonces
`444000000002`, `444000000040`, and `444000000042`, each evaluator count one
higher.  These three rows are localization evidence, not a tuning corpus.

## Question

Does one source-semantic circuit mechanism produce the evaluator-only fault
shots, and can that mechanism be represented without nonce, shot, or fixture
special cases?

## Allowed diagnostic work

1. Reproduce the baked operations independently for the three fixed failure
   nonces and require the exact operation count and hash family expected from
   the unchanged source.
2. Use temporary trusted-evaluator instrumentation to emit exact classical
   mismatch shot indices.  Preserve evaluator semantics; instrumentation may
   only expose existing mismatch indices, total Toffoli count, shot count, and
   bounded first-divergence/op context.
3. Extract the predictor's exact mismatch-shot sets without changing its model.
4. Compare exact sets.  Localize each evaluator-only or predictor-only shot to
   the earliest divergent circuit mechanism and identify its source-level
   guard/state transition.
5. Derive at most one minimal source-semantic predictor correction.  The
   correction must describe a general circuit rule and must not inspect or
   branch on a frozen nonce, shot index, expected count, or fixture membership.

No model-semantic edit is allowed until the exact-set comparison and mechanism
trace have been frozen in a durable diagnosis commit.

## Blinded disjoint validation corpus

The 32 nonces in `.lane/missing-channel-disjoint-v1.tsv` are frozen before any
mechanism diagnosis.  Each is the big-endian integer represented by the first
12 hexadecimal digits of:

`SHA256("b523-q1276-missing-channel-disjoint-v1:%02d" % index)`.

They are disjoint from H64.  Trusted-evaluator outcomes for this corpus must not
be generated or inspected until after the proposed correction is committed.

## Gates

### Diagnosis gate

- exact trusted-evaluator and predictor shot sets for all three failed rows;
- every set difference enumerated;
- first divergent operation/mechanism recorded for each differing shot;
- one source-semantic hypothesis or a terminal proof that no bounded common
  mechanism was found.

### Correction gate

If a correction exists, freeze its source commit before revealing the disjoint
evaluator outcomes.  Re-run the original fixed H64 and require exact count and
shot-set equality on all 64 rows.  Any mismatch keeps `FAIL_MODEL`.

### Disjoint gate

Run unchanged full 9,024-shot evaluation for all 32 frozen disjoint nonces and
compare exact classical shot sets, not only counts.  Exact parity requires
32/32 set equality.  An approximate mode may be described only as canary-only:
predictor undercount can create extra confirmer work, while any predictor-only
fault (overprediction at the shot-set level) can discard a true zero and blocks
all scan use.

Linux/CUDA parity remains downstream of exact CPU-model parity.  No parity host,
range, scan, hunt, provider, submission, or incumbent may be touched in this
audit.

## Artifact policy

Commit only clean source, predeclarations, compact exact-set/trace evidence, and
verdicts.  Keep generated operations, evaluator binaries, raw logs, temporary
instrumentation, and scan artifacts outside Git.

