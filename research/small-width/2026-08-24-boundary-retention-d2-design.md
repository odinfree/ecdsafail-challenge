# D2 exact boundary-carry cleanup design

## Scope and verdict boundary

This gate covers only the chunked wrapping adder's inter-chunk boundary carries.
It does not establish field-correct point addition, production integration, or
score competitiveness. The two families being distinguished are:

1. **Reverse retention:** retain every inter-chunk boundary until all chunks
   have consumed their carry-in, then clean boundaries from highest to lowest.
2. **Early erase without prefix recomputation:** erase a predecessor boundary
   before a later boundary cleanup that depends on it, and substitute zero (or
   another value not reversibly derived from the preserved prefix state).

Prefix recomputation and checkpoint-pebbling schedules are outside this gate.

## Dependency and schedule

Let `b_i` be the carry out of chunk `i`, and therefore the carry in of chunk
`i+1`. Exact X-basis cleanup of `b_i` must condition the phase repair on the
same Boolean that produced `b_i`. For `i > 0`, that Boolean depends on `b_{i-1}`.
The classical HMR result for `b_{i-1}` is a random X-basis outcome and is not a
copy of the destroyed carry value.

For chunks `C_0 .. C_{k-1}`, the implementable schedule is:

1. Run chunks forward, retaining `b_0 .. b_{k-2}`.
2. After `C_{k-1}`, clean `b_{k-2}` using live `b_{k-3}` as its chunk carry-in.
3. Continue downward. Clean `b_i` using live `b_{i-1}`.
4. Clean `b_0` last with the known global carry-in zero.

At width 256 with budget 96 and comparison window 21, the current layout is
`[86, 85, 85]`. The schedule retains exactly two boundary qubits. The measured
standalone peak remains 598 qubits because the 86-qubit forward chunk ladder is
larger than either reverse-cleanup scratch region. The exact adder emits 555
Toffolis versus 295 for approximate cleanup, a delta of +260.

For a general layout with producing chunk widths `w_0 .. w_{k-2}` and window
`c`, this implementation retains `k-1` boundary qubits and adds cleanup cost

`sum_i (w_i if w_i <= c else 2*w_i - c)`

on top of the `n-1` Toffolis in the value adder. Layout admission must also
check the forward live bound `w_j - 1 + retained_before_j + outgoing_j` and the
reverse comparator scratch bound; the existing two-boundary width-256 layout
clears both bounds.

The 256-bit point-add proxy contains 1,400 such adds. It measures the same peak
of 1,550 qubits for both variants, but exact cleanup adds 364,000 emitted
Toffolis (`1,400 * 260`), from 544,582 to 908,582. Reverse retention is therefore
exact and bounded in this model, but score-negative on the available proxy.

## Small-width falsifier

Add a red-team-only variant of reverse cleanup that retains all boundaries but,
for each boundary after the first, substitutes a clean zero for its live
predecessor carry. This keeps the value path unchanged and isolates the
dependency in the phase repair.

Run it exhaustively on the smallest discovered layout with at least three
chunks. The falsifier succeeds only if it produces:

- zero value errors;
- zero dirty-ancilla batches; and
- at least one phase-garbage witness.

The correct reverse-retention schedule must clear the same input geometry. A
smallest `(width, budget, window, addend, accumulator)` witness will close the
early-erase/no-prefix-recomputation family, not any schedule that reconstructs
the missing predecessor from preserved prefix state.
