# b523 paired-cap descent below Q1276 — result

Updated: 2026-08-23

## Decision

`GO_MODEL / HOLD_HUNT / NO_DEFAULT_CHANGE`

The exact paired-cap law extends strictly below Q1276 on live source `b523ecf`.
Lowering both co-binders one step at a time reaches Q1275 and then Q1274, each a
strict score beat over the frozen live anchor. Every winning row is a dirty
inherited-nonce architecture result, not a submission or hunt authorization. No
source default changed: the only source edit exposes `SUB4_PP_BREAK_1`, which is
inert when unset (proven by byte identity below).

## Live and source anchors

- frozen live score: `1,169,101,620 = 1278 * 914790`, source `b523ecf`;
- baseline reproduced exactly: Q1278, T914789.886, `0/0/0`, 12,876,472 ops,
  operation SHA-256 `shasum -a 256 ops.bin` =
  `4cb1787b181417c1e180ddf362fd7e44430ef2d422bb4184d73d7fe1924fdf7e`;
- inherited nonce `81327465284` (`SUB4_PINGPONG_TAIL_NONCE` default), used by
  every row below;
- strict rounded-T ceilings: Q1275 <= 916942, Q1274 <= 917662.

## Paired-cap law (verified, not assumed)

- replay peak owner is capped by `SUB4_PP_PEAK`; realized full-circuit Q == PEAK
  in every row (point-add selfcheck peaks: Q1275 row 1275, Q1274 row 1274);
- square peak owner obeys `square_peak = 1030 + SUB4_SQUARE_LADDER` exactly
  (product-square selfcheck: LADDER=245 -> 1275, LADDER=244 -> 1274), and is
  provably independent of `SUB4_PP_BREAK_1` (identical peaks with BREAK_1=24:
  `SUB4_PRODUCT_SQUARE_SELFTEST` returns before the point-add is built);
- at the winning settings both owners co-bind at the same Q, so the descent is a
  genuine coordinated drop with no third owner exposed;
- point-add selfcheck peak == PEAK on all four rows (Q1275 ctrl/break -> 1275,
  Q1274 ctrl/break -> 1274), each validating all 64 affine additions against the
  secp256k1 reference.

## Bounded matrix (all rows: inherited nonce 81327465284, 9,024 shots)

| row | PEAK | LADDER | BREAK_1 | Q | avg T | round(T) | score | margin vs live | class/phase/anc | operation SHA-256 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| baseline (protected) | -- | -- | 30 | 1278 | 914789.886 | 914790 | 1,169,101,620 | 0 | 0/0/0 | `4cb1787b...` |
| Q1275 control | 1275 | 245 | 30 | 1275 | 916529.447 | 916529 | 1,168,574,475 | 527,145 | 15/9/0 | `db33c5cd...` |
| Q1275 +break | 1275 | 245 | 24 | 1275 | 912998.195 | 912998 | 1,164,072,450 | 5,029,170 | 27/18/0 | `c729b550...` |
| Q1274 control | 1274 | 244 | 30 | 1274 | 917227.881 | 917228 | 1,168,548,472 | 553,148 | 14/9/0 | `61a57ce6...` |
| Q1274 +break | 1274 | 244 | 24 | 1274 | 913684.649 | 913685 | 1,164,034,690 | 5,066,930 | 24/17/0 | `8bc29444...` |

All four rows reach their predicted Q and clear their ceiling. R1/R2/BREAK_2/
slopes stayed frozen at default throughout; no round cut or third architecture
family was added. Notably, memory's validated Q1275 route needed `R1=342/R2=625`
on branch 940e34a; on `b523ecf` the plain peak/ladder pair reaches Q1275 AND
Q1274 with the default 298/613 interleave, so R1/R2 tuning was neither needed nor
used. R1/R2 remain an unexplored lever for any future sub-Q1274 attempt.

## Headline — Q1274 is the reached floor, with two strict-beating compositions

Both Q1274 rows strictly beat live and both are dirty inherited-nonce
architecture results (neither submittable, neither hunt authorization). They are
NOT separated by their single-nonce fault counts: this lane's own convention (the
sibling Q1276-pair H64 study) is that two op streams seed different Fiat-Shamir
ensembles, so single-nonce counts are corpus-level noise, not a density
discriminator. The predeclared H64 corpus is the undone tiebreak.

