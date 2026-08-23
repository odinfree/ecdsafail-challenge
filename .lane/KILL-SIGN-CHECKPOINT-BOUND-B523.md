# KILL — bounded retained-root walk reconstruction cannot enter Q1114

Resolved: 2026-08-23T09:28:41Z.
Lane: `research/b523-sign-checkpoint-bound`.
Binding predeclaration:
`.lane/PREDECLARATION-SIGN-CHECKPOINT-BOUND-B523.md`, commit `5ce1c11`.
Frozen parent: `0e20bdd97df460121fc809d4ebeb6bab12a7a0ca`.

## Verdict

**Terminal KILL before implementation.** The most optimistic conventional
retained-root checkpoint/recompute scheme fails both static gates:

1. The first missing sign is round 8, where the shipped walk width is 258. Even
   after packing 256 bits of the raw `(u,v)` state into the already-paid retained
   word, the source needs 260 additional live qubits. Its floor is Q1284 before
   one sign, a carry, or any arithmetic scratch. That exceeds Q1114 by 170.
2. Consequently no finite T exists in this family's Q<=1114 feasible set. For
   a numeric exchange receipt, waive the otherwise-illegal transient walk state
   separately for each chunk but do not invent a persistent checkpoint that
   the real circuit cannot reach. The largest replay chunk is then three signs,
   and exact repeated-prefix accounting costs **57,027,954 unconditional
   Toffolis** across the missing Divide/Multiply signs. This exceeds the
   refreshed absolute Q1114 ceiling by 55,979,791 before charging a fused cell,
   square, or any other point-add gate.

There is no `GO_IMPLEMENTATION`. No model session, source edit, build, nonce,
provider, hunt, submission, or publication was opened.

## Exact qubit lower bound

The sealed retained splice and its independent tape-sign reference fix the
fused-cell envelope exactly:

```text
production denominator + coefficient + numerator    768 Q
retained denominator word                            256 Q
persistent base                                     1024 Q
fused cell, excluding its sign                        87 Q
```

Therefore a `k`-sign chunk has

```text
Q_cell(k) = 1024 + 87 + k = 1111 + k,
```

so Q1114 permits at most `k=3`. This grants away the two fixed oracle scratch
qubits used by the bounded rounds-2..7 probe and assumes they are freed before
the cell.

The ordinary checkpoint object is the exact shipped `(u,v)` state at
`value_width(r)`. The strongest packing lets its bits overwrite the 256 retained
work wires while the original denominator ABI remains the restoration root:

```text
extra_checkpoint(r) = max(2 * value_width(r) - 256, 0).
```

Selected exact widths from the frozen `WIDTH_SCHEDULE`:

| boundary | width `w` | raw `(u,v)` | extra beyond retained 256 | base + packed state | packed state + cell + one sign |
|---:|---:|---:|---:|---:|---:|
| 8 | 258 | 516 | 260 | **1284** | 1372 |
| 356 | 140 | 280 | 24 | 1048 | 1136 |
| 388 | 128 | 256 | 0 | 1024 | 1112 |
| 602 | 45 | 90 | 0 | 1024 | 1112 |
| 695 | 8 | 16 | 0 | 1024 | 1112 |

The later rows do not rescue the family. A round-388-or-later checkpoint can
fit inside the retained word once it exists, but creating it by the ordinary
walk must first cross the round-8 516-bit raw state. Calls 8..387 also need a
sign source before that compact late boundary. Q1284 is optimistic: it omits
the sign and the round-8 adder's carry ladder entirely.

Scheduling sign production before the coefficient is allocated cannot cover
the splice. After the first replay chunk, both coefficient words are live and
carry the nonzero midpoint proven by NM64; freeing or encoding either word is a
different coefficient-absorption/cleanup architecture. Storing all early signs
before allocating the coefficient recreates the resident tape.

## Exact Toffoli lower bound

### Live gate refresh

After the binding predeclaration was pushed, the leader promoted to source
`2c79d2f`, Q1274/T916526:

```text
leader score = 1274 * 916526 = 1,167,654,124
Q1114 strict T ceiling = floor((1,167,654,124 - 1) / 1114) = 1,048,163
1114 * 1,048,163 = 1,167,653,582  accepted
1114 * 1,048,164 = 1,167,654,696  losing
```

This supersedes the looser `1,169,101,620` dispatch gate frozen in the
predeclaration. The architecture fails both, and all terminal comparisons below
use the refreshed ceiling.

The Q gate already leaves no feasible conventional checkpoint execution. To
make the exchange numeric, this second ledger grants a narrower counterfactual:
each chunk's transient raw walk state is Q-invisible, but no raw checkpoint
persists between chunks or through a fused cell. A persistent late checkpoint
may fit after the walk shrinks, but the ordinary circuit cannot create it
without first crossing the round-8 Q1284 state. The ledger does not grant a
new compressed constructor. It also gives signs 2..7 for free, gives away
rounds 0..7 of every reconstruction, charges no sign copies or checkpoint
operations, and sets the cost of every replay cell, square, and other point-add
operation to zero.

