# Reachable carry invariant census: bounded mission order

## Ball owner and question

The single active owner is an exact reduced-width census of the signed
ping-pong walk adder.  The question is deliberately narrower than another
adder sweep:

> On the exact set of walk states reachable from every legal denominator, is
> any interior carry transition affine in the live wires often enough to
> remove a non-vanishing fraction of nonlinear stages or a material live
> carry segment?

The already-baked identities

```text
c1 = 1 xor sign
c2 = source[1]
```

are positive controls, not discoveries.  Approximate width scheduling,
nonce-tuned support, coefficient replay, history coding, stationary suffixes,
and generic chunk/layout retuning are outside this phase.

## Exact model

For modulus bit widths 5 through 10, enumerate every denominator in
`[1,p)`.  Lift an even denominator to `d-p`, then run the same alternating
integer recurrence and bit-one sign rule as the source-bound walk.  Analyze
each add in a fixed `N+3` two's-complement envelope.  The three guard bits
remove overflow and prevent a sampled width schedule from manufacturing a
false invariant.

At bit `i`, after the complement sandwich, compute

```text
a_i = source_i
b_i = target_i xor sign
c_{i+1} = majority(a_i, b_i, c_i)
delta_i = c_{i+1} xor c_i
        = (a_i xor c_i) & (b_i xor c_i).
```

Record the exact support of the live local controls and search for affine
expressions for `c_{i+1}`/`delta_i`.  The permissive search span includes the
sign, every source and target bit, and every already-materialized carry wire;
these generate the Clifford-linear span of the live ladder state at that cell.
Keep active and terminal states separate.  For every round, compute the exact smallest two's-complement
envelope that contains both operands and the signed-add result.  Cells above
that envelope are the already-known width-shrink mechanism, the last nonlinear
cell is the already-known terminal/top-skip mechanism, and rounds zero/one are
the already-specialized seed cells; none are counted as a new interior cut.
Hash the complete support/result table so every conclusion is tied to an exact
artifact.

## Tests before implementation

The harness must first prove that:

1. its carry ladder equals fixed-width modular addition;
2. exhaustive full Boolean support rejects an affine expression for AND,
   even when all affine term counts are allowed;
3. the known `c1` and `c2` identities hold on every enumerated walk state;
4. terminal filtering is explicit; and
5. the CLI receipt is byte deterministic.

## Admission and falsifier

`ADMIT` requires all of the following:

1. a new equation beyond `c1/c2` and beyond a constant-size terminal/top
   tail;
2. exact survival across increasing widths, including the largest census;
3. coverage of a non-vanishing fraction of active interior cell instances;
4. an arbitrary-width proof on the stated legal domain;
5. an implementation schedule showing the required wires are live at the
   replacement point; and
6. a production score equation predicting either a lower global Q binder or
   a material T cut at Q no greater than 1267.

`HARD_NACK` this family if the census finds only the two positive controls,
constant guard/sign-extension cells, `O(1)` late/terminal tails, or apparent
affinity caused by a support too small to persist with width.  A small-width
correlation without a proof is diagnostic only and does not authorize a Rust
source edit or trusted replay.

Provider, nonce, fleet, queue, push, public-note, protected-instance, and
submission authority remain closed.
