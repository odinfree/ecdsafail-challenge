# Balanced Q1277 saddle audit

Updated: 2026-08-23T05:44:37+02:00

## Decision

`CLOSED_Q1277_PRIOR / Q1276_DOMINATES`

The coordinated one-notch saddle is real:

```text
SUB4_PP_R1=356
SUB4_PP_R2=625
SUB4_PP_PEAK=1277
SUB4_SQUARE_LADDER=247
```

It reaches Q1277 and projects a strict beat of the live leader, but it is not
the best deployment target.  The adjacent Q1276 pair has a product lower by
350,918 and a better inherited full-shot fingerprint.  Q1277 therefore stays
as a measured saddle prior; model qualification and any later hunt belong on
Q1276 first.

No defaults were changed.  The worktree remains byte-source-identical to the
promoted commit apart from this lane evidence.

## Protected anchor and live refresh

- source: `bdf4845afa4f911192e20b5260b9efbd67655cf9`
- promoted submission: `792ac703-febb-488d-ad24-3d1d13160014`
- live refresh at 2026-08-23T05:44+02:00: source `bdf4845`, score
  `1,170,580,266 = 1278 * 915947`
- baseline artifact: 12,912,890 ops, SHA-256
  `5b60d0a227b56f53abdc99b9588a80c1ff02838618ce4e7c3bf7cb22decdebb8`
- baseline compressed bytes: 50,893,170; MD5
  `599a8c5212e6b17363c2c394c9ad087d`

The baseline was rebuilt first in a fresh directory with all saddle variables
unset.  Its op count and SHA match the promoted artifact exactly.

## Exact structural comparison

All diagnostic rows use `PP_PROFILE_SEED=0` over the same 64 lanes.  All full
rows use the unchanged trusted evaluator over all 9,024 Fiat-Shamir shots.

| route | knobs beyond bdf | ops | ops SHA-256 | Q | diagnostic T | diag channels |
|---|---|---:|---|---:|---:|---:|
| protected bdf | none | 12,912,890 | `5b60d0a227b56f53abdc99b9588a80c1ff02838618ce4e7c3bf7cb22decdebb8` | 1278 | 915994.83 | 0/0/0 |
| Q1277 pair | peak1277, ladder247 | 12,919,073 | `a6a79c5aad915ebdfa86305d05af2a8fd2f97832312ec72539f16db51b1b6d3d` | 1277 | 916234.28 | 0/0/0 |
| Q1276 pair | peak1276, ladder246 | 12,929,346 | `d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422` | 1276 | 916718.89 | 0/0/0 |
| Q1275 package | R1=342, peak1275, ladder245 | 12,947,403 | `059a249a8d2934aa83f508280f508821a92fb0b7ce5de5045d00acd0fa8e5e02` | 1275 | 917331.19 | 0/0/0 |

Compressed artifact identities:

| route | compressed bytes | MD5 |
|---|---:|---|
| Q1277 | 51,205,037 | `3f962f5f0571b97f9ae160e0788ddafc` |
| Q1276 | 51,271,953 | `db4645d14ff62f009a3571f49aa69211` |
| Q1275 | 51,047,371 | `0552ab9b9e297c15e07767b98168ccfb` |

## Detailed Q1277 co-binder trace

The existing active timeline was scanned inside the env-gated profiler.  The
temporary print hook was removed after the trace, and a forced rebuild proved
the candidate op SHA was unchanged.  Operation intervals below exclude the
96-op nonce tail, matching the profiler's 12,918,977-op view.

| phase | phase interval | peak Q | first peak op | last peak op | peak events |
|---|---:|---:|---:|---:|---:|
| `pp_div_replay` | [949585, 4716596) | 1277 | 2636152 | 4712134 | 469 |
| `square_product_register` | [6019820, 6940063) | 1277 | 6765556 | 6793644 | 4 |
| `pp_mul_replay` | [8203326, 8575628) | 1276 | 8206104 | 8573271 | 210 |
| `pp_mul_walkback` | [8575628, 12899428) | 1277 | 8596784 | 10275759 | 267 |

This is a genuine balanced plateau: divide replay, square, and multiply
walkback bind Q1277 independently.  Multiply replay is the near-binder at
Q1276.  The group-chat observation supports testing this pair, but the trace
and evaluator establish the result.

## Unchanged full 9,024-shot gate

| route | exact average T | rounded product | margin below live | cls/phase/anc | first classical mismatch |
|---|---:|---:|---:|---:|---:|
| protected bdf | 915947.392 | 1,170,580,266 | 0 | 0/0/0 | none |
| Q1277 pair | 916186.355 | 1,169,969,522 | 610,744 | 21/12/0 | 124 |
| Q1276 pair | 916628.572 | 1,169,618,604 | 961,662 | 15/5/0 | 32 |
| Q1275 package | 917361.243 | 1,169,635,275 | 944,991 | 17/8/0 | 923 |

The products for dirty rows are counterfactual ranking values, not submission
claims.  Q1276 is 350,918 below Q1277 and 16,671 below Q1275.  The Q1277 to
Q1276 step spends only 442.217 T for one qubit against a 718.014-T break-even;
the Q1276 to Q1275 step spends 732.671 T against a 718.924-T break-even and
therefore loses.

Q1277 does not earn a split hunt stream from current evidence.  Its inherited
fingerprint is worse than both neighbors, while exact target-bound candidate
density has not been calibrated.  No density number is inferred from one
nonce.  Q1276 remains the first stream to qualify because it wins both the
product and the observed fault comparison.

## Focused gates and provenance

- release build: pass; only the three pre-existing warnings in untouched
  multiply/dirtyscan code
- Q1277 product-square selftest: exit 0; 58,895 emitted / 58,668.734 executed
  T; Q1277; phase and ancilla clean
- Q1277 full point-add selftest: exit 0; 957,404 emitted / 916,315.016
  executed T; Q1277; 64 affine additions clean
- Q1277 same-seed profile: `0/0/0`
- `git diff --check`: pass
- source-clean `build_circuit` SHA-256:
  `e00f5e7a2fc768df3e209901045f18a9d569ca917ff550fb137c35ec7b0dccb6`
- unchanged `eval_circuit` SHA-256:
  `2198a5e92315ef1b98fa7cd51cb9783c06e0d909a8edbe5157af50d69b54fa7d`
- `pingpong_div.rs` SHA-256:
  `c89ccb06cddaaccb6e9755302bca96d9e4a88ec1eff7dc51d243db67aa2d174f`
- `product_register.rs` SHA-256:
  `897c6143b790421fe1d9abbbf8afff9f1f705859af22c678de5c6d9a67099cfd`
- trusted evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`

Generated `ops.bin`, evaluator rows, profiles, build targets, and full-eval
logs are not retained in Git.

## Scope closure

No nonce hunt, provider action, fleet mutation, spend, submission, or incumbent
change occurred.  Q1274 was not priced: the measured Q1276 to Q1275 exchange
already crosses break-even, and another blind notch has no cheap evidence of
dominance.

Next objective-advancing action: continue exact model qualification on the
Q1276 artifact `d1461959...`; do not allocate Q1277 capacity unless later
calibration overturns both its product deficit and its dirtier fingerprint.