For a generic shipped walk round, `signed_add_wrapping_sigma` contains exactly
`value_width(r)-3` unconditional CCX gates in one direction. A chunk ending at
round `e` therefore costs at least

```text
2 * sum(value_width(r) - 3, r=8..e)
```

to derive from the retained root and reverse-clean. In the counterfactual
no-persistent-checkpoint schedule, each chunk pays that prefix.

The exact width-array digest (700 little-endian `u16` entries) is
`c9d5dca1b83902e21950101e5506525b128cd2722be8a797b0e39a7395db3c90`.
For each `k`, a short remainder is placed first and all other chunks have the
maximum size; this minimizes the positive prefix sum.

| `k` | `Q_cell(k)` | Divide chunks (690 missing calls) | Multiply chunks (688 missing calls) | Divide source T | Multiply source T | total source T |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1112 | 690 | 688 | 85,542,016 | 85,164,638 | 170,706,654 |
| 2 | 1113 | 345 | 344 | 42,818,114 | 42,629,420 | 85,447,534 |
| **3** | **1114** | **230** | **230** | **28,576,794** | **28,451,160** | **57,027,954** |

For the optimum `k=3` row, the exact endpoint sets are:

```text
Divide:   10, 13, 16, ..., 697
          230 chunks; endpoint-vector SHA256
          d51428a706d2314ba074c94bd50a84b737fd1d72867147d6198d73fa13f96731

Multiply: 8, 11, 14, ..., 695
          230 chunks; endpoint-vector SHA256
          77219633c4bc60b377105a9a3a1f5eba5ecb6a501f0cfc61d69392c630431874
```

A dynamic-programming sweep over every legal chunk length `1..k` independently
returns those same minimum endpoint sets and integer totals.

One ordinary forward/back pass over only the same missing rounds costs:

```text
Divide  rounds 8..697: 188,694 T
Multiply rounds 8..695: 188,674 T
single-pass total:       377,368 T
```

Thus the exact repeated-prefix tax on the same unconditional-CCX ledger is:

```text
57,027,954 - 377,368 = 56,650,586 T.
```

Against the frozen parent T919785, Q1114 under the refreshed leader buys only

```text
1,048,163 - 919,785 = 128,378 rounded T
```

of full-circuit headroom. The repeated-prefix tax exceeds that exchange by
56,522,208 T. More decisively, even this counterfactual source-only 57,027,954
price exceeds the absolute Q1114 T ceiling:

```text
57,027,954 - 1,048,163 = 55,979,791 T
1114 * 57,027,954 = 63,529,140,756
```

No subtraction of the old walk or estimate of the other phases can overturn
that absolute source-only inequality because those other phases were already
priced at zero here.

## Gate ledger

| gate | result | verdict |
|---|---|---|
| frozen source / predeclaration | exact parent/tree/source hashes; predeclaration pushed at `5ce1c11` | PASS |
| full coverage | frozen at 696 Divide + 694 Multiply fused calls; signs 2..7 granted free, missing 8..terminal priced | PASS scope |
| checkpoint/source Q | optimistic first-missing source Q1284 before sign/carry; target Q1114 | **KILL** |
| bounded recompute T | no finite T at Q<=1114; counterfactual no-persistent-checkpoint `k=3` price T57,027,954 vs refreshed ceiling 1,048,163 | **KILL** |
| implementation / closure miter | static gates fail | NOT OPENED |
| protected default / full9024 candidate | no source or candidate build | unchanged inherited control only |

## Critique, fix, verify

- **Packing objection:** counting a separate 516-Q checkpoint would be too
  pessimistic. The final bound packs 256 of those bits into the retained word
  and charges only 260 extra at round 8.
- **Early-oracle objection:** charging the already-proven prefix would overstate
  the bound. The final sum gives all signs and arithmetic through round 7 away.
- **Chunk-choice objection:** `k=1` or `k=2` can lower cell Q, but the complete
  sweep shows their recomputation totals are strictly worse. `k=3` is the
  optimistic Q1114 choice.
- **Other-gate objection:** the comparison does not assume the baseline walk
  remains. It sets every non-source candidate gate to zero and still fails the
  absolute ceiling.
- **Changed-representation objection:** a compact algebraic transducer that
  updates a 256-bit retained code without ever materializing `(u,v)` is not a
  conventional walk checkpoint. It is the separately predeclared rank/code
  family excluded here, as are direct ANF and coefficient absorption.

Two independent arithmetic forms (direct endpoint sums and dynamic programming
over all legal chunk lengths) agree exactly. `git diff 5ce1c11 -- src/` is empty;
the frozen source hashes remain unchanged.

## Next structural recommendation (not opened)

Do not revisit ordinary walk checkpoints or shorter chunks. The only changed
premise that bypasses both fired gates is an in-place algebraic retained-word
transducer whose state never expands to raw `(u,v)` and whose per-epoch inverse
is explicit. It requires its own predeclaration and a synthesis lower bound
before any implementation; this lane provides no `GO` for it.
