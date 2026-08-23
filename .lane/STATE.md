# Lane state — Q1272 rounds696 / ladder242 production bake

Date: 2026-08-23 (Europe/Zurich)

## Decision

The audited Q1272 composition is now baked into source defaults on the isolated
branch `research/q1272-round696-ladder242`, starting from exact receipt commit
`82a742b19fb28d641e3993c3ef18abd0191544ee`.

The build is byte-for-byte reproducible and passes the production 64-lane
profile plus both focused self-tests. The inherited 9,024-shot draw remains
dirty at `17/16/0`, so this branch is a frozen hunt candidate, not a submission
candidate. No nonce search, provider action, or submission was started here.

## Frozen source defaults

```text
SUB4_PP_WIDTH_RESCALE=1 (implicit default; =0 is the opt-out)
SUB4_PP_R1=340
SUB4_PP_R2=628
SUB4_PP_ROUNDS=696
SUB4_PP_ROUNDS_MUL=696
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
SUB4_PINGPONG_TAIL_NONCE=251000962439 (unchanged inherited nonce)
```

Only three runtime defaults changed from the audited Q1274 source: divide
rounds `698 -> 696`, replay peak `1274 -> 1272`, and square ladder `244 -> 242`.
Multiply rounds were already 696; width rescaling and R1/R2 were already baked.
No arithmetic primitive or evaluator code changed.

Every tuned value retains its environment override. Two reproduction paths
were exercised after the bake:

- prior Q1274 route: `ROUNDS=698`, `ROUNDS_MUL=696`, `R1=340`, `R2=628`,
  `PEAK=1274`, `SQUARE_LADDER=244`, width rescale on -> artifact
  `60b6fe451b0cea31c2deffee907c74a1327e175f1adbe9dd41d6e9d76e6ea933`;
- promoted live route: the prior vector plus `WIDTH_RESCALE=0`, `R1=342`,
  `R2=625`, `PEAK=1275`, `SQUARE_LADDER=245` -> artifact
  `d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124`.

## Exact production evidence

Clean release build:

```text
cargo clean
cargo build --release --bin build_circuit --bin eval_circuit
```

Final default reconstruction:

| item | exact result |
|---|---|
| loaded/emitted ops | 12,901,167 |
| semantic ops before 96-op tail | 12,901,071 |
| `ops.bin` SHA-256 | `ecc3d9f0bb1dd4e68e6d337e39c4cdb66cfbfe83928a81fec28e22797fca4cfd` |
| peak qubits | 1272 |
| 64-lane diagnostic T | 914748.17 |
| 64-lane gate | classical 0, phase `0x0`, dirty qubits 0 |

The final source state was rebuilt once more after comment cleanup and produced
the same op count and artifact hash.

## Co-binder profile

`PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1` shows a balanced Q1272 plateau:

| phase | peak qubits | executed T on 64-lane diagnostic |
|---|---:|---:|
| `pp_div_replay` | 1272 | 262590.31 |
| `square_product_register` | 1272 | 58733.52 |
| `pp_mul_replay` | 1272 | 24218.28 |
| `pp_mul_walkback` | 1272 | 307586.95 |

First peak: op 2,527,023 in `pp_div_replay`. Its live-set census is 339 prior
walk-tape wires, 256 input/numerator wires, 256 replay coefficient wires, 145
`u`, 145 `v`, 128 replay-ladder wires, and three one-wire controls/signs: 1272
total. The two-qubit peak cut comes from replay ladder `130 -> 128`, coordinated
with square ladder `244 -> 242`; R1 remains 340, so the prior tape contributes
339 wires at the binding snapshot.

## Focused source gates

- `SUB4_PRODUCT_SQUARE_SELFTEST=1`: PASS — 58,980 emitted / 58,721.141
  executed Toffoli, Q1272, 64 square inputs, phase and ancilla clean.
- `SUB4_PINGPONG_POINT_ADD_SELFTEST=1`: PASS — 956,012 emitted / 914,661.344
  executed Toffoli, Q1272, 64 affine additions, phase and ancilla clean.
- `git diff --check`: PASS.

Release compilation emits three pre-existing warnings in unrelated arithmetic
and dirty-scan code. No warning originates in this bake. Repository-wide
test-only compilation is not claimed because the audited base has stale legacy
test modules; the callable production self-tests and unchanged trusted
evaluator are the applicable gates.

