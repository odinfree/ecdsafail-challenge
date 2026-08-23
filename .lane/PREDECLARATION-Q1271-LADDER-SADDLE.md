# Predeclaration — direct live-source Q1271 ladder saddle (binding, before any armed run)

Lane: `research/q1271-live-ladder-saddle`, isolated worktree
`par/work/q1271-live-ladder-saddle`. Supplements dispatch commit `af1789a`.
Committed and pushed BEFORE any Q1271-armed measurement or semantic edit.

## Exact source

- Promoted source commit: `2c79d2f4ef1f6fdc6f75024ef4ae50c6506e2208`
- Source tree: `d50e00b6ba06975de822e7184ca930d3542e255e`
- Worktree HEAD differs from the source only under `.lane/`;
  `git diff 2c79d2f -- src/` is empty and stays empty (knob-only lane,
  both knobs already exist in the frozen parent).
- Frozen structure: `SUB4_PP_ROUNDS=698`, `SUB4_PP_ROUNDS_MUL=696`,
  `SUB4_PP_R1=340`, `SUB4_PP_R2=628` (source defaults), width schedule,
  replay fold, and all arithmetic semantics unchanged.

## Live economics (reopened this session, 2026-08-23)

`ecdsafail benchmark`: current best **1,167,654,124** @ source `2c79d2f`
(= 1274 × 916,526; parent official avg executed Toffoli 916,525.546).
Strict beat ceilings, rounded T ≤ floor((S−1)/Q):

| Q | ceiling rounded T | headroom over parent 916,526 |
|---|---|---|
| 1273 | 917,245 | +719 |
| 1272 | 917,967 | +1,441 |
| 1271 | **918,689** | **+2,163** |

## Four co-binders (parent census at Q1274, sibling-corrected `c70526d`)

All four bind at exactly 1274 and all are budget-filled carry ladders:

1. `pp_div_replay` — terminal batch ladder 62, peak binds ops_idx 2528381
2. `square_product_register` — `SQUARE_LADDER=244`, peak = 1030 + 244
3. `pp_mul_replay` — terminal batch ladder 63 + doubled_out
4. `pp_mul_walkback` — interleaved replay + split-walk ladders

The three `pp_*` binders derive from `plan.peak` (`SUB4_PP_PEAK`,
`pingpong_div.rs:1263`); the square from `SUB4_SQUARE_LADDER`
(`trailmix_ludicrous/square/product_register.rs:41`). The N-way-tie law
applies: a candidate scores only if all four drop simultaneously.

## Hypothesis

Candidate configuration (no source edit): `SUB4_PP_PEAK=1271
SUB4_SQUARE_LADDER=241`.

- Q hypothesis: builder `peak_qubits` = `num_qubits` = trusted evaluator
  qubits = **1271**; every phase maximum ≤ 1271; no new binder appears.
- T hypothesis: per-wire price measured at Q1274→Q1273 was +632…+678
  executed; if the plateau stays linear for three wires, projected official
  rounded T = 916,525.546 + 1,896…2,034 → **918,422…918,560 ≤ 918,689**
  (margin +129…+267). The sibling dossier expects "roughly two more wires
  before layout cliffs", so Q1271 sits at the potential cliff edge: a
  chunk-count increase or walk-split guard break is the named risk, and the
  paired measurements decide.
- Value exactness: budget shrink re-partitions chunk ranges only; carry
  values remain bit-exact; approximation stays confined to the existing
  measured phase-channel repairs.

## Deterministic corpora (all fixed, no randomness outside them)

1. `PP_PROFILE` 64-lane corpus: inputs SHAKE256("pp_profile inputs 0"),
   simulator randomness SHAKE256("pp_profile sim 0") (`PP_PROFILE_SEED`
   unset → "0").
2. Composition selfcheck 64-lane corpus
   (`SUB4_PINGPONG_POINT_ADD_SELFTEST=1`): inputs SHAKE256("pingpong full
   affine point-add composition gate"), simulator randomness
   SHAKE256("pingpong full affine point-add simulator randomness").
3. Square component miter (`SUB4_PRODUCT_SQUARE_SELFTEST=1`): the source's
   fixed selfcheck corpus, unmodified.
4. Trusted full stream: `eval_circuit`, 9,024 SHAKE256 shots, inherited
   tail nonce = source default `100000045835813`
   (`SUB4_PINGPONG_TAIL_NONCE` unset).

## Measurement order and stop rules

1. **Controls first (no arming):** parent default build must reproduce the
   four-way 1274 tie, profile-lane exec ≈ 916,424.62, selfcheck-lane exec
   ≈ 916,510.47, `ops.bin` md5 `fdbc7f23a1ed45cca413531bed988100`; sibling
   control `SUB4_PP_PEAK=1273 SUB4_SQUARE_LADDER=243` must reproduce peak
   1273, deltas +631.86 (profile) / +677.89 (selfcheck), md5
   `5ba8782cd13b79eda79752b9351bc166`. Any mismatch → rig drift, STOP, no
   armed run.
2. **Q1272 prerequisite row** (`SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242`,
   `PP_PROFILE` only, no full battery — a separate lane owns Q1272): all
   four binders must sit at exactly 1272 with nothing new ≥ 1273 and a
   parent-delta consistent with two wires. If the allocator leaves the
   plateau here, name the exposed floor precisely; continue to Q1271 only
   if the floor is ≤ 1271, else KILL.
3. **Armed Q1271** (`SUB4_PP_PEAK=1271 SUB4_SQUARE_LADDER=241`): admit only
   if builder peak = num_qubits = 1271 AND trusted evaluator qubits = 1271
   AND all phase maxima ≤ 1271 AND profile composition `0 / 0x0 / 0` AND
   square miter passes AND composition selfcheck passes (asserted values,
   phase 0, ancillae clean) AND both paired deltas project official rounded
   T ≤ 918,689 from base 916,525.546. Any floor above 1271 → name owner
   phase and binding ops_idx, KILL as exposed-floor record.
4. **R1/R2 rebalance (gate 5):** at most one, only if the projected rounded
   T breaks 918,689 narrowly (≤ +400) AND the profile identifies the
   responsible rounds; the exact pair will be appended here before it runs.
   No broad sweep, no round/depth/width/fold change, no imported repair.
5. **Full diagnostic (gate 6):** only if every cheap gate passes — exactly
   one 9,024-shot `eval_circuit` run at the inherited nonce, unchanged.
   Record exact classical / phase / ancilla and average T. Dirty →
   **HOLD-HUNT**; clean → still HOLD for the successor (submission is
   excluded from this lane).
6. Nothing else runs: no nonce or range hunt, no other knob changes, no
   source edits, no model reuse by configuration label (gate 7 is answered
   as a semantic-portability record, with operation/checkpoint hashes and
   fixture qualification treated as new).

## Exclusions (restated, binding)

No provider/cloud compute, no nonce/range hunt, no submission, no public
note, no API-key access, no external message, no edits outside this
worktree. Never commit `ops.bin`, `results.tsv` changes, `score.*`,
binaries, `target/`, logs, caches, helpers, temporary evaluators, or
generated artifacts.
