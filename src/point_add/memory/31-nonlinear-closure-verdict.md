# Exact nonlinear simplification and pair closure: verdict

Verdict: `HARD_NACK_MATERIAL_SCALE`

## Binding

- official baseline ops SHA-256: `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e`
- constant/affine scanner commit/tree: `328048faa74be52ce3e8cf78d0d9e2d04d2051af` / `d5f191f2c9c03c0f0b3b9ff9bde7f9721d76aebc`
- exact-pair prototype commit/tree: `d2e3e05fb211374fd22d9492b1a95d6e900c50ea` / `92213831c03bd5026c3b431c8647ccd1d8bf83fa`
- exact revert commit/tree: `28318cd0b501e1956e32295403058401bd0ccbd4` / `d5f191f2c9c03c0f0b3b9ff9bde7f9721d76aebc`

## Constant-one and affine result

The source-integrated exact constant interpreter finds 15 additional CCX
gates with one control fixed at one. Each can be downgraded to a CX while
preserving its condition context. Together with the admitted 22 deletions,
this closes the complete three-valued nonlinear simplification domain at 37 T.

An independent exact affine interpreter then treated all 1,024 declared input
bits/qubits and every unconditional HMR result as independent Boolean
variables. It canonicalized XOR forms, Boolean idempotence, complementary
controls, and inconsistent affine control systems. Its complete baseline scan
reported:

```text
AFFINE_SCAN_PASS ops=12593858 identities=22 reductions=15
```

The 15 reductions were exactly the constant-one set. There were no additional
equal-control, complementary-control, or higher affine-inconsistency gates.

## Exact inverse-pair result

The repository's existing inverse-pair finder normally shares a measured
cascade allow-list, so the prototype added an explicit exact-only entrypoint:
no cascade triples and no straddle widening. Applied to the complete promoted
ping-pong stream, it reported:

```text
STRUCTURAL_EXACT_CCX_CLOSURE passes=0 pairs=0 removed_ccx=0 output_ops=12593762
[W018 CCZ straddle] total_ccz=40 same_triple_candidates=0 cancelled_pairs=0 removed_ccz=0 -> 12593762 ops
```

The prototype was reverted exactly after the zero-result receipt. The generic
legacy constprop driver was not applied to ping-pong: its simple domain starts
classical bits at zero, while this ABI declares 512 classical input bits.
Using it unchanged would therefore violate the fail-closed premise.

## Decision

Do not materialize or validate a 37-T variant as the next campaign candidate.
It is source-exact but too small to satisfy the mission's material-win bar and
would create another Fiat-Shamir reroll. Reopen only with a changed equation
or a source-exact transform having a materially larger leading term. No
provider, nonce-grind, fleet, queue, push, public-note, or submission action
was taken.
