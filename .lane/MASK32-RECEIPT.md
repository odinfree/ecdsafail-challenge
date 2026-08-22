# E6 mask comparison receipt

This receipt closes the interrupted 32-nonce local comparison for
`SUB4_PP_WIDTH_RESCALE=1`. It is evidence for screen behavior only. It does
not authorize or record a provider run, nonce fleet, or submission.

## Exact target identity

- Semantic base: `940e34acbc9cdc9ac497f67eea40db80551d1f7c`
- Source subtree used by all resumed comparisons:
  `e7b4db8d41f930457e39909798cb74f64183a116`
- Source delta from the semantic base is default-off instrumentation in only
  `src/point_add/mod.rs` and `src/point_add/pingpong_div.rs`.
- `build_circuit` SHA-256:
  `96b8c99b62b92dd52319a8ee9b0b64156dfc88310c9346c8f04faf54faf13ca4`
- Trusted `evalall` SHA-256:
  `a9f647b60cfc3cb8c2beff0894ab88555a6abbce21d0e1175e5ba739c7340bc0`
- Predictor SHA-256:
  `f763f770527117be409123ae23ab8ceeecac1d5b8d7ee4e698d468f375f58128`
- Predictor geometry was explicit: `PPF_ROUNDS_DIV=698`,
  `PPF_ROUNDS_MUL=696`.
- Rescale schedule CSV SHA-256:
  `d1700e214dadd4554b941432b682f3f8d82cdc7fb68472c5ff31facc9c8560ed`
- Frozen rescale ops: 12,864,810 ops, 50,411,849 bytes,
  MD5 `09b1e83b6b438b31b6cd956389074f99`, SHA-256
  `9d9dbebaf74e74543c62d3ca7f803a9110adcd26746dc89635adbe88eb5d31fd`.

Every trusted receipt reported 12,864,810 loaded ops, Q1278, 9,024 tested
shots, and zero ancilla-garbage batches.

## Baseline byte-identity guard

After the 32 comparisons, a clean default build with every rescale/table/
nonce override unset reproduced the archived `940e34a` baseline byte for
byte:

- 12,918,089 ops; 50,973,289 bytes
- MD5 `2476648bade253b539b41bbc2e230b7b`
- SHA-256 `38e4d98d2ed7c9d0c3600f631e371de54284832f7cd7657fe25698c46c062a7e`
- `cmp` against `.lane/probe-base/ops-base-baked.bin`: identical

The default-off instrumentation therefore leaves the shipped baseline
unchanged.

## Result

- Comparisons completed: **32/32**
- Exact predicted/measured shot sets: **31/32**
- Measured fault shots: **503**
- Predicted fault shots: **504**
- False negatives: **0**
- False positives: **1**
- Predicted-count range: **8..25**
- `pred<=4` exercised: **no**
- `pred=0` exercised: **no**

The sole difference is nonce `6000229651`, shot `8735`: the predictor emits
mask `4` (multiply-walk terminal/convergence guard), while the trusted
evaluator is classically clean on that shot. This is a conservative false
positive, so it costs a confirm but cannot hide a clean nonce. There were no
measured-only shots anywhere in 32 x 9,024 = **288,768** shot decisions.

The one-sided rule-of-three bound for the observed zero false negatives is
`3 / 288,768 = 1.04e-5` per shot. A union bound over 9,024 shots gives a
heuristic worst-case survivor probability of at least 0.906 and an FN hunt
multiplier of at most about **1.11x**. Nonce-level path correlation remains a
caveat; the unobserved `pred=0` regime still requires the fleet's ordinary
trusted confirmer.

## Wrong-table movement

The canary was rerun with the same predictor binary, R698/R696, nonce
`6000000000`, and frozen base ops:

- trusted base measured set: 13 shots
- embedded base-table prediction: 13 shots, exact set match
- deliberately wrong rescale-table prediction on the base stream: 15 shots
- wrong-table-only shots: `1339`, `3619`

Correct-table and measured-set SHA-256:
`5f34d5076e88d931b1ca21c74ddf240d8465b7d38d97d6f06235fbe384982ffc`.
Wrong-table set SHA-256:
`a99c8267e8f6ffcfde087b3b3d9eab23547e7d49efb207ccf95a44f8c3007f55`.
The override therefore demonstrably moves predictor output; it was not
silently ignored.

## Raw receipt preservation

The ignored local raw receipts remain in `.lane/probe-rescale/masks/`:
32 trusted evaluator logs, 32 measured shot lists, 32 predicted shot lists,
and the reconciled summary. `.lane/MASK32-SHA256SUMS` records all 97 file
hashes; its own SHA-256 is
`9e2e001f819031e231e09f97e30a84d94bdac5fcb27dcec3a16890c1544dd346`.
Generated logs and ops binaries are intentionally not committed.

The tracked `.lane/MASK32-SUMMARY.tsv` is byte-identical to the reconciled
local summary (SHA-256
`8bdf9b27b8856f6acbf82eed5ad38f561631d134e9c21045e2b0c102c58f1d44`).
Its columns are nonce, measured count, predicted count, set verdict, and the
trusted per-nonce average executed Toffoli.

The reconciled summary parses average Toffoli directly from each trusted
receipt. This removes the two obviously foreign `3,962,753.000` cells and
also replaces the earlier shared-`results.tsv` carry-forward values with the
correct per-nonce values.
