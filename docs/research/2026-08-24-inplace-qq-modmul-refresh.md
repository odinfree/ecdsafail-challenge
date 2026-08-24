# 2024-2026 primary-source refresh: in-place quantum-quantum modular multiplication

Status: `HARD_NACK_PRIMARY_REFRESH` for a direct `pp_mul` replacement.

## Decision

No published or first-party implemented primitive found in the 2024-2026
refresh satisfies the affine-shell replacement contract:

```text
exact quantum interface      = two 256-bit field registers only
persistent third field words = 0
linear history bits          = 0
Q_component                  <= 1100
T_exec + companions          <= 335738.86 executed Toffoli
```

The genuinely new lead is Kahanamoku-Meyer and Yao's ancilla-free Fourier
multiply-accumulate. It materially changes the multiplication kernel, but its
published quantum-quantum interface retains both multiplicands and a distinct
output register. Its modular construction is approximate, and its in-place
construction covers only multiplication by a classical constant. It therefore
does not implement the required destructive map on `(T, lambda)`.

The 2025 optimized folding Barrett reducer and the 2025 Qrisp Kaliski inverter
both fail the Q gate independently of their time cost. Measurement-based
uncomputation improves one-bit modular-adder cleanup but explicitly leaves
modular multiplication to future work. The 2025 DFT multiplier is an in-place
permutation only for a classically fixed multiplier.

This is a hard NACK on transplanting the named primary artifacts. It is not a
lower bound against a bespoke two-register affine-shell transducer.

## Campaign binding

This review uses the source and cost equation recorded in
`docs/superpowers/specs/2026-08-24-affine-shell-transducer-design.md`:

- research base commit `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f`;
- promoted tree `eab2326ce33549eceeb5c10aa64eae33f148b0ac`;
- complete removed traversal `T_complete_mul = 426845.00`;
- ten-percent replacement ceiling `335738.86` executed Toffoli;
- component width ceiling Q1100;
- exactly two quantum field registers at the transducer ABI.

The symbol `T_exec` below means the challenge's executed-Toffoli metric. A
paper's Clifford+T `T-count` is reported under that explicit name and is not
silently equated with `T_exec`.

## Search scope and duplication boundary

The refresh queried the official arXiv corpus for `modular multiplication`,
`modular inversion`, and `quantum multiplication`, restricted to primary
papers submitted from 2024 through 2026, and followed only paper-hosted or
author-maintained source links. The last query was run on 2026-08-24.

The following already-audited sources were used as the duplication boundary,
not repeated as new findings:

- Ragavan and Vaikuntanathan's generic inversion-by-adjoint reduction and
  four-register inverse-carrying workaround, recorded in
  `src/point_add/memory/18-inplace-modmul-primary-research.md` on the historical
  research branch;
- Luo et al.'s April and July 2026 register-shared EEA constructions, already
  source-bound and costed in
  `src/point_add/memory/22-affine-multiply-cut-verdict.md`.

No August 2026 arXiv result newer than Luo et al. appeared in the primary
queries.

## Primary artifact ledger

