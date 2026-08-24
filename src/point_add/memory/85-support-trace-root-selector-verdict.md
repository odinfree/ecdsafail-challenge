# Support-Trace Root-Selector Verdict

Branch-label verdict: `ADMIT_TRACE_BRANCH_TAG_SAMPLE_ONLY`

Decoder verdict: `HARD_NACK_SUPPORT_TRACE_ROOT_SELECTOR_NATURAL_TAGS`

## Exact branch labels

The gate exhaustively searched low-bit residues of twelve natural quotient-
Euclid statistics, alone and in pairs. At the first classical point, the
minimum tags distinguishing every GLV fiber require 3, 3, 4, 8, and 10 bits at
field widths 5, 6, 7, 10, and 12. The budget grows toward the word width; a
trit is not a width-stable trace statistic.

## Deterministic secp256k1 sample

On 10,000 SHA-256-derived GLV triples, the first collision-free natural tag is
13 bits: seven low bits of quotient sum and six low bits of maximum quotient.
For the same pair, the exact collision counts at budgets 2 through 13 are:

```text
6877, 3594, 1815, 881, 434, 203, 96, 45, 18, 9, 4, 0
```

This is useful evidence that a small terminal branch label can exist. It is a
sample, not an exhaustive production certificate, and it neither constructs a
root nor prices reversible tag accumulation.

## Reconstruction still costs a word

For each tag class, the gate then asked whether

```text
T = A_tag*g + B_tag*z + C_tag
```

holds. On complete supports at widths 5, 6, 7, 8, 9, 10, and 12, the first
consistent tag budget is exactly the field width. Beyond width 5 the winning
tag is simply the full cofactor `k`, where `k*T = 1 mod p`. Retaining a complete
inverse word is not compression and still leaves inversion or an equivalent
transformation.

## Next obligation

Terminal labeling is exhausted for this natural library. The next grammar is
`TRACE_CONDITIONED_COUPLED_SEED`: feed a bounded state into the live transposed
recurrence so it changes the word before information is discarded. A valid
route must derive its seed online, keep the total resident state within Q1266,
and give exact reversible cleanup and T cost.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
