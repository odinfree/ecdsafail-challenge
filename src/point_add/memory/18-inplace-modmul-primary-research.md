# In-place variable modular multiplication: primary-source research verdict

**Bound artifact:** source commit
`67524171baaf568dc3dc606f38515745f70804ff`, tree
`8202910d176fa1f3332ff961e6f3f789ca6a7ac2`; current peak Q1267; live
history tape 636; replay pair 512; Q1000 added-Toffoli headroom 243,341.

## Verdict

`HARD_NACK` for transplanting a generic published in-place
quantum-quantum modular multiplication or division construction as the
one-word replay cut under the current Q/T equation.

This is **not** a lower bound against every nonlinear, tape-specialized
transducer.  The primary literature establishes a sharp reduction, not a
universal ancilla or gate lower bound: a clean circuit for

```text
U: |a>|b> -> |a>|a*b mod p>
```

over nonzero `a` has an adjoint implementing
`U†: |a>|c> -> |a>|a^-1*c mod p>`.  In particular, `c=1` computes the
variable inverse.  Therefore a cheap bare in-place variable multiplier would
also be a comparably cheap inverter.  It does **not** follow that every possible
implementation must visibly contain Euclid, a stored inverse, or an extra
256-qubit word.  A new specialized construction can reopen this verdict, but it
must exhibit and price that construction rather than assume inversion away.

## Binding to the live ECDSA.fail equation

- Deleting one of the two 256-qubit replay words changes Q1267 only to Q1011.
  Reaching Q1000 still requires at least 11 more live-qubit deletions, before
  scratch for the replacement transform.
- The current history binder is 636 qubits and the Q1000 history cap is 369;
  the required reduction is 267 qubits.  A bare 256-qubit deletion alone is
  therefore insufficient by the same 11-qubit margin.
- The exact Q1000 added-Toffoli allowance is 243,341.  Ragavan and
  Vaikuntanathan's generic variable-input workaround uses six calls to an
  out-of-place multiplier (four forward and two inverse).  If that architecture
  had to fit this allowance, its average budget would be at most 40,556.8 T per
  call, before swaps or surrounding logic.  This is a campaign falsifier, not a
  complexity lower bound.
- Their workaround represents a logical value together with its inverse:
  `(a,a^-1,b,b^-1) -> (a,a^-1,ab,(ab)^-1)`.  It therefore preserves a second
  field-width carrier per value and does not turn the live 512-qubit replay pair
  into one 256-qubit word.

## What the primary sources actually show