## Unchanged full 9,024-shot evaluation

The final default artifact was evaluated by the unchanged release
`eval_circuit` binary:

```text
loaded ops:              12,901,167
qubits:                  1272
classical mismatches:    17
phase-garbage batches:   16
ancilla-garbage batches: 0
exact average T:         914792.720
```

Rounded T would be 914793 and the score would be
`1272 * 914793 = 1,163,616,696` if a clean nonce exists, an 8,072,604 reduction
against the audited live score 1,171,689,300. The inherited draw is not clean,
so no submission claim follows from that score.

The full evaluator appends its receipt to `results.tsv`; that generated row was
removed after reading the exact average and is not part of this branch.
`ops.bin`, release binaries, logs, and generated score artifacts remain ignored
and uncommitted.

## Risk and next gate

The square and affine primitives pass their binary correctness gates. The
remaining faults are graded-route risks: two fewer divide rounds change
convergence exposure, width rescaling narrows the sampled schedule, and the
smaller replay/square budgets change measured-boundary exposure.

Before any hunt, qualify an exact classical predictor against unchanged full
9,024-shot fixtures and prove CPU/GPU parity on this exact op hash. Only after
that gate should a bounded first-predicted-clean canary be evaluated. A final
candidate still requires full `0/0/0` on the unchanged evaluator.

---

# Lane continuation — Q1272 density overturn (from checkpoint 091abce)

Date: 2026-08-23 (Europe/Zurich). Objective: minimize expected time to a clean
Q1272 nonce with a strict score beat (clean rounded T <= 921139); re-descend
density on the exact 696/696 stream.

## D0 — baseline reproduced byte-for-byte (clean rebuild)

- `cargo clean` + release rebuild at 091abce; `build_circuit` emitted
  12,901,167 ops, ops.bin sha256
  `ecc3d9f0bb1dd4e68e6d337e39c4cdb66cfbfe83928a81fec28e22797fca4cfd` — exact
  match to the frozen receipt. VERIFIED.
- 64-lane diag (`PP_PROFILE=1`): T914748.17 total, Q1272, peak op 2,527,023 in
  `pp_div_replay`, 0 classical / phase 0x0 / 0 dirty — exact match.

## D1 — tooling ported (route 1), byte-neutral

- Ported the Q1274 lane's `SUB4_DUMP_WSCHED` (schedule dump through the real
  `value_width` path) and `SUB4_PP_WSCHED_FILE` (sampled-table CSV override,
  default-off) into `mod.rs`/`pingpong_div.rs`. No `WIDTH_REPAIR` const
  imported — repairs must be refitted on this stream.
- Byte-neutrality: default rebuild after the port reproduces sha256
  `ecc3d9f0...` exactly. VERIFIED. (Note: a `SUB4_DUMP_WSCHED=1` run clobbers
  `ops.bin` with an empty stream; always rebuild after dumping.)
- Effective 696-map schedule dumped: `round*703/695` compression; effective
  width hits the 8-bit floor from round ~614 (rescale) vs ~692 (base).

## D2 — classical fault oracle validated on THIS stream

- ppfilter binary sha256 `f763f770527117be409123ae23ab8ceeecac1d5b8d7ee4e698d468f375f58128`
  (the exact binary the Q1274 lane cross-checked against its trusted 18/10/0
  and 22/11/0 receipts), source `/Users/olifreuler/ecdsa-ppfilter-rl`.
- `PPF_OPS=<this ops.bin> PPF_ROUNDS_DIV=696 PPF_ROUNDS_MUL=696
  PPF_WSCHED=<effective rescaled schedule>` breakdown @ inherited nonce
  251000962439: **pred_cls=17** == the trusted full-eval receipt (17/16/0).
  Split: walk_div=10 replay_div=0 walk_mul=5 replay_mul=2; causes: width=11
  term=4 walkback=0 shell=0; first faulting shot 889.

## D3 — corpus predeclaration (BEFORE any census observation)

Committed before any fit/census run on these draws:

- Training sample A: nonces 111000000000 .. 111000000319 (320 draws).
- Held-out sample B: nonces 222000000000 .. 222000000319 (320 draws).
- Held-out sample C: nonces 333000000000 .. 333000000319 (320 draws).
- Fitting uses A only (refits may use A+B, then validate on C, mirroring the
  Q1274 protocol). Controls (direct Q1274 r100/r200 index transfer) are
  priced on A and validated on B without refitting.
- The inherited nonce 251000962439 is a fixture only, never a density sample.

## D4 — pricing correction + pre-registered decision rule (BEFORE census)

- **Diag→full offset on THIS stream is +44.55, NOT the Q1274 lane's -23.37.**
  Measured pair: diag 914748.17 vs trusted full average 914792.720. Sign is
  flipped vs Q1274. All candidate pricing uses full-eval T and reports against
  the 921139 ceiling directly; the offset is re-derived for any schedule change.
- Headroom: 921139 - 914792.72 = **6346 full-eval T** (~6302 diag).
- Objective is expected time to a clean nonce; clean = 0 classical AND 0 phase
  AND 0 ancilla over 9024 shots. E[nonces-to-clean] ~ exp(lambda_cls +
  lambda_phase + lambda_anc). Inherited draw: 17 cls / 16 phase batches / 0 anc.
  Width repair CANNOT touch phase or the hard classical channels (term/replay/
  walkback/square/result).
- Inherited-nonce classical decomposition (ppfilter): width=11, term=4,
  walkback=0, shell=0, replay_mul=2 -> ~6 lambda already hard-channel.
- **PRE-REGISTERED DECISION RULE**: after the corpus-A deficit census yields the
  +1-repairable lambda ceiling C1, compare C1 to measured lambda_phase:
    * If C1 is small relative to lambda_phase (width is not the binding channel
      for time-to-clean), width repair is PRICED-AND-PARKED (report the frontier
      as evidence, do not fit r100/r200 analogues) and the lane PIVOTS to
      phase/hard channels (route 4) and the square/replay-ladder phase audit
      (route 5).
    * Otherwise, fit sparse +1 / bounded +2 width repairs on corpus A, validate
      on B/C, and price the Pareto knee against the 6346-T ceiling.
- lambda_phase is measured in parallel on corpora A/B/C: first via any existing
  fleet phase predictor (phase-rank/ppprobe, 787e-opus5-phase-filter), else via
  small-n `screen_nonces --full` on the PREDECLARED nonce lists. This is a
  DENSITY MEASUREMENT on fixed predeclared nonces (no --best-score win search,
  no scanning), not the prohibited nonce scan.

## D5 — corpus-A width deficit census (n=320, ppfilter census, VALIDATED)

Census total cross-validated: single-nonce census at 251000962439 = 17 faulting
shots == trusted receipt (17/16/0). Corpus-A (nonces 111000000000+0..319):

| quantity | per-nonce lambda |
|---|---:|
| lambda_cls (total) | 17.56 |
| hard_only (no width deficit) | 3.63 |
| hard_and_width (non-converging walk, +deficit) | 7.85 |
| soft width-only (hard-clean, width-fault) | 6.08 |
|   of which +1-repairable (all deficits == 1 bit) | **3.51 (C1)** |
|   of which need +2 or more | 2.57 |

Classical floor under UNLIMITED width widening = hard_only + hard_and_width =
**11.48 lambda** (these shots fault even at infinite width — non-converging
walks / terminal / replay, all schedule-independent). Max conceivable classical
reduction by width = the 6.08 soft lambda.

Greedy +1 set-cover frontier (in-sample corpus A; each shot needs ALL its
deficit sampled-indices widened): 40 idx -> 0.94 lambda, 100 idx -> 1.66,
200 idx -> 2.34, 300 idx -> 2.80 (ceiling 3.51 needs >300 diffuse indices).
Population is DIFFUSE: median 3 indices/shot, top index touches 96/1123 shots
(8.5%), no cheap pocket. The Q1274 lane's "no ~6-round pocket, smooth frontier"
finding TRANSFERS qualitatively to the 696-stream. Held-out realizable is ~half
in-sample (Q1274 measured r100 = -0.95 held-out), so r100 ~0.9 lambda, r200
~1.2 lambda held-out.

## D6 — phase/classical/ancilla ground truth (screen_nonces --full, held-out)

