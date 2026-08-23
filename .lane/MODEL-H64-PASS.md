# Q1274 circuit-exact CPU model: H64 closure

Date: 2026-08-23

## Verdict

`MODEL_H64_PASS`; the frozen disjoint32 may be opened only after this source
and evidence commit is pushed.

The single predeclared correction replaces exact-field squaring with the value
semantics of `product_register::square_sub`.  It reproduces the low-56 F
window, the five NAF folds, the 24-bit guarded partial-product windows, and all
outgoing carry drops.  No nonce, shot, corpus, expected-count, ping-pong,
Fiat-Shamir, or fault-accounting rule changed.

## Source and build binding

- candidate operation count: `12,935,433`;
- candidate inherited operation SHA-256:
  `61a57ce6e167b64663288ade584785b26562f61ff197f6ae0c11c85ea098ee8e`;
- corrected predictor source SHA-256:
  `3af19302b1d655cc30f89d6ef8e65ac9029d350d71e649b35bf1e2e432a53453`;
- local release binary SHA-256:
  `2426108f06e1e6c55a7423e58cf7eb0bd9580005b4df23e971c1e1278cd1331d`;
- built-in selftest receipt SHA-256:
  `807a1c4831a19be95e20d809ed17e846f995866111bc89427abb282465eaf81d`;
- SHAKE KAT, exact operation count, scalar/point KAT, and two frozen
  square-register KATs: `PASS`.

## Original H64 closure

- trusted evaluator rows: `64`;
- structural guard on every evaluator row: Q1274, 12,935,433 operations,
  ancilla zero;
- evaluator classical total: `1,032`;
- predictor classical total: `1,032`;
- per-nonce count equality: `64/64`;
- complete classical shot-set equality: `64/64`;
- evaluator-only shots: `0`;
- predictor-only shots: `0`;
- canonical 1,032-row `(nonce, shot)` set SHA-256, independently derived from
  evaluator and predictor receipts:
  `f7351ce5fabd4614e22ee74208004b6a8de9478c6bae514236d900cd621a36dc`;
- corrected predictor count receipt SHA-256:
  `80b0101b234ea45aa59eb217e8efeaf6883bd0a870f4febbd5418647cab45d70`;
- corrected predictor verbose receipt SHA-256:
  `72deedcad38d0f4aead4c911d7beb7e4ac74038d2180cc242bb60166b4988ab5`;
- frozen paired evaluator raw receipt SHA-256:
  `10ecb3139f4280bdf61b44a4416fc6ce301119f259f1e2a343ed283b7862b947`.

The CLI's optional phase estimate is not qualified by this classical H64 gate
and must not decide retention.  The unchanged full evaluator remains the
authority for classical, phase, and ancilla channels.

## Next gate

Push this commit before producing any disjoint32 outcome.  Then run the
corrected predictor first and the unchanged full evaluator second over exactly
the 32 precommitted nonces in `.lane/model-disjoint-v1.tsv`.  Require 32/32
complete classical shot-set equality, Q1274, 12,935,433 operations, and ancilla
zero on every row.  Any predictor-only shot is terminal.

