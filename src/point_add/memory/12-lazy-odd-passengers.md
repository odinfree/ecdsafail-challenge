# Lazy odd passengers at Q1265

Status: **local structural prototype; not an admitted candidate**.

This experiment is bound to official source
`522d00296ab014b0f4d128915b53851516f17f4d`.  It keeps the two proven-one
low bits of the ping-pong value registers implicit across the interleaved
replay/walk region instead of restoring their physical wires at every replay
boundary.  The feature is opt-in with `SUB4_PP_LAZY_ODD_RESTORE=1`; the default
path is unchanged.

## Why the transform is exact

After each ping-pong halving round both value registers are odd.  For rounds
two and later, the wrapped signed add consumes the two low-bit values
algebraically.  Its target low bit is known zero immediately before the
halving rotation, so the implementation materializes a temporary clean wire
only for that rotation and releases it after the exact low-two-bit recurrence
proves the new target low bit is one.  The inverse traversal performs the
reverse sequence.  `NO_QUBIT` marks implicit slots so accidental physical use
fails closed.

`SUB4_PP_LAZY_ODD_SELFTEST=1 cargo run --release --bin build_circuit` first
compares explicit and implicit forward register state, sign, phase, and
ancillas on 64 odd input pairs.  It covers even and odd rounds with both the
split and unsplit wrapped add forced.  It then exercises an explicit and
implicit forward/reverse roundtrip and checks the returned registers, global
phase, every non-register ancilla, and that the implicit construction has a
lower peak.  This passed locally.

The opt-in path rejects `SUB4_PP_LOAN_ONE=1` immediately with an explicit
incompatibility message.  That diagnostic mode does not provide the two
proven-one low-wire loans required by this transform.

## Bound artifacts and measurements

Exact build parameters are `SUB4_PP_ROUNDS=694` and
`SUB4_PP_ROUNDS_MUL=693`.

| path | Q | emitted ops | compressed bytes | SHA-256 |
|---|---:|---:|---:|---|
| feature disabled | 1266 | 12,553,305 | 45,725,252 | `a4995dc4be4b7b314853d379941141b3b5753110412c07e8a2bc5d097d218ed1` |
| lazy odd feature | 1265 | 12,548,730 | 45,628,312 | `482b4f2b6f62973b0cdc20139006ae57583a9c230d329bace751a516a34c2a26` |

The disabled artifact is byte-identical to the exact pre-change reference,
which establishes that the environment gate is inert when absent.

Four independent 64-lane profile seeds all reported zero classical
mismatches, zero phase, and zero dirty qubits.  The executed-Toffoli estimates
were `908680.36`, `908775.98`, `908598.69`, and `908641.59`; the emitted CCX
count was invariant at `951726`.  At the current official score
`1,153,834,932`, the rounded diagnostic score range is
`1,149,377,735..1,149,601,640`, a projected lead of
`4,457,197..4,233,292`.

The inherited tail nonce is not clean for the new artifact.  The untouched
trusted evaluator over all 9,024 shots reported 28 classical mismatches,
17 phase-garbage batches, and zero ancilla-garbage batches.  This is the
expected nonce negative control.  Because a changed artifact also changes the
Fiat-Shamir samples, this run alone cannot separate ordinary nonce-lottery
failures from a transform-specific fault; it is not a submission result.

## Rejected attempts to reach Q1264

- Cutting every competing replay ladder reached Q1264 but raised diagnostic T
  to `909708.38`; rounded score `1,149,870,912`, about 390,712 worse than the
  Q1265 route on the corresponding profile.
- Porting the source-host role into an exact Cuccaro chain reached Q1264 but
  added 1,326 executed Toffoli activations versus a break-even budget of about
  719.  Diagnostic T was `910126.70`, rounded score `1,150,400,528`.

Both Q1264 variants were removed.  Reopen only with a materially cheaper
all-round ladder representation or a host port below the measured activation
budget.

## Admission path

1. Finish the source-bound P3/P4 prefilter gates and obtain a classically clean
   nonce receipt.
2. Rebuild this exact branch with that nonce and bind the resulting artifact
   hash.
3. Run the untouched 9,024-shot trusted evaluator and require 0 classical,
   0 phase, and 0 ancilla failures.
4. Reproduce independently from a clean checkout, refresh the live frontier,
   and submit only if the exact rounded score still wins strictly.

Until all four steps clear, this work is structural evidence only.
