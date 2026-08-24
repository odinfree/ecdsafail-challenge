# Separable Field-Polynomial Product Census

Status: approved by the autonomous structural-cut mandate; exact local
falsifier only.

## Circuit hypothesis

On the exact curve-supported shell states, the hard product may admit

```text
T*lambda = f(T) + g(lambda)  (mod p)
```

for low-degree univariate field polynomials `f` and `g`. Such an identity would
replace the mixed-register multiply by two independent univariate maps and one
addition. It is a circuit-bearing hypothesis and is distinct from fitting
Boolean affine or quadratic features.

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Complete `pp_mul` traversal: T426844.55.
- Conservative replacement ceiling: T335738.86.

## Exact support graph

Reuse the deterministic complete support rows for p=31, 61, 127, and 251.
Build a bipartite graph with one vertex for every distinct `T`, one vertex for
every distinct `lambda`, and one edge per legal state labelled
`h=T*lambda mod p`.

An unrestricted decomposition `h=f(T)+g(lambda)` exists on the finite support
if and only if the edge equations are consistent. On every even graph cycle,
the alternating sum of the edge labels must be zero. A nonzero alternating sum
is therefore an exact, degree-independent witness against additive
separability on that support.

When the graph is consistent, solve the stricter polynomial problem over
GF(p). For degree `k`, the feature columns are

```text
1, T, ..., T^k, lambda, ..., lambda^k.
```

Use exact modular Gaussian elimination to find the minimum symmetric `k` whose
span contains the complete target vector. No random samples, real-valued fit,
tolerance, nonce, or term cutoff is allowed.

## Controls

- Re-evaluate every returned coefficient vector on every support edge.
- On a consistent graph, verify that the unrestricted vertex potentials
  satisfy every edge.
- On an inconsistent graph, emit the ordered cycle nodes, edge labels, and
  nonzero alternating residual.
- Admit a synthetic `T^2 + lambda^3` target at degree three.

## Transfer and cost gate

A production family requires a uniform symbolic identity whose degree and
nonzero coefficient count are `O(n^c)` in the bit width `n`, followed by an
explicit reversible evaluation and cleanup schedule below Q1100/T335738.86.
Degrees proportional to `p` are exponential in `n=log2(p)` and are lookup
interpolation, not a scalable arithmetic construction.

## Falsifier

Issue `HARD_NACK_SEPARABLE_FIELD_POLYNOMIAL` if any adjacent-width support has
a nonzero cycle residual, or if the minimum exact degrees do not form a
polynomial-in-width family. This closes only additive separation into
univariate field polynomials. It does not close rational functions with mixed
terms, algebraic square-root extensions, or an explicit in-place unit action.

## Residual gate

No identity earns circuit credit until its forward and inverse schedules clear
all value, phase, and ancilla residuals on the exact support.

## Authority

Local Python research only. Provider, nonce-grind, fleet, queue, push,
public-note, promotion, and submission authority remain false.