| Primary source | Exact construction or obstruction | Published resource consequence | Relevance here |
|---|---|---|---|
| Ragavan and Vaikuntanathan, [*Space-Efficient and Noise-Robust Quantum Factoring*](https://arxiv.org/html/2310.00899v5#S1.SS3) (2024), [Section 5.1](https://arxiv.org/html/2310.00899v5#S5.SS1) | Explicitly reduces bare in-place quantum-quantum multiplication to inversion using the adjoint.  Lemma 5.1 converts an out-of-place multiplier to an in-place **constant** multiplier with three multiplier calls.  Lemma 5.2 handles variable inputs only by storing each value and its inverse, then using four forward plus two inverse out-of-place calls. | Lemma 5.2 restores the multiplier's `S` clean ancillas and `n` dirty ancillas, but retains four `n`-bit logical registers.  The paper's discussion identifies the four `n`-qubit accumulators as an unresolved space cost. | Strongest exact reduction.  The published generic workaround does not delete a replay word; it changes the representation while retaining inverse carriers. |
| Rines and Chuang, [*High Performance Quantum Modular Multipliers*](https://arxiv.org/html/1801.01081#S2.SS2) (2018), [quantum-quantum case](https://arxiv.org/html/1801.01081#S2.SS5) | Their in-place quantum-classical circuit computes out of place, swaps, and reverses multiplication by a classically known inverse.  For two quantum inputs they provide an accumulated, out-of-place product and state that making it in place requires reversible modular inversion. | Their leading binary-ripple estimate for the easier in-place quantum-classical case is `3n` qubits and `4n^2` Toffolis; at `n=256`, the leading Toffoli term is 262,144. | Even this constant-input leading term exceeds the live 243,341-T allowance by 18,803, before coherent variable inversion.  This is an architecture estimate, not a strict secp256k1 lower bound. |
| Häner, Jaques, Naehrig, Roetteler, and Soeken, [*Improved Quantum Circuits for ECDLP*](https://arxiv.org/html/2001.09580v1#S2) (2020), [arithmetic details](https://arxiv.org/html/2001.09580v1#S3) | Notes that the inverse of in-place `(x,y)->(x,xy mod p)` is division, while Bennett cleanup adds an output register, copies, and runs the computation backward.  Its generic `xy+z` construction computes a product into an auxiliary register, adds it, and uncomputes it.  Appendix A.3 reports no efficient in-place recursive matrix multiplication; fresh outputs exceeded the qubit budget. | Generic multiplication-with-accumulation costs two multiplications solely to compute and uncompute the product carrier. | Directly matches the replay problem: merely naming a multiply/divide transform does not remove the carrier or cleanup cost.  The paper reports best-known methods, not an impossibility proof. |
| Häner, Roetteler, and Svore, [*Factoring using 2n+2 qubits with Toffoli based modular multiplication*](https://arxiv.org/html/1611.07995v2#S3) (2017) | For a classical constant, computes `|x>|0> -> |x>|ax>`, swaps, then subtracts `a^-1` times the new value to clear the old word. | Uses `2n+1` qubits for the modular multiplication and gives `32 n^2 log2(n) + O(n^2)` Toffolis; both compute and uncompute perform `n` controlled modular additions. | A celebrated low-space construction still uses a second `n`-qubit word and a classically precomputed inverse.  It does not solve variable-input one-word replay. |
| Roetteler, Naehrig, Svore, and Lauter, [*Quantum Resource Estimates for Computing Elliptic Curve Discrete Logarithms*](https://arxiv.org/pdf/1706.06752) (2017), Table 1 | Published reversible field arithmetic XORs multiplication, squaring, and inversion results into an `n`-bit result register so the branch/history can be reversed cleanly. | At `n=256`, its formulas give about 12.88M Toffolis and Q770 for double-and-add multiplication, about 6.67M Toffolis and Q1284 for Montgomery multiplication, and 16.78M Toffolis and Q1817 for inversion. | Historical exact-cost baselines miss the 243,341-T allowance by orders of magnitude and do not provide a one-word in-place replacement. |

The numerical substitutions in the last row use the paper's Table 1 formulas:
`32n^2 log2(n)-59.4n^2`, `16n^2 log2(n)-26.3n^2`, and
`32n^2 log2(n)`.  The decimal lower-order coefficients are fitted resource
estimates, so those substituted totals are comparative estimates rather than
integer gate certificates.

## First-party source audit

The published designs' register diagrams are also visible in their maintained
source implementations:

- Microsoft's archived
  [QuantumEllipticCurves `ModularArithmetic.qs`](https://github.com/microsoft/QuantumEllipticCurves/blob/dbf4836afaf7a9fab813cbc0970e65af85a6f93a/MicrosoftQuantumCrypto/ModularArithmetic.qs#L799-L817)
  (repository commit `dbf4836afaf7a9fab813cbc0970e65af85a6f93a`, raw-file SHA256
  `faaceba293fd0cb2a87e4c7bb0c20e9e2d483c95bfc17b8015a75d9a2bde8402`)
  implements constant in-place multiplication by borrowing an `n`-qubit
  register, computing the classical modular inverse, and applying the adjoint
  inverse multiplier after the swap.  Its
  [generic Montgomery multiplier](https://github.com/microsoft/QuantumEllipticCurves/blob/dbf4836afaf7a9fab813cbc0970e65af85a6f93a/MicrosoftQuantumCrypto/ModularArithmetic.qs#L1090-L1224)
  has a distinct `n`-qubit output and explicit uncomputation; its
  [binary-GCD inverter](https://github.com/microsoft/QuantumEllipticCurves/blob/dbf4836afaf7a9fab813cbc0970e65af85a6f93a/MicrosoftQuantumCrypto/ModularArithmetic.qs#L2055-L2300)
  allocates full-width Euclidean state and reports `2n + ceil(log2 n) + 2`
  ancillary qubits in addition to the output.
- Google's current
  [Qualtran `mod_multiplication.py`](https://github.com/quantumlib/Qualtran/blob/42ffddb657b8c36867cb0cc4aacf2366b6fa6259/qualtran/bloqs/mod_arithmetic/mod_multiplication.py)
  (repository commit `42ffddb657b8c36867cb0cc4aacf2366b6fa6259`, raw-file SHA256
  `38664151422563e924465c210f739f1861bcd9291a50ca4c1cbfc07bb31ea6ed`)
  makes the same distinction: `CModMulK` borrows an `n`-bit `y`, clears the old
  word using `-k^-1`, and swaps; `DirtyOutOfPlaceMontgomeryModMul` exposes a
  separate `n`-bit target plus quotient/reduction history, consumed by its
  adjoint.  This is implementation evidence, not proof that another design
  cannot exist.

## Falsifier-oriented recommendation

Do not implement or benchmark a generic literature transplant.  Reopen the
structural cut only when an owner supplies one explicit reversible transform
that simultaneously passes all five gates:

1. It is correct either on the full nonzero field or on the exact reachable,
   tape-conditioned replay domain; the domain restriction is stated and
   independently checked.
2. A source-level lifetime trace proves peak Q1000 or lower.  Because deleting
   one word leaves Q1011, the design must delete at least 11 further co-live
   qubits **and** accommodate every scratch qubit.
3. Source-bound executed added T is at most 243,341, including inverse,
   quotient/reduction handling, swaps, controls, and cleanup.
4. No hidden 256-bit product, inverse, quotient, discriminator, or history
   carrier is present; any dirty borrow is restored on every legal path.
5. If it claims the generic bare map, running its adjoint on `|a>|1>` is priced
   as the corresponding inverter.  A tape-specialized construction may evade
   the generic reduction only by a proof that its restricted domain does not
   expose arbitrary inversion.

Failure of any gate keeps this lane closed.  Passing the gates admits only a
candidate for independent replay and full official validation; it does not
open provider, nonce, queue, public-note, or submission authority.

## Scope and actions

Research was restricted to primary papers and first-party source repositories.
No production circuit, provider, nonce, fleet, queue, push, public note, or
submission state was changed.
