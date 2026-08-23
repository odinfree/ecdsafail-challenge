# Predeclaration — b523 paired-cap descent below Q1276

Written 2026-08-23, before measuring any Q1275/Q1274 row. Source: exact live
`b523ecf` in this worktree. Baseline reproduced exactly:

- operation SHA-256 (`shasum -a 256 ops.bin`) =
  `4cb1787b181417c1e180ddf362fd7e44430ef2d422bb4184d73d7fe1924fdf7e`
- Q1278, T914789.886, `0/0/0`, 12,876,472 operations.
- frozen live score `1,169,101,620 = 1278 * 914790`.

## Question

Does the exact paired-cap law (`SUB4_PP_PEAK` caps the ping-pong replay peak,
`SUB4_SQUARE_LADDER` caps the square via `square_peak = 1030 + LADDER`) extend
strictly below Q1276 on the current source, first at Q1275 then Q1274?

## Frozen levers (NOT touched by any row)

`SUB4_PP_R1=298`, `SUB4_PP_R2=613`, `BREAK_2=304`, slopes 17/34/40, MARGIN=4,
rounds 700/696, split 298/613, `PP_TAIL_SHARE` unset. If the plain pair misses a
target Q with these frozen, that IS the finding — a negative reported with
R1/R2 named as the unexplored interleave lever. Reaching for R1/R2 mid-run to
rescue a missed Q is the skill's ladder-arm anti-pattern and is forbidden here.

## Owner-attribution rule (free, no analyzer)

Prediction `square_peak = 1030 + LADDER`, corroborated by ladder248->Q1278,
peak1276+ladder248->Q1278 (owner in `square_product_register`),
peak1276+ladder246->Q1276. For each row:
- Q == PEAK              => replay binds (expected primary owner).
- Q > PEAK and Q == 1030+LADDER => square binds.
- Q > PEAK and Q != 1030+LADDER => a THIRD owner exists; stop and build an
  ops.bin peak-index analyzer (kept outside git) before any score claim.

## Bounded matrix (exactly these rows; no third architecture family)

| row | PEAK | LADDER | BREAK_1 | predicted Q |
|---|---:|---:|---:|---:|
| Q1275 control | 1275 | 245 | default(30) | 1275 |
| Q1275 +break  | 1275 | 245 | 24          | 1275 |
| Q1274 control | 1274 | 244 | default(30) | 1274 |
| Q1274 +break  | 1274 | 244 | 24          | 1274 |

`BREAK_1` is a compile-time const on this source; it is exposed as env
`SUB4_PP_BREAK_1` via a `OnceLock` wrapper (the file's `tail_share_k` idiom).
Byte-identity gate: with `SUB4_PP_BREAK_1` unset, the rebuild MUST reproduce
12,876,472 operations and SHA `4cb1787b...` exactly, or the edit is rejected.

## Gates, in order (stop a row at the first failure)

1. Q reachability: read Q off the eval (never inferred). Row must reach its
   predicted Q. Owner attribution per the rule above.
2. Strict score ceiling: rounded-T <= 916942 at Q1275, <= 917662 at Q1274
   (so Q*round(T) < 1,169,101,620). avg_tof read from the eval / results.tsv
   FAIL row (dirty builds do not emit score.json but avg_tof is still logged).
3. Structural sanity: a row returning hundreds of classical mismatches is a
   starved-allowance structural failure, not a fault-density datapoint — stop
   and report as such, do not compare its density to the 17/16/0-class rows.
4. For any row that reaches its Q AND beats its ceiling: verify operation
   identity (SHA), Q owner profile, focused square + complete point-add
   selftests, exact value/phase/ancilla, and one unchanged inherited 9,024-shot
   evaluation. A dirty inherited nonce is an architecture result, never hunt
   authorization.

## Outcome policy

Prefer the lowest-Q strict-beating composition. A dirty nonce authorizes no
hunt, provider action, fleet retarget, submission, or public note. Bake only
after an env-driven artifact is frozen and byte identity is proven. Protected
b523 defaults must stay reproducible. No source default change beyond exposing
`SUB4_PP_BREAK_1` (which is inert when unset).