| Artifact | Exact binding | What is actually provided | Campaign verdict |
|---|---|---|---|
| Kahanamoku-Meyer and Yao, [*Fast quantum integer multiplication with zero ancillas*](https://arxiv.org/abs/2403.18006v4) | arXiv `2403.18006v4`, 2024-11-14; PDF SHA256 `5700b36dbb02c5aaabe7bf79a885f5cf29113296e0c1c7d23eaaf8c64847baee`; [estimator source](https://github.com/GregDMeyer/mult_cost_estimation/tree/f5fcb5c246e7330e621e5d8f3b3d828599abcfea) tag `v0.0.1`, commit `f5fcb5c246e7330e621e5d8f3b3d828599abcfea`, Zenodo [10.5281/zenodo.10871110](https://doi.org/10.5281/zenodo.10871110) | Ancilla-free exact integer multiply-accumulate and subquadratic phase-product decompositions; approximate modular output; in-place modular multiplication only for a classical constant | `HARD_NACK_INTERFACE_EXACTNESS` |
| Luongo, Miti, Narasimhachar, and Sireesh, [*Measurement-based uncomputation of quantum circuits for modular arithmetic*](https://arxiv.org/abs/2407.20167v1) | arXiv `2407.20167v1`, 2024-07-29; PDF SHA256 `c5b152e5dbfdbc767e49edaec45f3550e623fdefa269fdabed0ab578d7a392f0`; [symbolic source](https://github.com/AdithyaSireesh/mbu-arithmetic/tree/ee0643e4ca6de422383877bf57d289c045a86dcd) commit `ee0643e4ca6de422383877bf57d289c045a86dcd` | Formal one-qubit MBU and 10-25% expected savings for modular adders; modular multiplication explicitly future work | `HARD_NACK_NOT_A_MULTIPLIER` |
| Polimeni and Seidel, [*End-to-end compilable implementation of quantum elliptic curve logarithm in Qrisp*](https://arxiv.org/abs/2501.10228v1) | arXiv `2501.10228v1`, 2025-01-17; PDF SHA256 `53e41e0c8395d585e443599e9647d3154a59fe5084432762c70361df87c678d1`; latest implementation commit before submission [`09ca25bb6a17c97c2f1bfcbb386ae8494bd647cc`](https://github.com/diehoq/quantum-elliptic-curve-logarithm/tree/09ca25bb6a17c97c2f1bfcbb386ae8494bd647cc), pinned Qrisp commit `a00724e81733addf349931e02781b95b43c16cbd` | Compilable Kaliski in-place inverter at toy scale, with two full EEA work registers and a `2n`-bit iteration transcript | `HARD_NACK_Q_HISTORY` |
| Patoary, Vikram, and Galitski, [*A discrete Fourier transform based quantum circuit for modular multiplication in Shor's algorithm*](https://arxiv.org/abs/2503.10008v2) | arXiv `2503.10008v2`, 2025-03-20; PDF SHA256 `85f304a35f95cd3f85c66de2e4cd550062ba9cf0a47a68f4b047da32b5435559` | DFT factorization of the fixed-classical permutation `U_A: m -> A*m mod N`, using a second `L`-qubit register | `HARD_NACK_CLASSICAL_ONLY` |
| Zhang et al., [*Optimized quantum folding Barrett reduction for quantum modular multipliers*](https://doi.org/10.1038/s41598-025-04987-1) | Scientific Reports 15, 22808, published 2025-07-02; publisher PDF SHA256 `7b0a17fbf969be6237fd5352c54ffed214275b8e5e93b0d996d29a8b325b4a42`; the paper states all generated/analyzed data are contained in the article | Reversible reduction of a pre-existing `2n`-bit product, not a destructive two-word multiply; Q and Clifford+T formulas are supplied | `HARD_NACK_Q_PRODUCT_WORD` |

## 1. Kahanamoku-Meyer/Yao: important kernel, not the transducer

### Published interfaces

For two `n`-bit multiplicands, the exact integer quantum-quantum primitive is
an accumulator:

```text
U_qq |x>|y>|w> = |x>|y>|w + x*y>
```

The QFT denominator is `2^(2n)`, so the full integer output register has `2n`
bits. "Zero ancillas" means zero qubits beyond the input and output registers;
it does not mean that the output carrier disappears.

The recursive diagonal kernel is

```text
PhaseTripleProduct(phi)|x>|y>|z>
    = exp(i*phi*x*y*z)|x>|y>|z>.
```

For a split into `k` limbs, the three-polynomial Toom-Cook product uses
`q = 3k - 2` evaluation points. Its gate recurrence gives

```text
G_qq(n) = O(n^log_k(3k-2)).
```

At the paper's practical `k=9`, the exponent is
`log_9(25) = 1.4649735207`. This is a real asymptotic improvement over the
schoolbook phase-triple-product, and it is the one finding in this refresh that
could inform a genuinely new action grammar.

### Why it does not fit

The modular variant replaces the diagonal phase with

```text
exp(2*pi*i*x*y*z/N)
```

and applies a power-of-two QFT to an output register of
`n + O(log(1/eta))` qubits. It produces the residue only within error `eta`.
Both multiplicands remain available while the distinct Fourier/output register
is transformed. Consequently:

```text
published modular QQ carriers >= x[n] + y[n] + z[n + error padding]
persistent third field words  = 1
```

The affine-shell ABI has only `(T, lambda)` and requires
`(T,lambda) -> (a-T, m(T)*lambda-b-...)`. Aliasing `z` with `T` or `lambda`
is not a legal application of the published diagonal primitive: each of
`x`, `y`, and `z` appears independently in the phase and the construction
preserves both multiplicands.

Appendix E does provide an in-place modular circuit, but only for the
classical-constant permutation

```text
|x> -> |c*x mod N>.
```

It allocates

```text
m = n + ceil(2*log(2 + 1/(2*eta)))
```

work qubits and uses a classically precomputed `c^-1`. No corresponding
variable-quantum in-place circuit is supplied. The construction remains
approximate for every finite `m`; exact challenge value and relative phase
cannot be obtained by setting a finite published `eta=0` parameter.

### Source audit

The first-party estimator at commit
`f5fcb5c246e7330e621e5d8f3b3d828599abcfea` supports `cq` and three
`x^2 mod N` proof-of-quantumness modes. It does not emit or estimate the
general quantum-quantum modular primitive. The paper likewise says explicit
circuit construction and optimization are left to future work.

The paper's 2048-bit concrete table is for classical-quantum multiplication,
not quantum-quantum multiplication. Scaling its 0.6-million Toffoli number to
256 bits would not be a valid price for this campaign. There is therefore no
source-bound `n=256` exact `T_exec` certificate to compare with `335738.86`.

Verdict: `HARD_NACK_INTERFACE_EXACTNESS`. Preserve
`PhaseTripleProduct` as a research lead only if a new construction eliminates
the independent output register and supplies exact finite-field phase cleanup.

## 2. Measurement-based uncomputation: local savings only

Luongo et al. formalize MBU for a one-bit garbage function `g(x)`. Measuring
the garbage in the X basis avoids calling `U_g` with probability `1/2`; the
resource counts are therefore expectations. Applied to their modular adders,
the paper reports roughly 10-15% Toffoli savings for VBE-derived designs and
almost 25% for Beauregard-derived designs.

The result does not uncompute a field-width product, inverse, quotient, or
iteration transcript. The paper explicitly leaves modular multiplication and
modular exponentiation applications to future work. Its first-party repository
contains symbolic adder-cost calculations, not a multiplier.

Even a favorable 25% local reduction applied to an already admitted multiplier
would be an optimization of that multiplier, not a construction of the missing
two-register permutation. It supplies no route from three field words to two
and no `n=256` whole-transducer Q/T formula.

Verdict: `HARD_NACK_NOT_A_MULTIPLIER` for this replacement. MBU remains a
possible downstream optimization only after a clean reversible architecture
exists and its phase-repair oracle is included.

## 3. Qrisp Kaliski: "in-place" output still carries linear history

Polimeni and Seidel provide a real, compilable in-place inversion routine, but
it implements the known fixed-round Kaliski architecture rather than a new
two-register inverter. The source-level live registers in
[`kaliski_quantum`](https://github.com/diehoq/quantum-elliptic-curve-logarithm/blob/09ca25bb6a17c97c2f1bfcbb386ae8494bd647cc/src/quantum/ec_arithmetic.py)
include:

```text
v input/output             n
u EEA value                n
r, s modulo 2p             2*(n+1)
m iteration transcript     2n
a, b, add, f controls      4
--------------------------------
declared live lower bound  6n + 6
```

This lower bound excludes comparison results, zero predicates, carry scratch,
and adder work. At `n=256` it is

```text
Q_declared >= 6*256 + 6 = 1542 > 1100.
```

The paper's `p=7` benchmark measures Q30 and 2,918 Clifford+T T gates for the
inverter, confirming additional temporary width beyond the declared-register
lower bound. The paper calls the implementation a toy-scale proof of concept
and says compilation beyond toy instances is not yet scalable. It publishes no
production-width exact T formula.

The implementation binding is reproducible: commit
`09ca25bb6a17c97c2f1bfcbb386ae8494bd647cc` is the latest repository commit
before the arXiv submission; its `requirements.txt` pins Qrisp commit
`a00724e81733addf349931e02781b95b43c16cbd`. The arithmetic source SHA256 is
`de107418fe44bc085057f67d08f2e0d3241eb19db0ac2eca2758222a33560c07`.

Verdict: `HARD_NACK_Q_HISTORY`. Overwriting the input with its inverse does not
make the implementation workspace-free; the `2n` transcript alone violates
the no-linear-history fingerprint.

## 4. Patoary/Vikram/Galitski: fixed multiplier, not QQ

The 2025 DFT paper factorizes the modular multiplication permutation for an
odd, classically known `A` as

```text
U_A |m> = |A*m mod N>
U_A     = F_N^-1 * G_N(A).
```

Its circuit outline uses two `L`-qubit registers and the phase unitary

```text
V_A |m>|n> = exp(2*pi*i*A*m*n/N)|m>|n>.
```

The reported modular-multiplication complexity is `O(L^2)` and modular
exponentiation is `O(L^3)`. This is an in-place permutation on `m` only because
`A` and `A^-1` are classical constants. Replacing `A` by the live quantum
register `T` changes the operator type and recreates the quantum-quantum
product/inversion problem. The paper supplies neither that circuit nor an exact
Toffoli resource expression at `L=256`.

Verdict: `HARD_NACK_CLASSICAL_ONLY`.

## 5. Zhang et al. Barrett reducer: exact companion misses Q

The optimized folding Barrett circuit consumes a pre-existing `2n`-bit product
`|t>` and reduces it modulo an `n`-bit classical modulus. It retains a result
register `|g>` and explicit ancillary register `|a>` throughout its three
stages. It is therefore a reducer companion to an out-of-place integer
multiplier, not an in-place quantum-quantum multiplier.

Table 4 gives the optimized reducer formulas

```text
Q_reducer       = 6n + 12
T_count_reducer = 5n^2 + 38n + 32
T_depth_reducer = (5/4)n^2 + (19/2)n + 8.
```

At `n=256`:

```text
Q_reducer       = 1548
T_count_reducer = 337440 Clifford+T T gates
T_depth_reducer = 84360
```

The width formula alone exceeds Q1100 by 448 qubits, before embedding the
reducer in the affine shell. It also begins from the prohibited `2n`-bit
product carrier. The published `T-count` is not the challenge's executed
Toffoli metric, so the numerical proximity of 337,440 to the 335,738.86
campaign ceiling is not used as a cross-metric rejection.

Verdict: `HARD_NACK_Q_PRODUCT_WORD`.

## Result matrix

| Required property | KMY/Yao | MBU modular adders | Qrisp Kaliski | DFT fixed multiplier | Folding Barrett |
|---|---:|---:|---:|---:|---:|
| Variable quantum-quantum operation | yes, accumulate only | no | inversion | no | reducer accepts product |
| Destructive two-register map | no | no | output-only label, no | no | no |
| No third field-width carrier | no | n/a | no | second work register, classical multiplier | no |
| No linear transcript | yes for kernel | one-bit only | no, `2n` | yes | garbage/work registers |
| Exact finite-field value and phase | integer kernel yes; modular no | exact/expected branch correction | claimed exact toy circuit | mathematical fixed permutation; no QQ gate certificate | reduction yes |
| Q<=1100 at n=256 | kernel register total can fit, ABI fails | not a component | no, `>=1542` | no variable component | no, `1548` |
| Source-bound exact T_exec<=335738.86 | absent | absent | absent | absent | different metric and incomplete operation |

## Changed-premise reopen gate

Do not port any of these artifacts into production Rust. Reopen this literature
lane only if an owner supplies one of the following changed premises:

1. A KMY-derived exact circuit that applies the required nonlinear action
   directly to `(T,lambda)` without an independent Fourier/output word.
2. A variable in-place quantum-quantum modular primitive whose adjoint inverter
   is explicitly implemented and priced, not assumed.
3. A measurement-uncompute construction for a field-width carrier with its
   complete feed-forward phase oracle and no linear transcript.

Every reopen artifact must emit a source-level live-wire trace, an exact
forward/inverse proof, and challenge-native executed-Toffoli pricing satisfying

```text
Q_component <= 1100
T_exec + companions <= 335738.86
third_field_words = 0
linear_history_bits = 0.
```

Until then, the correct next architecture remains the bespoke two-register
affine-shell transducer or a register-shared Euclidean action grammar. This
refresh changes no provider, nonce, fleet, queue, push, public-note, candidate,
or submission state.