Full-sim (trusted-equivalent, no early abort) over corpus B nonces
222000000000+0..15 (n=16):

- lambda_cls = 17.56 +/- 4.18  (== ppfilter census 17.56 exactly: classical
  oracle cross-validated on held-out data)
- lambda_phase = 13.31 +/- 3.87
- lambda_anc = 0
- lambda_total (cls+phase) = 30.87

This was a DENSITY MEASUREMENT on predeclared fixed nonces (no --best-score win
search, no scanning), tool source screen_nonces.rs (ported from
fable-peak-q1275-940e34a, digest guard stripped for this tree; kept uncommitted
as a temporary evaluator per gate).

## D7 — VERDICT: width repair PRICED-AND-PARKED; Q1272 not huntable by density

Applying the D4 pre-registered decision rule (C1=3.51 vs lambda_phase=13.31):

- E[nonces to clean] ~ exp(lambda_cls + lambda_phase) = exp(30.87) ~ 2.6e13.
- Huntable reference (accepted-class configs): lambda_total ~10.9 ~ 5.4e4.
  Q1272 as-is is ~exp(20) ~ 5e8x harder than a huntable config.
- Width repair addresses ONLY the soft classical channel. Realizable within any
  sane T budget: r100 ~0.9 held-out lambda (+~500 diag T), r200 ~1.2 (+~1000 T)
  -> a 2.5-3.3x search speedup. The 6346-T ceiling could in principle buy the
  full C1=3.51 (~33x) but only at the diffuse tail's rising T/lambda cost.
- Even at INFINITE width widening the classical floor (11.48) + phase (13.31)
  leaves lambda_total ~= 24.79 ~ 5.8e10 -- still ~1e6x worse than huntable.

Therefore width repair CANNOT make Q1272 huntable. Per the decision rule, width
is PRICED-AND-PARKED (frontier recorded above as evidence; NO r100/r200 baked --
baking would erode the strict-beat score margin for a practically infeasible
search and add risk surface with zero huntability payoff). The Q1272 frozen
artifact stays byte-identical (ecc3d9f0..., diag T914748.17, Q1272; square and
affine selftests reproduce exact frozen values; git diff --check clean).

The BINDING channels for time-to-clean are both schedule-independent and NOT
width-repairable:
1. Hard classical ~11.48 lambda: non-converging pingpong walks (7.85),
   terminal/replay clears (3.63). Route 4 (walkback/replay/tape overturn).
2. Phase ~13.31 lambda: untouched by any width move; no exact predictor exists
   for the 696/696 stream (would need a new tool). Route 4/5.

## Next binder

The task premise ("~6.3k T of density-repair room" implies a reachable clean
nonce) is REFUTED with held-out data: the T room is real but density at Q1272 is
exp(~30.9) from clean, dominated by two channels width cannot touch. The
highest-value next experiment is NOT width fitting; it is a phase + hard-classical
attack:
- Build a 696/696 phase predictor (the fleet has only partial lower-bound K
  rankers at 700/696; none predicts the trusted phase-batch count) to make the
  ~13.3 phase lambda measurable/attackable cheaply.
- Characterize the 7.85-lambda non-converging-walk population (route 4): is it
  intrinsic to the a_div/a_mul distribution at 696 rounds, or reducible by a
  bounded walkback/replay-tape architectural change with an exact miter?
