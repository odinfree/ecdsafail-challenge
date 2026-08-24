# Odd Power-of-Two Triangular Unit Action

Status: approved for local exact implementation and falsification on
2026-08-24.

## Question

The surviving joint-arithmetic grammar asks whether an odd quantum word `M`
can act on a target word `x` in place,

```text
(M, x) -> (M, M*x mod 2^n),
```

without allocating a second field-sized product register.  `M` must remain
unchanged, all work qubits must be returned clean, and the inverse must be an
explicit reversal rather than a classical inverse oracle.

This is a subprimitive for the odd-lift route.  It does not by itself implement
multiplication modulo secp256k1: the conversion between the `2^256` residue and
the pseudo-Mersenne field residue remains a separate obligation.

## Recurrence

For `i = n-2, ..., 0`, add the following value to the suffix `x[i+1:n]`:

```text
x_i * floor(M / 2) mod 2^(n-i-1).
```

Equivalently, the full word receives

```text
x_i * (M - 1) * 2^i mod 2^n.
```

The loop is descending, so every earlier update touches only positions above
its control.  Therefore `x_i` still equals the corresponding bit of the
original input when it is consumed.  Summing the updates gives

```text
x + (M - 1) * sum_(i=0)^(n-2) x_i 2^i = M*x mod 2^n.
```

The omitted top-bit term is zero modulo `2^n` because `M-1` is even.  The
inverse visits `i = 0, ..., n-2` and subtracts the same controlled suffix.

## Circuit construction

At step `i`, allocate `L=n-i-1` clean gated-source qubits and compute

```text
gated[j-1] = x_i AND M_j,  1 <= j <= L.
```

Add `gated` into `x[i+1:n]` with `add_nbit_qq_fast`, then measurement-uncompute
every gated source with its still-unchanged controls.  The inverse substitutes
`sub_nbit_qq_fast` and reverses the step order.

At width `n`, the construction predicts exactly

```text
AND Toffolis    = n(n-1)/2
adder Toffolis  = (n-1)(n-2)/2
total Toffolis  = (n-1)^2
peak qubits     = 4n-2
```

for `n >= 2`, including the two input words.  At `n=256`, that is 65,025
Toffolis and peak Q1022, below the isolated replacement budget Q1100 / T335738.86.

## Tests and falsifiers

1. Exhaust every odd `M` and every `x` at widths 1 through 9 against classical
   multiplication modulo `2^n`.
2. Require forward followed by inverse to recover both registers for the same
   exhaustive domain.
3. Run the Rust circuit through the repository simulator at reduced widths,
   checking value, preserved multiplier, zero phase, and zero non-input state.
4. Count emitted Rust operations at widths through 256.  Require exact
   `(n-1)^2` `CCX|CCZ` count and exact `4n-2` peak qubits for `n >= 2`.
5. Require the default Q1266 op stream to remain byte-identical.

Any value, inverse, phase, ancilla, resource-formula, or default-stream failure
is `HARD_NACK_ODD_POW2_TRIANGULAR_ACTION`.  If every check passes, the verdict
is `ADMIT_ODD_POW2_TRIANGULAR_SUBPRIMITIVE`; this is not a full-field candidate.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