**Q1274 +break — score-optimal** (`SUB4_PP_PEAK=1274 SUB4_SQUARE_LADDER=244
SUB4_PP_BREAK_1=24`):
- Q1274, T913684.649, score 1,164,034,690, **5,066,930 below live** (~9x the
  control's margin — the objective the skill tells us to target);
- operation SHA-256 `8bc2944418c7935dc9eb141988ec5223c0b3a90429668a2af62629667ceea7fe`,
  12,879,923 ops; inherited 9,024-shot eval `24/17/0`;
- point-add selftest: pass, all 64 affine adds validated, peak 1274.

**Q1274 control — fault-minimal at the inherited nonce**
(`SUB4_PP_PEAK=1274 SUB4_SQUARE_LADDER=244`, two co-binders only):
- Q1274, T917227.881, score 1,168,548,472, **553,148 below live**;
- operation SHA-256 `61a57ce6e167b64663288ade584785b26562f61ff197f6ae0c11c85ea098ee8e`,
  12,935,433 ops (SHA reproduced identically outside the sandbox by a direct
  `build_circuit`, so operation identity is sandbox-independent);
- inherited 9,024-shot eval `14/9/0`;
- product-square selftest: pass, 58946 emitted / 58709.125 executed T, peak 1274;
- point-add selftest: pass, all 64 affine adds validated, 958962 emitted /
  917360.719 executed T, peak 1274; ancilla zero on the full run.

`SUB4_PP_BREAK_1=24` rewrites the walk width schedule (`value_width`): it cuts
avg T by ~3,500 at fixed Q, trading measured single-nonce faults up. It is the
"dirty but ample T room for another structural descent" lever the dispatch
anticipated (consistent with the sibling `6f6da43` B1=24 `22/20/0` diagnostic) —
T headroom for a future Q-owner reduction. Which Q1274 row to carry forward is a
density question, decided by the corpus below, not by these counts.

## Source edit (the only diff vs b523ecf)

`src/point_add/pingpong_div.rs`: `value_width`'s compile-time `BREAK_1` const is
exposed as env `SUB4_PP_BREAK_1` via a `OnceLock` wrapper (`break_1()`), matching
the file's `tail_share_k()` idiom so the per-round hot path stays cache-cheap.

Byte-identity gate PASSED: with `SUB4_PP_BREAK_1` unset the rebuild reproduces
12,876,472 operations and SHA `4cb1787b...` exactly. The protected b523 default
op stream is unchanged. No knob was hard-coded; no default was baked.

## Why no bake and no density corpus yet

Bake was gated on a frozen env-driven artifact with proven byte identity AND a
clean landing. The env-driven artifacts are frozen (SHAs above) and byte
identity of the default is proven, but every strict-beating row is a dirty
inherited nonce, so there is nothing clean to bake as a new default. Baking a
dirty structure as the incumbent is the skill's grind-first anti-pattern, so
defaults stay untouched.

Fault-density comparison on a predeclared corpus is the next gate for source-
bound predictor qualification of a Q1274 stream (mirroring the sibling Q1276-pair
H64 study), and it also decides which Q1274 row to carry forward. It changes
neither the structural finding nor the `HOLD_HUNT` disposition and was deferred.

## Next gate (recommended, not executed here)

1. Predeclared H64 corpus on both Q1274 SHAs (`61a57ce6...` control and
   `8bc29444...` +break) vs protected b523, fresh artifact + all 9,024 shots per
   nonce, to test (a) whether either stream's fault distribution is materially
   worse than b523 and (b) whether +break's extra single-nonce faults are draw
   noise, since +break wins the objective by ~9x if it is corpus-non-inferior.
2. Only on a non-inferior corpus: bind exact classical/phase predictors to the
   surviving SHA and consider a bounded canary. Final acceptance remains a fresh
   `0/0/0` full run whose measured score strictly beats a reopened frontier.

No hunt, provider action, fleet retarget, submission, public note, adaptive
nonce search, or ecdsa-ops mutation occurred in this lane. `git diff b523ecf..HEAD
-- src` is the single inert `SUB4_PP_BREAK_1` exposure.

---

# H64 three-stream tiebreak — PREDECLARATION

Written 2026-08-23 on HEAD `b718d20`, BEFORE any candidate aggregate is
observed. Frozen here, then measured. The structural matrix above is closed and
is not redone. This tiebreak only decides which reached-Q1274 stream (if any) is
carried forward for source-bound predictor qualification.

## Streams (exact, source-bound; SHAs reproduced on this host)

- protected b523 — no knobs, Q1278, op SHA `4cb1787b...`, 12,876,472 ops;
- control — `SUB4_PP_PEAK=1274 SUB4_SQUARE_LADDER=244`, Q1274, op SHA
  `61a57ce6...`, 12,935,433 ops, inherited-nonce `14/9/0`;
- score-optimal (B1=24) — `+ SUB4_PP_BREAK_1=24`, Q1274, op SHA `8bc29444...`,
  12,879,923 ops, inherited-nonce `24/17/0`.

All three SHAs were reproduced byte-for-byte on this host before predeclaring.

## 1. Corpus (frozen, identical for every stream)

Exactly the 64 nonces `444000000000..444000000063` (`SUB4_PINGPONG_TAIL_NONCE`),
each built from a clean source-bound config and evaluated by the UNCHANGED full
`eval_circuit` over all 9,024 shots. 64 rows/stream, 128 candidate rows total.
No row may be skipped: a missing/short/malformed row is a HARD FAIL of the run,
never a shrunk denominator. Widths, rounds, R1/R2, corpus, and evaluator are
frozen; nothing is tuned or adapted to results.

## 2. Metrics (per stream)

- classical = sum over 64 nonces of per-shot classical mismatches;
- phase = sum over 64 nonces of phase-garbage batch counts;
- ancilla = sum over 64 nonces of ancilla-garbage batch counts;
- combined = classical + phase;
- meanT = mean of the 64 exact 3-decimal evaluator average-T rows;
- every candidate row must read Q == 1274 and ancilla == 0 off the evaluator
  (Q read per row, never inferred); any violation is a row-level HARD FAIL.

## 3. Protected reference — reuse-or-rerun, and non-inferiority ceilings

The sibling Q1276 study (`b523-ladder-redescent/.lane/STATE.md`) froze the
protected-b523 H64 receipt: 64 rows, meanT `914783.503250`, `1069/848/0`, 0 clean
rows; "protected H64 rows, header excluded" SHA-256
`3b1d7777a7b45fb851cdad5fa9d2e04e6fbd1ace86497e6ceb7a60fd70f82402`.

The frozen row-ledger file was kept outside Git and is not recoverable in any
worktree/job dir, so its receipt hash CANNOT be verified by re-hash here.
Therefore, per the task's reuse-or-rerun clause, protected b523 is RERUN
unchanged. Because this tree reproduces `4cb1787b...` byte-for-byte with
`SUB4_PP_BREAK_1` unset, the protected op streams — hence Fiat-Shamir seeds and
every per-nonce count — are deterministically identical to the sibling's. The
rerun MUST land on `1069/848/0` and meanT `914783.503250` EXACTLY; any deviation
is a harness bug (env leakage, wrong nonce range, miscount) and the run stops
rather than averaging over it. Exact reproduction verifies the frozen receipt by
reproduction, which is stronger than the unavailable hash match.

Ceilings are fixed NOW from the frozen protected totals P, using the
predeclarable H0 dispersion σ₀ = √(2P) (candidate expected == protected under
H0; Var(C − P) ≈ 2P). Three-sigma non-inferiority ceilings, floor-rounded:

- classical: 1069 + 3·√2138 = 1069 + 138.7 → **≤ 1207**;
- phase: 848 + 3·√1696 = 848 + 123.5 → **≤ 971**;
- combined: 1917 + 3·√3834 = 1917 + 185.8 → **≤ 2102**;
- ancilla: hard **0** on every one of the 64 rows (no sigma).

A stream is "non-inferior to protected" iff classical ≤ 1207 AND phase ≤ 971 AND
combined ≤ 2102 AND ancilla == 0 on all rows. This σ₀ = √(2P) form is
intentionally tighter and predeclarable, unlike the sibling's post-hoc
σ = √(P+C); both z-forms are reported afterward for continuity, but adjudication
uses these frozen √(2P) ceilings and this floor-rounding convention only.

## 3b. Score-optimal-vs-control comparison rule (fixed before candidate totals)

"score-optimal not materially worse than control" iff, on the SAME 64-nonce
corpus, `combined(B1=24) − combined(control) ≤ 3·√(2·combined(control))` AND
`classical(B1=24) − classical(control) ≤ 3·√(2·classical(control))`. Control's
totals are unknown until its run; the RULE (formula, threshold, floor rounding)
is frozen now — only the numbers plug in.

## 4. Selection rule

1. carry score-optimal (B1=24) forward iff it is non-inferior to protected (§3)
   AND not materially worse than control (§3b);
2. else carry control forward iff it is non-inferior to protected (§3);
3. else HOLD BOTH.

Carry-forward means source-bound predictor qualification only — never a hunt,
provider action, fleet retarget, submission, public note, or default change. A
dirty inherited nonce is an architecture result, not hunt authorization. Score
margin never excuses density: the ~9× score edge of B1=24 does not enter §3/§4.
Final acceptance of any stream remains a future fresh `0/0/0` full run beating a
reopened frontier; this corpus only gates qualification.

Row ledgers, the harness, and receipt hashes are frozen OUTSIDE Git; only the
compact aggregate/selection table and one small per-nonce three-stream audit TSV
are committed.

## H64 terminal decision

The completed result is sealed in `.lane/H64-RESULTS.md`, with the compact
per-nonce audit in `.lane/H64-AUDIT.tsv`. Q1274 control passed every frozen
non-inferiority ceiling; B1=24 failed them and the control-comparison rule.
Carry Q1274 control forward for exact predictor qualification. No hunt is
authorized by this decision.
