# Q1273 source-specific conditional-phase predictor predeclaration

Status: predeclared before any predictor, schedule, fixture, or circuit-source
edit in this lane.

## Frozen source and inherited result

- branch base and circuit source:
  `093d85d64de87aa5006a94868172f642daacf136`;
- source tree: `f6fd9d8b151a84fd886835ff3a818d3c1c9ef072`;
- exact emitted stream: `12,933,805` operations, SHA-256
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- trusted inherited nonce: `100000045835813`;
- trusted full-9,024 result: Q1273, average executed Toffoli
  `917,103.815`, classical/phase/ancilla `12/12/0`;
- strict live score ceiling: rounded T `<= 917,245`;
- receipt:
  `/Users/olifreuler/ecdsa-ops/q1273-redescent-093d85d-full9024/RECEIPT.md`,
  SHA-256
  `f65aad34d8392d2c273349aa06f50beb8a8cc0a01c04892e801455081840ce17`;
- trusted evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- trusted evaluator binary SHA-256:
  `a082c8449897081a0822fcf8866346a90cd4d37dfcdd3660ab64768ffb542436`;
- trusted result-row SHA-256:
  `dc515b01994fc32eeba8485990910972bf0bbf908ff69092515a6973d718bd64`.

This is a new source-specific derivation. No Q1274 schedule, phase fixture, or
oracle result is admissible as Q1273 evidence. Shared evaluator architecture
may be ported only after every source ordinal, operation family, stream
identity, and fixture row is regenerated from this exact source.

## Exact modeled contract

The predictor may claim only the complete conditional set

`clean_phase_mask = exact_evaluator_phase_mask & ~exact_classical_mask`.

A clean survivor exists only under the conjunction

`exact_classical_mask == 0 && clean_phase_mask == 0`.

Raw phase behavior on classically dirty shots is outside the claim. The
predictor must report the complete sorted clean-phase shot set and the complete
exact classical set/count for every declared nonce; count-only parity is
insufficient. CPU is the only implementation target. No CUDA phase claim is
authorized.

## Independent source oracle and schedule derivation

Before predictor implementation, this lane will reproduce the exact stream
from the frozen source and derive a Q1273-only ordered R/Hmr schedule from that
stream and its source-family trace. The schedule must bind every modeled
predicate to an exact operation/R-Hmr ordinal, require monotonic in-range
consumption, and consume the complete declared source-family sequence.

The independent oracle will use the trusted full evaluator semantics in a
two-pass form: patch the final 96 cancelling nonce-tail X operations before
both Fiat-Shamir hashing and simulation, evaluate all 9,024 shots, and record
complete sorted exact classical and conditional-phase sets. A label-only
nonce change with an unpatched tail is a mandatory negative. Predictor and
oracle must not share the generated phase schedule or predicate code.

## Frozen validation corpus

The inherited nonce is always evaluated first. The disjoint corpus is frozen
before any oracle row is revealed:

`nonce[i] = 730000000000 + i * 10000103`, for `0 <= i < 16`.

Its canonical newline-delimited nonce-list SHA-256 is
`95cdff3d994ed74866e87aff7822d8d8aa8091e74ed5a2842c2fca6732afd3b0`.
All 17 rows are mandatory; the gate stops on the first mismatch. Any predictor
change restarts the inherited row and the complete D16 corpus from the
beginning. Fixtures may be committed only after the oracle has generated them
and the predictor has independently matched every complete sorted set and
per-set SHA-256.

## Frozen gates

1. A clean source rebuild reproduces the exact operation count and SHA-256
   before any semantic derivation.
2. The inherited row reproduces the trusted `12/12/0` aggregate and predictor
   versus oracle equality for complete classical and clean-phase shot sets.
3. D16 passes `16/16` complete-set equality in declared order, with immutable
   nonce-list, ledger, per-set, and combined-output SHA-256 values.
4. Wrong magic, wrong operation count, same-count/wrong-SHA, wrong predictor
   digest, wrong source schedule, and unpatched nonce tail fail closed before a
   parity claim.
5. Repeated runs over the same source, stream, and nonce list are byte-identical
   in output order and hash.
6. The source-specific classical predictor supplied by the balanced Q1273 lane
   must remain unchanged-compatible on its full declared corpus. Until that
   packet arrives and passes identity plus per-shot equality, this lane remains
   validation HOLD even if phase parity is exact.
7. Existing production/self-check evidence stays unchanged; no circuit
   optimization or score claim is introduced by this predictor-only lane.

Any source/stream ambiguity, missing shot, aggregate-only match, schedule
under-consumption, classical incompatibility, nondeterminism, or identity
bypass kills the packet until corrected and all gates restart. No provider,
remote host, range scan, hunt, submission, recovered-wave input, or CUDA phase
work is authorized.