- Route 5 (square/replay-ladder co-binder audit) only with measured co-binder
  and exact-test evidence, since the Q1272 peak cut REQUIRES replay 128 + square
  242 jointly (Q1274 lane exp #6/#7: square binds 1274 without both).

## D8 — VERDICT CORRECTION: huntable reference measured; width repair is a LIVE lever

Three advisor-prompted validations (all passed) overturn the D7 "not huntable"
framing, which rested on a mis-recalled huntable reference (lambda_total ~10.9
from another lane's prose) and an unjustified channel-independence assumption.

**Apparatus validation (screen_nonces false-negative gates):**
- Fixture B: Q1272 ops.bin @ inherited nonce 251000962439 -> **17/16/0**, avg
  914793 == trusted receipt exactly. lambda_phase=13.31 is now cross-validated
  (the phase channel of the modified screen_nonces reproduces the paid receipt).
- Fixture A: live-equiv artifact (opt-out chain
  `SUB4_PP_ROUNDS=698 SUB4_PP_ROUNDS_MUL=696 SUB4_PP_WIDTH_RESCALE=0
  SUB4_PP_R1=342 SUB4_PP_R2=625 SUB4_PP_PEAK=1275 SUB4_SQUARE_LADDER=245`
  -> sha256 d9737f51... byte-for-byte, confirming the tooling port left the
  opt-out intact) @ 251000962439 -> **CLEAN 0/0/0**, avg 918972, score
  1171689300 exactly. Strongest possible FN gate: the apparatus certifies the
  accepted submission's own clean nonce.

**Channel dependence:** classical and phase co-vary strongly:
r=0.833 (Q1272 corpus B), r=0.912 (live corpus B). So the independence product
exp(lambda_cls+lambda_phase) is a LOWER bound on P(clean); the correlated
upper bound is exp(-max(lambda_cls,lambda_phase)). E[nonces] for Q1272 lies in
[exp(17.56), exp(30.87)] = [4.2e7, 2.6e13] -- a 6-order-of-magnitude range.

**Huntable reference (MEASURED, not recalled):** the live config -- which is
provably huntable, its clean nonce 251000962439 was found and accepted -- has
measured density on corpus B (n=16, full sim): lambda_cls=15.00,
lambda_phase=11.38, sum=26.38, r=0.912. NOT 10.9.

**Corrected gap Q1272 vs proven-huntable live:**
- independence (sum): 30.87 - 26.38 = 4.49 -> ~89x harder
- correlated (max channel): 17.56 - 15.00 = 2.56 -> ~13x harder
So Q1272 is ~13-89x harder to hunt than a config that WAS hunted -- a bigger
GPU scan, NOT categorically infeasible. The 1e6x-from-huntable claim in D7 is
RETRACTED.

**Width repair is therefore a LIVE lever, not parked.** Cutting classical lambda
directly closes the gap to the proven-huntable live density, at a STRICTLY
BETTER score (peak 1272 vs 1275). Held-out realizable (frontier x0.5 in-sample,
per Q1274 calibration) vs resulting gap:

| width cut (held-out lambda_cls) | gap indep | gap correlated |
|---|---|---|
| 0.9 (r100-class) | x36 | x5.3 |
| 1.2 (r200-class) | x27 | x3.9 |
| 1.75 (+1 ceiling C1 held-out) | x16 | x2.2 |
| 3.0 (all-soft, needs +2 repairs) | x4.4 | x0.6 (better than live) |

At the +1 ceiling Q1272 reaches ~2.2x live's hunt cost (correlated); adding
bounded +2 repairs on the 2.57-lambda soft-excess-gt1 population reaches
hunt-parity-or-better while beating the score. This is a real search-economics
win, well inside the 6346-T ceiling.

**Estimated strict-beat score (if a clean nonce is found):** peak 1272 x rounded
T 914793 = **1,163,616,696**, a **-8,072,604** reduction vs live 1,171,689,300.
**Held-out density change from THIS lane: none** -- no repair was baked; the
Q1272 artifact is byte-identical (ecc3d9f0...). The width frontier is recorded
as the priced, validated recipe for the next step.

## Next binder (corrected)

1. HIGHEST VALUE: fit the sparse +1 width repair on corpus A (greedy cover,
   tables in D5), validate held-out on B/C via the census tool, MEASURE the
   diag-T cost per r-set by rebuild+PP_PROFILE (do NOT assume Q1274's T rates),
   confirm peak co-binders unchanged at Q1272 and both selftests, then bake the
   knee that reaches hunt-parity with live inside the T ceiling. Add bounded +2
   repairs on the soft-excess-gt1 population if +1 alone leaves gap > ~1x.
   Because widening is exactly evaluable (never creates a classical fault), the
   held-out lambda is provable from deficit profiles without new full sims.
2. Then re-measure the correlated joint P(clean) directly (larger n full-sim on
   the baked stream) to price expected nonces exactly, not by the r-bracket.
3. Phase (~13.3 lambda) and the hard non-converging-walk classical (~7.85) remain
   the untouchable floor; they cap how far width alone can go but do NOT block
   reaching live-parity. Route 4/5 architectural work is the lever BEYOND parity.
