# Lazy odd passengers and round-zero a0 elision at Q1264

Status: **source-baked structural candidate; not admission-validated**.

This experiment is bound to official source
`522d00296ab014b0f4d128915b53851516f17f4d` and the sealed Q1265 parent
`30bc8cb79b63f89ca08610c85f24d13f2f41b4df`.  It keeps the two proven-one
low bits of the ping-pong value registers implicit across the interleaved
replay/walk region instead of restoring their physical wires at every replay
boundary.  It then removes the retained fused-round-zero `a0` tape wire and
reconstructs it immediately before inverse round zero.  The reviewed 694/693
geometry, lazy restoration, and `a0` elision are now the zero-environment
source defaults required by the official benchmark.

`SUB4_PP_ELIDE_ROUND0_A0=0` restores the Q1265 retained-tape path.
`SUB4_PP_LAZY_ODD_RESTORE=0 SUB4_PP_ELIDE_ROUND0_A0=0` restores the exact
pre-change Q1266 control path.

Reduced-width autoresearch direction suggested by Justin Drake.

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

The default lazy path rejects `SUB4_PP_LOAN_ONE=1` immediately with an explicit
incompatibility message.  That diagnostic mode does not provide the two
proven-one low-wire loans required by this transform.

## Why the round-zero tape elision is exact for this stream

The baked sparse forward cell starts `v[255]` at zero.  Its pseudo-Mersenne
controls vanish above bit 32, and its 52-bit truncated carry reaches only bit
53.  The complement sandwich therefore cancels at bit 255 before the cell's
final `CX(a0, v[255])`, making `v[255] = a0` for every 256-bit denominator.
The implementation clears and releases `a0`, stores `NO_QUBIT` in tape slot
zero, and allocates/copies `v[255]` as the first inverse-round-zero action.
Both round-zero replay cells are sign-independent, so they never consume the
sentinel.

This identity is specific to the baked sparse/truncated stream.  The ideal
dense/full-carry map has exactly `2,147,484,136 = 2^31 + 488` exceptions in
two strided arms: `a = 3 (mod 4)` from `3` through `0x1000003cf`, and
`a = 0 (mod 4)` from
`0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffdfffff860`
through
`0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2c`.
The dedicated selftest proves those dense-control boundaries while requiring
zero relation exceptions on the baked sparse cell.  Elision therefore fails
closed when the dense, separate-lift, or full-width carry variants are chosen.

`SUB4_PP_ROUND0_A0_SELFTEST=1 cargo run --release --bin build_circuit` runs
retained-versus-elided direct round-zero and complete 694-round shrink/regrow
differentials over the directed boundaries plus deterministic random lanes.
It checks phase and every non-register ancilla, then runs both complete Divide
and Multiply components.  The final local receipt was Q1264 for both
directions with zero classical, phase, or dirty failures.

## Bound artifacts and measurements

The exact build uses the baked divide/multiply round defaults `694/693`.

| path | Q | emitted ops | compressed bytes | SHA-256 |
|---|---:|---:|---:|---|
| both optimizations disabled | 1266 | 12,553,305 | 45,725,252 | `a4995dc4be4b7b314853d379941141b3b5753110412c07e8a2bc5d097d218ed1` |
| `SUB4_PP_ELIDE_ROUND0_A0=0` | 1265 | 12,548,730 | 45,628,312 | `482b4f2b6f62973b0cdc20139006ae57583a9c230d329bace751a516a34c2a26` |
| zero environment (both baked) | 1264 | 12,548,734 | 45,649,871 | `f49c0d5d16bf41f0cb7a3eac0a74e5a097082f285cd3e0577d3023baa552c292` |

The double opt-out artifact is byte-identical to the exact pre-change 694/693
reference.  The `a0` opt-out is byte-identical to the reviewed Q1265 parent.
The zero-environment Q1264 artifact differs by exactly four CX operations and
no CCX/CCZ operations: clear and reconstruct `a0` for each of the two
ping-pong traversals in the affine point-add.

Five paired 64-lane profile seeds all reported zero classical mismatches, zero
phase, and zero dirty qubits.  Baseline and elided executed-Toffoli estimates
were bit-exact for every pair: `908680.36`, `908775.98`, `908598.69`,
`908567.73`, and `908661.33`; the emitted CCX count was invariant at `951726`.
Every phase stayed at or below Q1264.  The two binders were
`pp_div_replay=1264` and `pp_mul_walkback=1264`.  At the current official
score `1,153,834,932`, the rounded diagnostic score range is
`1,148,429,952..1,148,692,864`, a projected lead of
`5,404,980..5,142,068`.

The inherited tail nonce is not clean for the new artifact.  The untouched
trusted evaluator over all 9,024 shots reported 23 classical mismatches,
13 phase-garbage batches, and zero ancilla-garbage batches.  This is the
expected nonce negative control.  Because a changed artifact also changes the
Fiat-Shamir samples, this run alone cannot separate ordinary nonce-lottery
failures from a transform-specific fault; it is not a submission result.

## Superseded attempts to reach Q1264

- Cutting every competing replay ladder reached Q1264 but raised diagnostic T
  to `909708.38`; rounded score `1,149,870,912`, about 390,712 worse than the
  Q1265 route on the corresponding profile.
- Porting the source-host role into an exact Cuccaro chain reached Q1264 but
  added 1,326 executed Toffoli activations versus a break-even budget of about
  719.  Diagnostic T was `910126.70`, rounded score `1,150,400,528`.

Both variants were removed.  The round-zero tape elision supersedes them by
reaching Q1264 with zero executed-Toffoli delta.

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
