# Boolean Euclid-Tag Root-Carrier Gate

Status: approved for exact support-degree and canonical-ANF falsification on
2026-08-25.

## Question

The selected constant seed makes `(g,z)` injective on exact curve support, but
field polynomial and rational decoders are interpolation-only. Does binary
representation expose a width-stable direct decoder for the bits of `T`?

This gate deliberately separates two questions that are easy to conflate:

1. Does *any* Boolean completion agree with a low-degree polynomial on support?
2. Is the simplest deterministic completion sparse enough to suggest a
   circuit?

## Completion-independent support degree

Write the little-endian bits of `(g,z)` as `2n` Boolean variables. For each
output bit of `T`, evaluate all square-free monomials of degree at most `d` on
the exact selected-seed support. Exact GF(2) column-span membership gives the
minimum possible ANF degree over every off-support completion.

Record, by field and output bit:

- the first degree whose feature span contains the target bit;
- the cumulative monomial count and feature rank there;
- the preceding feature and augmented ranks;
- the first degree at which raw monomial count reaches support size.

This is a degree lower bound only. A low-degree solution can still be dense,
and a high-degree ANF can still have a compact factored circuit.

## Canonical zero extension

Define each output bit to equal `T` on selected-seed support and zero on every
other `(g,z)` bit pattern. Apply the exact Boolean Möbius transform over the
full `2^(2n)` table. Record degree, coefficient count, and density per bit.

Zero extension is a deterministic diagnostic, not a claim about the best
reversible off-support permutation.

## Exact fields and decision

Use first-point supports at primes 31, 61, 127, 251, and 509. These require at
most 18 input bits and 262,144 truth-table rows.

`HARD_NACK_BOOLEAN_EUCLID_TAG_ROOT_CARRIER_NATURAL_ANF` if:

1. no output bit exhibits a single width-bounded degree-one family;
2. the maximum completion-independent minimum degree grows beyond two and the
   admitted systems are explained by support interpolation capacity;
3. canonical zero-extension degrees and densities grow rather than exposing a
   stable sparse template.

Otherwise hold the route for a factored-circuit follow-up. In either case this
gate does not close arbitrary factored Boolean circuits, nonlinear seeds, or a
decoder that retains the Euclidean quotient trace instead of collapsing it to
`(g,z)`.

The predeclared next grammar after a natural-ANF NACK is
`SUPPORT_TRACE_ROOT_SELECTOR`: test whether one bounded statistic retained from
the Euclidean trace resolves the GLV branch without reconstructing a cube root.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
