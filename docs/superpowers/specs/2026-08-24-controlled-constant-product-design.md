# Controlled-Constant Product-Code Gate

Status: approved for local exact falsification on 2026-08-24.

## Question

Can the variable unit action be replaced by a sequence of in-place
classical-constant multipliers selected by disjoint windows of `T`?

For a partition of the 256 input bits into two or more nonempty windows, this
requires fixed nonzero field constants satisfying

```text
T = K * product_j C_j[window_j(T)] mod p
```

for every nonzero field value `T`. The circuit would then apply the
classically invertible permutation `lambda <- C_j[digit]*lambda` for each
window. It is a concrete direct-unit grammar: no quantum product is used once
the product code exists.

## Exact obstruction

Multiplicative separation implies every two-window rectangle has determinant
zero. With other windows fixed,

```text
F(00)*F(11) = F(01)*F(10) mod p.
```

Choose one bit `i` from one window, one bit `j` from a different window, and a
third context bit `k`. For

```text
b   = 2^k
A   = 2^i
B   = 2^j
T00 = b
T10 = b+A
T01 = b+B
T11 = b+A+B,
```

the required rectangle residual is

```text
T00*T11 - T10*T01 = -A*B mod p.
```

For secp256k1, choose `k` distinct from `i,j`. Every such three-bit value is
nonzero and below `p`: the largest possible sum of three powers of two is
`7*2^253`, while `p>7*2^253`. Also `A*B` is nonzero modulo the prime.
Thus every pair of input bits has a nonzero interaction, so no partition into
two independent windows can satisfy the target.

The same witness is checked exhaustively at toy prime widths by enumerating
every split of the bit positions and finding a legal context bit and nonzero
rectangle. Positive controls are generated from random fixed per-window
constants and must have zero residual on all rectangles.

## Decision

- `HARD_NACK_CONTROLLED_CONSTANT_PRODUCT_CODE` if the production symbolic
  witness passes, every toy partition is rejected, and every synthetic product
  code passes.
- Otherwise `INCONCLUSIVE`.

A single window containing all 256 bits is not a survivor: it is a `p-1` entry
lookup or the original variable unit primitive and violates the no-exponential
lookup fingerprint. This gate does not reject overlapping-window factors,
adaptive factor selection, or a genuinely arithmetic nonlocal action. No
provider, nonce, fleet, queue, push, public-note, candidate, or submission
authority is created.
