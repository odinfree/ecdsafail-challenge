# Support-Trace Root-Selector Gate

Status: approved for exact natural-tag search and deterministic production
sampling on 2026-08-25.

## Question

The Euclidean walk sees the complete multiplier `T` before the transposed row
action collapses it into `(g,z)`. Can one bounded statistic retained from that
trace select the correct GLV root and also make `T` cheap to reconstruct?

A branch label and a root carrier are separate obligations. A tag may
distinguish the three members of each fixed-`z` fiber while carrying almost no
information about the full output word.

## Natural trace-statistic library

For the canonical positive quotient trace, measure:

```text
length, sum, alternating sum, first, last, penultimate,
sum of quotient popcounts, maximum, position-weighted sum, quotient xor,
r, k
```

where the orientation-one extended-Euclid cofactors satisfy

```text
k*T-r*p = 1.
```

A tag is the low `b` bits of one statistic or the concatenation of low-bit
residues from two statistics. Search total tag budgets in increasing order and
use a deterministic statistic/allocation ordering.

## Two gates

### GLV branch selection

On every fixed-`z` support fiber, all `T` values must have distinct tags. Run
this exactly at the first classical point for `p = 31, 61, 127, 1021, 4093`,
the tested fields congruent to one modulo three.

Also generate 10,000 deterministic secp256k1 GLV triples. Candidate `X` values
come from SHA-256 of the sample index and are accepted exactly when
`X^3+7` is a nonzero quadratic residue. Use the standard generator X as the
classical coordinate and hash every accepted X into the sample receipt. Search
natural tags through 32 total bits.

Zero sampled collisions admits only
`ADMIT_TRACE_BRANCH_TAG_SAMPLE_ONLY`; it is neither an exhaustive production
certificate nor a reversible-cost result.

### Tag-conditioned affine reconstruction

For every tag class, test exact field-rank consistency of

```text
T = A_tag*g + B_tag*z + C_tag.
```

Search all one- and two-statistic tags through the field width on complete
first-point supports at widths 5, 6, 7, 8, 9, 10, and 12. If the first
consistent decoder requires at least the complete field width and is explained
by retaining full `k = T^-1`, classify it as word retention, not compression.

## Decision

`HARD_NACK_SUPPORT_TRACE_ROOT_SELECTOR_NATURAL_TAGS` if:

1. exact branch-selector budgets grow across the GLV widths;
2. the deterministic production sample needs more than a trit and remains
   explicitly sample-only;
3. exact tag-conditioned affine reconstruction first succeeds only at a
   full-word tag budget.

This closes only the stated natural low-bit statistic library and affine
postdecoders. It does not close nonlinear trace accumulators, arbitrary
factored decoders, or a trace recurrence that transforms the live word before
the terminal state.

The next grammar after a NACK is `TRACE_CONDITIONED_COUPLED_SEED`: use a bounded
trace state inside the transposed recurrence, rather than retaining a terminal
label and trying to decode afterward.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
