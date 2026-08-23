# E002 — fixed-nonce sparse width-repair feasibility predeclaration

Status: `PREDECLARED / NO SEMANTIC SOURCE EDIT / NO RESULT`.

## Exact base, fixture, and score binder

- worktree: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/q1272-fixed-nonce-width-repair`;
- branch: `research/q1272-fixed-nonce-width-repair`;
- evidence base commit / tree:
  `41dd0b4508527081b8d24255adf0579389f02453` /
  `04fee126fd8fb3112e7422bddb2e458dd38adbc6`;
- structural source commit / tree:
  `73422709ed70ba9725b3cb592770bcf197df4cdb` /
  `fe77bddfb49b426312b1cca3d009b150cd06fd89`;
- `pingpong_div.rs` / `mod.rs` / `pp_profile.rs` SHA-256:
  `6e7cce578663d8419c032190a9caa405ca0d84e0512104b766b9c68540f01994` /
  `0c9e9a920d9078f2390028009895f03d495096fdac9d2b596c7913c064e03e63` /
  `3eeab2801b88b16b1e9334febf9ae1d3e32a8de64e62ca852625e4ae913bb538`;
- inherited operation artifact: 12,904,643 operations, SHA-256
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- inherited nonce: `65700024945645`;
- exact build environment: `SUB4_PP_FOLD_SELECTOR_EVICT=1`,
  `SUB4_PP_PEAK=1272`, `SUB4_SQUARE_LADDER=242`; every other `SUB4_*`
  control unset;
- unchanged full fixture: Q1272 / 957,916 bits / 9,024 shots,
  T914783.521 (rounded 914784), classical/phase/ancilla `23/8/0`;
- inherited receipt: `.lane/E001-RESULT.md`, SHA-256
  `ab5189cc5c9005a7056167b29cf8dd25f07bab5d608d2d1febf566c1135120df`;
- tracked `results.tsv` baseline SHA-256:
  `eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

The strict Q1272 rounded-T ceiling is `914961`; the inherited rounded T is
`914784`, leaving at most `+177`.  Q must remain exactly 1272.

Before classification, this experiment must import one **committed** predictor
packet that is bound to the same source commit, source hashes, operation SHA,
nonce, and unchanged 9,024-shot fixture and that reproduces the complete
classical failure set exactly `23/23`.  The imported commit/tree, predictor
source and executable hashes, sorted shot set and its SHA-256, trace schema,
and deterministic-repeat receipt will be appended before any candidate result.
Uncommitted or source-incompatible predictor files are inadmissible.

## Sole candidate family

The only allowed semantic change is a finite sparse set of `+1` adjustments to
sampled indices of the existing 700-entry `WIDTH_SCHEDULE`.  The adjustment is
evaluated on the inherited rescaled schedule and only at indices causally
required by the exact 23 classical failures.

Forbidden: `+2`, intervals, uniform bias, schedule refitting, round changes,
nonce changes, peak or square changes, a second circuit lever, and any repair
chosen from cost alone.  The inherited 100-index `WIDTH_REPAIR` list is only an
archaeological candidate pool; no index enters the solution without an exact
failure trace.  A missing profiler `TOTAL`, panic, parse ambiguity, or invalid
schedule row fails closed.

## Classification and minimum-repair proof

For every one of the 23 exact failure shots, record all source-localized first
classical divergences and the sampled width index, scheduled width, required
signed width, excess, direction, and replay/walk stage.

- `width-soft`: every causal classical divergence is an excess-exactly-one
  width loss and the source-bound predictor proves that `+1` at at least one
  recorded causal index clears that shot without creating another classical
  failure;
- `hard`: any non-width mechanism, excess greater than one, unavailable causal
  index, or residual failure after all admissible causal `+1` repairs.

One hard shot is an immediate terminal `KILL`.

For the all-soft case, construct the shot-to-index clearance matrix by exact
predictor reruns, enumerate the minimum-cardinality covering subsets, and break
ties by lowest conservative source-exact cost and then lexicographically by
index.  Record both a lower bound (including pairwise-incompatible witness
shots where present) and an explicit covering set.  Re-run the complete
9,024-shot predictor on the composition; predicted classical count must be
exactly zero.

## Pricing and execution gates

First reproduce the inherited fixed diagnostic with `PP_PROFILE=1` and
`PP_PROFILE_SEED=0` three times.  Price every trace-admissible single `+1` and
the minimum composition from clean forced builds under the exact three-variable
candidate environment.  Record source hash, schedule-file hash, binary hash,
operation count, Q, `TOTAL`, profiler correctness channels, and repeat hashes.

The fixed 64-lane diagnostic is a deterministic comparison tool, not the
official 9,024-shot score.  Negative single-index deltas are not credited as a
proof of score headroom.  Before the unchanged full evaluator may run, the
source-bound 9,024-shot model must predict both:

1. classical count exactly zero for the complete repair composition; and
2. Q1272 with rounded T no greater than 914961 under a conservative cost
   binder.

If the exact minimum composition is priced above `+177`, or the conservative
binder cannot establish score positivity, the experiment is `KILL` without a
full evaluation.  If both gates pass, run the unchanged full 9,024-shot
evaluator once.  Acceptance then requires Q1272, rounded T at most 914961, and
classical/phase/ancilla exactly `0/0/0`; otherwise `KILL`.

Generated schedules, traces, logs, binaries, and operation artifacts remain
outside Git.  Durable predeclaration, compact tables, hashes, source changes,
and decision evidence may be committed.

No provider, range, hunt, fleet, submission, or public-note action is
authorized.
