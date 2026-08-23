# Teddy numerator-residual carrier X010 dependency gate

Analyzed: 2026-08-23

Status: `DIRECT_SOURCE_ORACLE_SELECTED_FOR_ONE_CONSTRUCTION`.

## Bound inputs and determinism

The gate consumes only the complete X010 Stage-A records described in
`.lane/TEDDY-NUMERATOR-RESIDUAL-STAGE-A.md`. The analyzer is
`.lane/tools/analyze_teddy_numerator_residual.py`, SHA-256
`cb8b9014e86bc4fd530eea05fa8e23bb81aa33ebb038c968433fcf301c873964`.

Two independent direct runs produced byte-identical normalized build, 4,096
row, 64 batch, and PASS records at SHA-256
`7ce27cc97c07d8303c5c0f1f5b86c91c26377a0349225a85425b67a3b62b90b9`.
Their outer logs differ only because one includes the executable wrapper and
the other `/usr/bin/time`; their raw SHA-256 values are respectively
`c3fc02dc470a5279af5247e6c5a3f9200b254d07ebf961bb5ebe0fef67dd1b9c`
and
`48e1e480564c4a12caeb2c5ef9bde2d6959159e7541ce6359928f424088accfc`.
Both analyzer runs produce the same canonical semantic payload SHA-256:
`a1d394d6851b1f27f7bfa41168a43ec42b5943a7f15448bc932ee1255bcf9080`.
The repeat took 0.84 seconds wall time. Logs and JSON outputs remain outside
Git.

## Exact residual shape

For `delta_field = (n2_raw-n2_candidate) mod p` over all 4,096 rows:

- 127 distinct values;
- empirical Shannon entropy `4.488941556776` bits;
- information lower bound 7 bits;
- zero on 1,984 rows and nonzero on 2,112 rows;
- zero exactly iff retained walk sign 1 is zero on this corpus;
- multiplicities: one value occurs1,984 times, one occurs50 times, one occurs16
  times, 62 occur25 times, and 62 occur8 times;
- support and varying mask are both
  `fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f`;
- highest active/varying bit255 and naive fixed width256.

Production and stress halves each contain65 values, entropy
`3.989429838026`, information lower bound7, full256-bit active/varying width,
and zero multiplicity992. The complete field multiplicity-table SHA-256 is
`49dee364c7b10587d0a8bd4becb8ed2178245b7e66358103fb6d85a1e56ff84f`.

The wrapping residual has the same127-value multiplicity histogram and full
all-one256-bit support/varying masks. Field and wrapping words agree on3,065
rows and differ on1,031, so field-only equality is not used as the final
continuation gate.

## Dependency fibers

The declared retained/live-key census gives:

| key | unique keys | largest fiber | conflicting fibers | max residual pairs |
|---|---:|---:|---:|---:|
| `d` | 64 | 64 | 33 | 63 |
| `c1` | 126 | 66 | 63 | 2 |
| `n1` | 57 | 192 | 57 | 7 |
| `(d,c1)` | 4,032 | 2 | 0 | 1 |
| `(d,n1)` | 3,648 | 3 | 165 | 3 |
| `(c1,n1)` | 128 | 33 | 64 | 2 |
| `C2.c` | 126 | 66 | 63 | 2 |
| `C2.n` | 252 | 41 | 4 | 2 |
| `(C2.c,C2.n)` | 256 | 25 | 0 | 1 |
| full `R2` | 4,096 | 1 | 0 | 1 |
| full `R3` | 4,096 | 1 | 0 | 1 |

Full tuples and the near-injective `(d,c1)` key are finite-corpus facts, not
accepted production formulas. The source-derived diagnostic key
`(sign1,sign2,c1)` has252 keys, largest fiber50, and zero conflicting fibers;
dropping sign2 or sign1 creates conflicts.

## Formula order and selected construction

The frozen formula order was applied once:

1. constant fails (127 values);
2. sign-conditioned constant fails (126 distinct nonzero values);
3. affine XOR fails for every tested subset through
   `(sign1,sign2,c1)`, first inconsistent no later than row33;
4. direct arithmetic remains the first admissible source-semantic family.

Let `F_s(c,n)` be the exact emitted round-2 fused halving replay cell, `D_s`
its paired exact doubling inverse, `H` the emitted modular halving cell, and

```text
N_d(c) = c xor (sign1(d) * p)
```

the existing reversible sentinel-normalization toggle. The one selected
carrier oracle is the exact source composition

```text
residual = H(D_sign2(N_d(c1), F_sign2(c1, 0))).
```

It uses only the zero carrier, live `c1`, retained denominator, the existing
one shared sign and one normalization flag. It retains no `c1`/`n1`
predecessor, sign transcript, or second word. Its declared inverse is the
literal paired-source reverse:

```text
H^-1; F_sign2(N_d(c1), .); D_sign2(c1, .),
```

with sign1/sign2 recomputed and cleared between cells. Thus cleanup does not
require unavailable predecessor history if the emitted primitives compose as
declared.

The host simplification

```text
(-1)^sign2 * (c1 - N_d(c1)) / 2 mod p
```

matches3,980/4,096 rows. The116 remaining rows are exactly108 `+2^53` and8
`-2^53` source-fold corrections. This KILLs the simplified arithmetic formula;
the selected oracle deliberately composes the exact source cells so those
truncated-fold branches remain inside the falsifier. The correction-value
table SHA-256 is
`47f4f02c0e1d802bd769d8c360beb972dba970180773d21b7dcaa0b7b5b7b770`.

## Construction boundary

This gate authorizes exactly one opt-in Stage-B construction of the expression
above, followed by modular addition of the carrier into the candidate round-2
numerator and immediate inverse uncompute. Static base width is Q1284; the
source replay transient budget permits at most86 further qubits, hard cap
Q1370. The correction add, emitted/executed T, stochastic-event binding,
complete per-round value/relative-phase parity, carrier cleanup, and all X009
gates remain unproved and must be measured.

KILL immediately if the exact expression differs on the first frozen row, the
modular correction or inverse needs predecessor history, Q exceeds1370, the
carrier is dirty, or relative phase/new stochastic debt fails. There is no
lookup fallback, second construction, round4, full-circuit claim, provider,
range, hunt, submission, or public action.
