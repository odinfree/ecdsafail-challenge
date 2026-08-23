# E-004 boundary-carry audit

Date: 2026-08-23 (Europe/Zurich)

## Verdict

The final-y `LSBS 53 -> 54` experiment failed because it moved the truncation
boundary; it did not preserve the boundary state. The exact repair is small and
fits the Q1272 saddle. Preserve one logical borrow bit, use it to decrement the
entire 203-bit high suffix, then uncompute it from the unchanged low result.

The source implementation is opt-in only:

```text
TLM_FINAL_Y_SUB_BOUNDARY_CARRY=1
```

It applies only while `circ.phase == "tlm_coord_y_sub_final"`. Protected
defaults and the held E-001c stream reproduce byte-for-byte with the switch
off. This audit did not hunt, use a provider, submit, or edit the active Q1272
worktree.

## Fresh frontier and exchange rate

The live benchmark was reopened before pricing:

```text
source: bdf4845
score:  1,170,580,266
Q/T:    1278 / 915947
```

At Q1272 a strict beat requires:

```text
maximum rounded T = floor((1,170,580,266 - 1) / 1272) = 920267
maximum product   = 1,170,579,624
```

The `921139` ceiling in the original E-004 note belongs to an older frontier
and must not be reused.

## Exact state derivation

Let:

```text
w = 53
f = 2^32 + 977 = 0x1000003d1
z = low_w(y - anc*f) mod 2^w
K = 2^w - f = 0x1ffffefffffc2f
```

`sub_f_window` computes `z` but deliberately discards the borrow at bit 53.
The missing Boolean is exactly:

```text
b = anc AND (z >= K)
```

Proof: with `anc=0`, no subtraction or borrow occurs. With `anc=1`, an
original low word at least `f` produces `z` in `[0, K-1]`; an original low word
below `f` wraps and produces `z` in `[K, 2^53-1]`. These intervals are disjoint
and exhaustive. The post-window low word and `anc` therefore retain enough
information to recompute the discarded borrow exactly.

The semantic state is one Boolean. No long-lived tape bit is required. The
measured construction materializes `b` in one clean transient qubit, applies a
controlled decrement to `y[53..256]`, then recomputes the same predicate and
returns `b` to `|0>`. Its multi-control and increment decompositions use at
most five temporary scratch qubits at once. A direct no-predicate-qubit
synthesis is possible in principle, but offers no Q benefit at this local
phase and would complicate the gate path.

Widening to 54 failed for the same algebraic reason: it updated bit 53, then
discarded the same Boolean at bit 54. Any finite-width extension can repeat
that failure. The correction must reach the complete high suffix.

## Opt-in composition

After the existing low-window subtraction and before
`controlled_add_carry_msbs_conditional`:

1. Toggle a clean qubit `b` using the controlled threshold predicate
   `anc && y[0..53] >= K`.
2. Apply `X` to `y[53..256]`.
3. Apply the existing `cinc_khattar_gidney(y[53..256], b)`.
4. Apply `X` to `y[53..256]` again. Steps 2--4 are a controlled decrement,
   including arbitrary zero-ripple and wraparound.
5. Recompute the threshold predicate into `b` and free it cleanly.

The threshold is synthesized as seven disjoint terms: one for each zero bit
of `K` at positions `4,6,7,8,9,32`, plus equality. Adding `anc` as a control to
each term avoids a second predicate qubit.

## Byte reproduction and measurements

Release binaries were rebuilt from a clean target before artifact generation.

| stream | operations | SHA-256 | Q | fixed64 T | channels |
|---|---:|---|---:|---:|---|
| protected default | 12,901,167 | `ecc3d9f0bb1dd4e68e6d337e39c4cdb66cfbfe83928a81fec28e22797fca4cfd` | 1272 | not repeated | opt-out byte match |
| held E-001c | 12,939,336 | `d4ecab6dd80d044d0a28ae456a9106992d2b3aae070d80cfa0dde3d24400f920` | 1272 | 916117.12 | `0/0/0` |
| held + boundary carry | 12,943,345 | `4618d4af86c23c06cc72fef26f8a8e5986c7a9de5f804891541a8ce6eb189f37` | 1272 | 918043.41 | `0/0/0` |

The same-seed delta is +4,009 operations, +1,927 emitted Toffolis, and
+1,926.29 executed T. The unchanged full evaluator measured exact candidate T
918104.700, rounded 918105, product 1,167,829,560. This is 2,750,706 below the
refreshed frontier and leaves 2,162 rounded-T headroom at Q1272. The prior held
stream measured exact full T916182.965865331, so the candidate's full-run delta
is +1,921.734.

This is an economic gate, not a submission score. The same unchanged full
9,024-shot evaluator returned `11/12/0`, first classical mismatch at shot 2582.
The architecture remains a dirty held route; no score file or submission claim
follows. Ancilla stayed clean.

## Co-binder trace

The boundary repair is off the global plateau. Its phase-local peak stays
Q1026. The four Q1272 co-binders are unchanged:

| phase | Q | held fixed64 T | status |
|---|---:|---:|---|
| divide replay | 1272 | 263184.47 | unchanged |
| product-register square | 1272 | 58720.72 | unchanged |
| multiply replay | 1272 | 24273.28 | unchanged |
| multiply walkback | 1272 | 308320.66 | unchanged |

No additional co-binder cut is needed for this composition. The correction's
focused primitive peaks at Q307.

## Focused primitive gate

Run:

```text
TLM_FINAL_Y_SUB_BOUNDARY_SELFTEST=1 target/release/build_circuit
```

The fixed 13-case set covers:

- control off at zero, maximum word, and `f-1`;
- the predicate transition at original low words `f-1`, `f`, and `f+1`;
- post-window `K-1`, `K`, and maximum boundary states;
- high-suffix decrement from zero, one, two, and a distant bit-100 singleton;
- complete 256-bit wraparound.

Measured result:

```text
TLM_FINAL_Y_SUB_BOUNDARY_SELFTEST_OK cases=13 emitted_t=1984 peak_q=307
value mismatches: 0
phase mask:       0
dirty ancillas:   0
```

The 1,984 count includes the low-window subtraction used by the focused test;
the full-circuit incremental emitted price is the 1,927 figure above.

## Smallest decisive fixed-shot falsifier

Use exactly two pinned inputs from held artifact `d4ecab6d...`, nonce
`444000000032`:

1. shot 7997, the carry-positive lane: exact through multiply restore, then
   baseline final y is `expected + 2^53`;
2. shot 7996, the adjacent clean carry-negative control.

Derive both target/offset pairs from the held artifact, not from the changed
candidate SHA. Replay all preceding evaluator batches so measurement RNG state
is unchanged. The first gate passes only if shot 7997 becomes classically
exact at final y, shot 7996 stays exact, x stays exact through rsub, and both
lanes finish phase/ancilla `0/0`. Any `2^k` residual, control regression, or
phase/ancilla fault kills the composition before H64.

If that two-lane gate passes, run the focused selftest above, the inherited
full evaluator, and the already frozen complete H64 block. Do not search this
stream until those gates and a stream-bound predictor all close.
