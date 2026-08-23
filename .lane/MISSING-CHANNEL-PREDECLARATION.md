# Predeclaration: Q1274 two-shot missing-channel audit

Date: 2026-08-23

## Frozen failure

- exact-port commit: `5aff017`;
- candidate operations: `12,935,433`;
- predictor source SHA-256:
  `aee0f0d03622a293a62e7d180d63eb3d426ea30ff3f694c42923b3ccbf4e1851`;
- H64 evaluator/model totals: `1032/1030`;
- evaluator-only shots: nonce `444000000008` shot `6885`, nonce
  `444000000031` shot `3691`;
- predictor-only shots: none;
- blinded disjoint32: still unopened.

## Question

Does one source-semantic mechanism introduced by the Q1274 peak/ladder geometry
explain both evaluator-only shots without a nonce, shot, expected-count, or
fixture special case?

## Allowed diagnostics

1. Rebuild the two exact nonce streams and require Q1274, 12,935,433
   operations, and the already-frozen per-nonce operation SHA.
2. Use the existing source phase transitions from the unchanged ping-pong
   builder to bind point-add operation boundaries.  Temporary trusted simulator
   instrumentation may emit only the two coordinate registers at those
   boundaries for the selected existing shots; it must not alter the operation
   stream, Fiat-Shamir seed, RNG consumption, simulation, or final channel
   accounting.
3. Emit the corresponding already-frozen predictor phase trace for the same
   shots and identify the first unequal phase boundary.
4. Exercise the first divergent subsystem directly on the exact boundary input
   pair when a focused reversible/value selftest exists.
5. Derive at most one general source-semantic correction.  It must implement
   the actual value geometry of the current source and remain parameterized for
   later CPU/CUDA ports.

No model-semantic edit is allowed until the exact first-divergence evidence is
frozen in a durable diagnosis commit.

## Gates

- both shots have a reproducible first divergent source phase;
- the common mechanism is named, or the audit closes terminally with no common
  bounded rule;
- temporary instrumentation is removed byte-for-byte before the diagnosis
  commit;
- one proposed correction at most;
- after a correction commit, H64 must match 64/64 complete sets before the
  precommitted disjoint32 may be evaluated;
- disjoint32 then requires 32/32 complete-set equality.

Any predictor-only shot blocks scanning.  Underprediction remains canary-only.
No provider, range, hunt, submission, incumbent, or ecdsa-ops action is
authorized.  Generated streams, binaries, phase traces, and logs stay outside
Git.
