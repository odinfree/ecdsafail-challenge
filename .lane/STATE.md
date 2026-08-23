# b523ecf balanced ladder re-descent

Updated: 2026-08-23

## Decision

`GO_MODEL / HOLD_HUNT / NO_DEFAULT_CHANGE`

The exact two-co-binder transplant works on the promoted `b523ecf` source:

```text
SUB4_PP_PEAK=1276
SUB4_SQUARE_LADDER=246
```

It reaches Q1276 with a counterfactual full-shot product 497,436 below the
refreshed live score. The promoted nonce is not transferable: its unchanged
9,024-shot result is `17/16/0`. A complete paired H64 comparison finds no
material fault-density regression, so the exact stream earns source-bound
predictor qualification. It does not earn a hunt or submission yet.

No source default changed. The branch differs from `b523ecf` only by lane
evidence.

## Live and source anchors

- live refresh after H64: source `b523ecf`, score
  `1,169,101,620 = 1278 * 914790`;
- protected promoted artifact: 12,876,472 operations, SHA-256
  `4cb1787b181417c1e180ddf362fd7e44430ef2d422bb4184d73d7fe1924fdf7e`;
- protected full result: Q1278, T914789.886, `0/0/0`;
- candidate artifact at inherited nonce: 12,901,678 operations, SHA-256
  `d460c3968659b6bbbf5615268d73df210df55f9cd4cbca330de1ef960c6dd4c0`;
- candidate compressed bytes: 51,641,151;
- unchanged rounds/window/width/tail: `700/696`, `298/613`, break 30,
  nonce `81327465284`.

The unset source was forced through a fresh build before the candidate. Its
operation count and SHA reproduced the promoted artifact exactly.

## Exact structural result

| route | knobs beyond b523 | operations | operation SHA-256 | Q | fixed64 T | fixed64 channels |
|---|---|---:|---|---:|---:|---:|
| protected | none | 12,876,472 | `4cb1787b...` | 1278 | official full anchor 914789.886 | official `0/0/0` |
| peak-only control | peak1276 | 12,901,294 | `395df60f...` | 1278 | 915872.42 | `0/0/0` |
| balanced pair | peak1276, ladder246 | 12,901,678 | `d460c396...` | 1276 | 915914.61 | `0/0/0` |

The peak-only control is an exact co-binder falsifier: lowering replay alone
leaves the square at Q1278, with first peak operation 6,768,029 in
`square_product_register`. Tightening the square ladder as well removes that
owner and exposes the Q1276 divide-replay plateau. The pair is therefore a
real coordinated descent, not an apparent reduction hidden by another owner.

The candidate fixed64 product is `1,168,707,540`, 394,080 below live. Fixed64
is a diagnostic, not submission evidence.

## Unchanged inherited full gate

The unchanged trusted evaluator ran all 9,024 shots on candidate SHA
`d460c396...`:

| Q | exact average T | rounded product | margin below live | classical/phase/ancilla |
|---:|---:|---:|---:|---:|
| 1276 | 915834.428 | 1,168,604,184 | 497,436 | `17/16/0` |

This is a structurally strict beat but not a candidate submission. The
promoted source's clean nonce cannot be inherited across the changed
operation SHA.

## Complete paired H64

Both streams evaluated every nonce `444000000000..444000000063` with a fresh
artifact and all 9,024 trusted shots: 577,536 shots per stream. The row ledger
contains exactly 128 unique stream/nonce identities; all operation counts,
qubit counts, and ancilla gates match their frozen values.

| stream | rows | mean of exact 3-decimal evaluator T rows | classical | phase | ancilla | clean rows |
|---|---:|---:|---:|---:|---:|---:|
| protected b523 | 64 | 914783.503250 | 1069 | 848 | 0 | 0 |
| Q1276 pair | 64 | 915830.126813 | 1048 | 883 | 0 | 0 |

Relative to the protected stream, candidate classical faults change by -21
(-1.96%), phase by +35 (+4.13%), and their simple combined count by +14
(+0.73%). Under a conservative independent-count approximation these shifts
are only -0.46, +0.84, and +0.23 standard deviations respectively. The two
operation SHAs seed different Fiat-Shamir ensembles, so this is a corpus-level
non-inferiority result, not paired-shot evidence or a density guarantee.

The candidate H64 rounded product is `1,168,599,080`, 502,540 below live. No
H64 row was clean in either stream, which is expected at these aggregate fault
rates and does not authorize a nonce hunt by itself.

## Focused gates

- product-square selftest: pass; 58,911 emitted / 58,693.562 executed T;
  Q1276;
- complete point-add selftest: pass; 956,173 emitted / 916,009.078 executed T;
  Q1276 and all 64 affine additions clean;
- candidate fixed64 profile: `0/0/0`;
- inherited full ancilla: zero;
- all 64 candidate and all 64 protected H64 ancilla counts: zero;
- live frontier refreshed after the corpus and unchanged;
- `git diff b523ecf..HEAD -- src`: empty.

## Receipt hashes

| receipt or source | SHA-256 |
|---|---|
| candidate H64 row ledger | `77be38498291c4df6194123caf447e64655d796ec616ec77516e51ec1e1e4318` |
| protected H64 rows, header excluded | `3b1d7777a7b45fb851cdad5fa9d2e04e6fbd1ace86497e6ceb7a60fd70f82402` |
| candidate H64 rows, header excluded | `84cdef5cc22bdde9c85210b28dab4dcfb767fec47463eadd7a21d761349febe2` |
| candidate fixed64 profile log | `9cbf45fe34a3a24e38895bee5ac86b9e15c3cd35d2bbfda737b732c4aae51ec9` |
| inherited full log | `bf872eec4aeb230ce7593e9957cfd8348b6379813556ffa5614f25e46a4e2e66` |
| product-square selftest log | `d99a06158ab303fa93312c3c5ed9592cccdb96727758e0d0178ab4065440793b` |
| point-add selftest log | `b0966bd2b45d6cde37530c0a2fda2c452c2a996566c93615a06727c398386834` |
| peak-only profile log | `98383efe219c6d38b9577ee0b56e55283c976283aaf98c41902817a5ffcae100` |
| H64 harness | `a172b4b3b45cdbfc0083032e1e1dc5402638f05c8cc20f220326e5d137fbb060` |
| `build_circuit` | `c69285ff7773871fdbe12be2ea0272e9c2c4fd11e791bd971e30ed1d382f038f` |
| unchanged trusted evaluator | `d32fd63c064d61b708825de50d1c51ee01866d183f7453df973914438abbaa2f` |
| trusted evaluator source | `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b` |
| `pingpong_div.rs` | `c8eca60208a91a7a18c6732f0f3e6f48dca35e2966c00a6288fe4d184a2d9dd4` |
| `product_register.rs` | `872f9a18929cc576dcdbfd05735bc3243b756488ce6acc70ce705f46e2b302ee` |

Generated operation artifacts, evaluator rows, binaries, logs, and the H64
harness remain outside Git.

## Next gate

Bind the exact classical and phase predictors to candidate SHA `d460c396...`,
calibrate CPU against unchanged full-evaluator fixtures, prove Linux/CUDA
combination parity if a GPU screen is proposed, and only then consider a
bounded canary. Final acceptance remains a new full 9,024-shot
`classical/phase/ancilla = 0/0/0` result whose measured score strictly beats a
freshly reopened frontier.

No hunt, provider action, fleet mutation, submission, incumbent edit, or spend
occurred in this lane.
