# Q1274 corrected CPU model: H64 failure

Date: 2026-08-23

## Verdict

`FAIL_MODEL`; `HOLD_DISJOINT32`; `HOLD_PARITY`; `HOLD_SCAN`; `HOLD_HUNT`;
`HOLD_PROVIDER`; `HOLD_SUBMIT`.

The already-qualified Q1276 generic coordinate-shell correction transfers to
Q1274 without fixture-specific edits and matches 62/64 complete H64 classical
shot sets.  Two Q1274 evaluator-only shots remain.  There are no predictor-only
shots.  The frozen blinded disjoint32 has not been evaluated or inspected.

## Port identity

The Q1274 predictor is byte-identical to
`research/b523-q1276-model-qualify@3be0bf0:src/bin/pingpong_filter.rs` except
for the source-bound validated operation count `12,901,678 -> 12,935,433`.  It
builds the current Q1274 circuit source directly.

- predictor source SHA-256:
  `aee0f0d03622a293a62e7d180d63eb3d426ea30ff3f694c42923b3ccbf4e1851`;
- local release binary SHA-256:
  `7d5a67139ed1b96ae994ef722549d188c73946eaa587d5535163f060c567bb58`;
- predicted operation count: `12,935,433`;
- built-in SHAKE/checkpoint/scalar/point self-test: `PASS`;
- model defaults: divide/multiply rounds `700/696`, replay fold `53`, B1 `30`;
- ported correction: generic low53/high203 coordinate subtraction plus fused
  reverse subtraction; no nonce, shot, expected-count, or fixture branch.

## Exact H64 result

- trusted evaluator rows: 64, Q1274, 12,935,433 operations, ancilla zero;
- trusted evaluator classical total: `1,032`;
- predictor classical total: `1,030`;
- complete-set equality: `62/64`;
- evaluator-only shots: `2`;
- predictor-only shots: `0`;
- predictor count receipt SHA-256:
  `c97b2240789c2cb583fd2f784010f8e91e24c19b19f5db78a797863307f5f6b9`;
- predictor verbose receipt SHA-256:
  `436aeb718fb7b36723841d2f189fa2c86f7e45a80829d89bd8cfe0ae617a80f5`;
- paired evaluator raw receipt SHA-256:
  `10ecb3139f4280bdf61b44a4416fc6ce301119f259f1e2a343ed283b7862b947`.

| nonce | evaluator | predictor | evaluator-only | predictor-only |
| ---: | ---: | ---: | ---: | ---: |
| 444000000008 | 14 | 13 | 6885 | none |
| 444000000031 | 16 | 15 | 3691 | none |

## Next bounded action

Freeze a source-semantic missing-channel diagnosis before any further model
edit.  Trace only these two already-revealed H64 shots through the current Q1274
point-add phase boundaries and localize their first divergence.  Derive at most
one general correction, commit it before revealing disjoint32, and reject any
nonce/shot/corpus-specific patch.  If no common source rule exists, retain this
model as canary-only and stop.
