# Odd-Lift Prefix-Stream Gate

Status: approved for local exact falsification on 2026-08-24.

## Question

Can the surviving direct unit action

```text
(T, lambda) -> (T, T*lambda mod p)
```

be split into an ancilla-free odd multiplication modulo `R=2^n`, followed by
a single causal overwrite that folds the pseudo-Mersenne high word without
storing that word?

For every nonzero `T` in `F_p`, choose the odd signed lift

```text
m(T) = T       when T is odd
       T - p   when T is even
M(T) = m(T) mod R.
```

Then `M(T)` is odd and the map
`lambda -> w=M(T)*lambda mod R` is a permutation of an `n`-bit word.  The
remaining operation would have to overwrite `w` with
`y=T*lambda mod p`.  This experiment asks whether that correction is a
one-direction ripple whose next output bit is determined without consulting
the as-yet-unprocessed portion of `w`.

This is a circuit-bearing grammar, not an entropy claim.  Failure closes only
the one-pass prefix-stream factorization.  It does not prove that every
two-register circuit needs a third word or that nonlocal gates are impossible.

## Exact domains

For each configured odd prime `p`, with `n=ceil(log2 p)` and `R=2^n`, enumerate
every pair

```text
T in {1, ..., p-1}
lambda in {0, ..., p-1}.
```

The full nonzero-field domain is required because the affine-shell transducer
is a total permutation, not merely an oracle on sampled curve points.  The
curve-supported subset is reported separately only as diagnostic evidence.

For every row, check:

- `M(T)` is odd;
- `m(T) == T (mod p)`;
- multiplication by `M(T)` is injective over all `R` bit strings;
- recovering `lambda` with `M(T)^-1 mod R` succeeds;
- `y == T*lambda mod p`.

## Low-to-high falsifier

At bit `k`, a strictly low-to-high overwrite has already emitted
`y[0:k]` and may inspect `T` plus `w[0:k+1]`; it may not inspect
`w[k+1:n]`, retain a quotient/high word, or use a width-growing lookup.

A collision is a pair of legal rows with equal

```text
(T, w mod 2^(k+1), y mod 2^k)
```

and different bit `y[k]`.  One such collision proves that bit `k` depends on
unprocessed high information and rejects the low-to-high grammar at that
width.

## High-to-low falsifier

The symmetric high-to-low overwrite has already emitted `y[k+1:n]` and may
inspect `T` plus `w[k:n]`; it may not inspect `w[0:k]`.

A collision is a pair of legal rows with equal

```text
(T, floor(w/2^k), floor(y/2^(k+1)))
```

and different bit `y[k]`.  One collision rejects the high-to-low grammar at
that width.

## Controls and decision

The unreduced target `y=w` is the positive control and must pass both causal
tests at every bit.  Each reported collision is replayed directly from its two
input rows.  Required prime widths are 5 through at least 11 bits, with exact
row counts and canonical hashes.

Verdict:

- `ADMIT_ODD_LIFT_PREFIX_STREAM` only if one direction has no collision at all
  tested widths and the same local rule is exhibited with a scalable gate and
  cleanup formula;
- `HARD_NACK_ODD_LIFT_PREFIX_STREAM` when both directions have independently
  replayable collisions at every width of at least 6 bits;
- otherwise `INCONCLUSIVE`.

An `ADMIT` is still subject to Q<=1100, replacement T<=335738.86, exact
relative phase, zero scratch, release build, and independent evaluation.  This
gate changes no provider, nonce, fleet, queue, push, public-note, candidate, or
submission authority.
