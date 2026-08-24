# Coupled Transposed Seed Gate

Status: approved for local exact algebra and bounded-degree falsification on
2026-08-24.

## Necessary coupled seed

Fix the continued-fraction orientation so the online row matrix is

```text
B_T = [[-r_T, T], [k_T, -p]],
k_T*T-r_T*p = 1.
```

Generalize the second row seed from `(lambda,h(T))` to

```text
(lambda, s(T)*lambda+h(T)).
```

Its output is

```text
g = (-r_T+k_T*s(T))*lambda + k_T*h(T)
z = T*lambda.
```

For the fixed-`T` lines to be pairwise disjoint, they must share one direction
ratio `c`. This is possible only when

```text
-r_T+k_T*s(T) = c*T,
s(T) = k_T^-1*(r_T+c*T) = T*r_T+c*T^2 mod p.
```

Distinct intercepts are then mandatory. The simplest choice is

```text
c = 0,
s(T) = T*r_T,
h(T) = T^2,
```

which makes the online output exactly `(g,z)=(T,T*lambda)`.

This is an exact algebraic construction only if its coupled seed can actually
be produced and erased. Computing `T*r_T*lambda` by a generic variable
multiplier would assume the primitive the construction is meant to replace.

## First falsifier

The bounded-degree seed grammar asks whether `T*r_T+c*T^2` has a fixed-degree,
sparse field-polynomial description. For every field:

1. choose the canonical or alternate-final-one quotient expansion so the
   normalized orientation is always `+1`;
2. exhaustively verify the ideal coupled seed maps every `(T,lambda)` to
   `(T,T*lambda)`;
3. interpolate the unique polynomial of degree below `p` representing
   `T*r_T`, totalized to zero at `T=0`;
4. report its exact degree and nonzero coefficient count;
5. prove adding `c*T^2` can change only the quadratic coefficient, so it
   cannot remove any degree above two.

## Decision

- `ADMIT_IDEAL_COUPLED_SEED_IDENTITY_ONLY` if the exact output identity passes.
- `HARD_NACK_BOUNDED_DEGREE_COUPLED_SEED` if the interpolant degree grows as
  `p-1` at adjacent widths. This closes literal bounded-degree field-polynomial
  seed generation, not all circuits for the cofactor function.

The next grammar is `ONLINE_COFACTOR_PRODUCT_RECURRENCE`: produce the exact
`r_T*lambda` cancellation while Euclid generates `r_T`, without storing a
linear quotient transcript or invoking a separate variable multiplication.
Its first artifact must state a reversible recurrence and complete live-state
ledger before production Rust.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
