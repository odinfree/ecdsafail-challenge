# Reduced-width point-add research harness

Hypothesis credit: **Justin Drake, relayed by Oli on 2026-08-24**.

This lane tests whether discrete structural steps in the 256-bit Pareto
frontier become easier to see at 32, 64, 96, and 128 bits. It is based on the
promoted source `67524171baaf568dc3dc606f38515745f70804ff`.

## Safety boundary

- `build_circuit` keeps the fixed 256-bit secp256k1 path. The new module is not
  called from the submission builder.
- `small_width_harness` is a research binary. Its `point-add-proxy` preserves
  the four-register ABI and the promoted replay/square liveness shape, but it
  deliberately computes identity. It is not a valid challenge submission or
  a field-correct affine point add.
- No provider and no submission are used by this harness.

## Commands

Build the dedicated probe without compiling the stale legacy test surface:

```sh
cargo build --release --offline --bin small_width_harness
```

Measure the canonical widths:

```sh
./target/release/small_width_harness --canonical --mode point-add-proxy --variant chunked-approx --batches 4
./target/release/small_width_harness --canonical --mode point-add-proxy --variant chunked-exact-window --batches 4
```

Exhaustively test the boundary-carry mechanism on all 65,536 pairs of 8-bit
inputs:

```sh
./target/release/small_width_harness --width 8 --mode adder --variant chunked-approx --budget 4 --compare-window 2 --exhaustive
./target/release/small_width_harness --width 8 --mode adder --variant chunked-exact-window --budget 4 --compare-window 2 --exhaustive
```

## First receipts

The 8-bit exhaustive probe found:

| variant | peak q | emitted T | value mismatches | phase-garbage batches |
|---|---:|---:|---:|---:|
| shipped-style approximate boundary cleanup | 20 | 8 | 0 | 192 / 1,024 |
| exact window-entry-carry cleanup | 22 | 13 | 0 | 0 / 1,024 |

The exact variant retains chunk boundaries, erases them in reverse, recomputes
the carry entering the truncated top window, and feeds that carry into
`cmp_lt_phase_conditioned_with_cin`. This is a real exactness mechanism, not a
fitted width knob. Its reduced-width price is +2 peak qubits and +5 emitted
Toffolis in the 8-bit geometry.

The canonical point-add proxy produced these peak-owner observations with the
default scaled ladder budget `ceil(96*n/256)`:

| n | ripple peak | chunked peak | chunked peak owner |
|---:|---:|---:|---|
| 32 | 215 | 196 | square proxy |
| 64 | 430 | 390 | replay proxy |
| 96 | 645 | 582 | replay proxy |
| 128 | 860 | 776 | replay proxy |

The 32-bit crossover is the first useful hidden step: shrinking the replay
ladder makes the square take over, while the same scaled design remains replay
bound from 64 bits upward. That is exactly the sort of binder transition the
small-width hypothesis is intended to expose.

For future field-correct work, the provisional pseudo-Mersenne family was
checked locally with 64 Miller-Rabin rounds:

| n | modulus |
|---:|---|
| 32 | `2^32 - (2^4 + 1)` = `0xffffffef` |
| 64 | `2^64 - (2^8 + 1)` = `0xfffffffffffffeff` |
| 96 | `2^96 - (2^12 + 79)` = `0xffffffffffffffffffffefb1` |
| 128 | `2^128 - (2^16 + 157)` = `0xfffffffffffffffffffffffffffeff63` |

The proxy reports these constants as metadata only; it does not yet perform
field arithmetic.

## Next exact step

Run a per-round reachable-state census for `signed_add_wrapping_sigma` at small
widths. Check whether carry stages beyond the two existing deletions, or high
terminal stages, become fixed or affine on reachable states. Keep that
semantic invariant census separate from the identity-valued resource proxy.
