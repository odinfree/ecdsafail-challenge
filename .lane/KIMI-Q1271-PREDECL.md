# Kimi Q1271 selector-plus-multiply-binder predeclaration

Status: `PREDECLARED / NO SEMANTIC EDIT / HOLD PROVIDER / HOLD HUNT`.

## Frozen source and score gate

- evidence commit: `41dd0b4508527081b8d24255adf0579389f02453`
- structural commit: `73422709ed70ba9725b3cb592770bcf197df4cdb`
- structural tree: `fe77bddfb49b426312b1cca3d009b150cd06fd89`
- exact operations: `12,904,643`
- operation SHA-256:
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`
- frozen selector environment: `SUB4_PP_FOLD_SELECTOR_EVICT=1`,
  `SUB4_PP_PEAK=1272`, `SUB4_SQUARE_LADDER=242`; every other `SUB4_*`
  variable unset
- measured selector saddle: Q1272, exact average T914783.521, rounded
  T914784, score `1,163,605,248`, full channels `23/8/0`
- live source/score when opened: `4eb93cb` / `1,163,831,339`
- strict rounded-T ceilings against that score: Q1271 <= 915681; Q1270 <=
  916402

The existing selector candidate is score-positive but validation-dirty. This
lane is structural only and does not claim a candidate nonce.

## One permitted family

Compose the proven selector lifecycle eviction with one multiply-replay
allocation change: remove the otherwise idle `doubled_out` qubit from the
binding chunked-add interval in `signed_mod_double_add_pm_fused`, then
reconstruct it exactly from still-live source/target/sign/add information for
its clear and inverse. The change must be default-off while under test.

This is not permission to introduce a second retained word, a new tape, a
lookup table, a permanent carry, or an unrelated arithmetic rewrite. Before
editing semantics, reproduce the Q1272 selector control and measure the
`PP_PEAK=1271` / `SQUARE_LADDER=241` binder profile. Name every Q1272 owner
that the one-qubit eviction must clear.

## Ordered gates

1. Read `/Users/olifreuler/burn-the-house-down/SKILL.md` completely and use
   its overturn, re-descent, bounded-saddle, composition, and grind-last
   discipline.
2. Rebuild the frozen selector operations byte-exact and reproduce its focused
   selector selftest plus Q1272 profile before source edits.
3. Reproduce the 1271/241 binder profile and show that `doubled_out` is live
   and idle across the exact peak interval. Kill if another unmodified owner
   makes the one-family composition incapable of reaching Q1271.
4. Implement only the default-off eviction/rematerialization family. Add a
   focused exact forward/inverse/value/relative-phase/ancilla falsifier that
   exercises both signs, carries, every relevant selector arm, and boundary
   values. Prototype tolerance is allowed before the final gate, but every
   relaxation must be explicit and cannot support a candidate claim.
5. Require Q <= 1271 and a source-exact measured rounded T <= 915681 before
   any unchanged full 9,024-shot run. Q1270 is preferred if the same family
   reaches it within T <= 916402.
6. Only if the structural and score gates pass may one unchanged full
   9,024-shot diagnostic run. A candidate requires classical/phase/ancilla
   `0/0/0`; otherwise record the exact channels and stop before search.

No web search, provider compute, nonce range, scan, hunt, submission, public
note, or external communication is authorized. Do not commit `ops.bin`,
generated binaries, evaluator rows, raw traces, logs, caches, or temporary
helpers. Keep durable state in `.lane/STATE.md` and `.lane/EXPERIMENTS.md`,
commit and push each meaningful checkpoint, and end with the next falsifier.
