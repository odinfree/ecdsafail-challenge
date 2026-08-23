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

## D9 — width-repair Pareto FITTED, VALIDATED, T-PRICED (this session)

Baseline reproduced byte-for-byte: build_circuit -> 12,901,167 ops, ops.bin
sha256 `ecc3d9f0...`, PP_PROFILE peak 1272 (op 2,527,023, pp_div_replay),
TOTAL diag T 914748.17, 64-lane classical 0 / phase 0x0 / dirty 0. VERIFIED.

**Census tool (ppfilter `deficits` mode) added and cross-validated.** ppfilter
source `/Users/olifreuler/ecdsa-ppfilter-rl` gained an infinite-width `walk_required`
census + `deficits` mode (per soft-repairable shot: sampled-index deficit set;
plus hard/soft/plus1 counts). Rebuilt binary sha256
`dfa6f76ca8681aaa260879293f5fb02f0f389c24b3e33e7df0535e7a3b7d9e3e` (was
`f763f770...`; MODEL unchanged, only a new read-only mode added). Provenance
re-validated: `breakdown 251000962439` still `pred_cls=17` (walk_div=10
replay_div=0 walk_mul=5 replay_mul=2, width=11 term=4). Census on corpus A
reproduces D5 EXACTLY: lambda_cls=17.559, soft=6.081, +1-repairable=3.509.

**Fitting protocol.** Deficits mapped raw round -> build sampled index via the
exact build map `width_round_index(r)=r*703/695` (ROUNDS_DEFAULT=704, r=696).
Two structural gates enforced at fit time (advisor-flagged):
- Monotonicity: `pingpong_simulator_selfcheck` asserts value_width non-increasing
  (PRODUCTION gate). Every candidate table is a right-to-left running-max
  ENVELOPE of base+deltas; all candidates verified non-increasing effective.
- Peak safety: the Q1272 binding plateau is sampled idx {342,343,344,345} (w=145,
  contributing 145 u + 145 v to the 1272 live-set). Excluded from the cover pool;
  14 soft shots that require it were dropped (cost 0.043 in-sample lambda).
Python compression of a candidate table reproduces the build's SUB4_DUMP_WSCHED
effective schedule with ZERO mismatch, so density is priced with no rebuilds via
`PPF_WSCHED=<candidate effective>`; T is priced with no recompile via the build's
`SUB4_PP_WSCHED_FILE=<candidate sampled table>` + PP_PROFILE (base-table override
reproduces TOTAL 914748.17 / peak 1272 exactly = neutral).

**Greedy +1 set-cover frontier (corpus A, excl forbidden plateau)** reproduces
D5: 40 idx->0.938, 100->1.659, 200->2.359, 300->2.816, +1 ceiling 555->3.466.

**Pareto set (peak 1272 held on ALL +1 candidates; 64-lane 0/0x0/0 on all):**

| cand | idx | diag T | ΔT | A λ_cls | B λ_cls (held-out) | held-out Δλ | Δλ/ΔT |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 0 | 914748.17 | 0 | 17.559 | 17.784 | 0 | — |
| r100 | 100 | 915106.17 | +358 | 15.900 | 16.275 | 1.509 | 0.00421 |
| r200 | 200 | 915772.23 | +1024 | 15.200 | 15.588 | 2.196 | 0.00214 |
| r300 | 300 | 916331.23 | +1583 | 14.744 | 15.062 | 2.722 | 0.00172 |
| ceil | 555 | 917491.50 | +2743 | 14.094 | 14.219 | 3.565 | 0.00130 |

In-sample Δλ matches set-cover exactly (1.659/2.359/2.816). Held-out transfer is
0.91-0.93 of in-sample (NOT 0.5 as D8 conservatively assumed) — the greedy indices
are high-population-rate, not overfit. **Subset property confirmed empirically:**
`hard` count is INVARIANT across all candidates (A=3673, B=3599) — widening never
creates a classical fault; the faulting-shot set is a strict subset of baseline's.

**Live classical anchor re-measured at n=320 (exact oracle), not D8's n=16.**
Live artifact rebuilt via the opt-out chain -> sha `d9737f51...` (byte-exact);
ppfilter certifies live's accepted clean nonce (pred_cls=0). Live corpus-B
classical lambda = **14.637** (D8's n=16 read was 15.00). So held-out classical
PARITY with live sits between r300 (15.062) and ceil (14.219); ceil is BELOW live
classical.

**Bounded +2 is INFEASIBLE.** The all-soft (widen every soft deficit) candidate
has deficits up to +9 bits, bumps peak to **1278** (pp_mul_walkback) and diag T to
931996 (over the 921139 ceiling). So the +1 ceiling is the natural maximum; the
soft_gt1 (deficit>1) population cannot be repaired without breaking Q1272. No +2
candidate is bakeable.

**Score headroom.** Full-eval T ceiling 921139; baseline full 914792.72 (offset
+44.55, to be re-derived for finalist). Est finalist full T (offset+44.55) and
strict-beat score (peak 1272 x rounded full-T) vs live 1,171,689,300:
- r300: full ~916376 -> score ~1,165,630,272 (beat -6,059,028)
- ceil: full ~917536 -> score ~1,167,085,792 (beat -4,603,508)
All +1 candidates beat live by millions; T ceiling is not the binding constraint.

**Uncertainty (small-n phase).** Width touches only the classical channel. Phase
lambda (D8 n=16): Q1272 13.31, live 11.38 — an irreducible +1.9 gap width cannot
close. Under the correlated (max-channel) model classical binds until cls~phase
(~13.31), so every +1 cut down to ~ceil still reduces the binding channel; under
the independent (sum) model the phase gap keeps Q1272 ~4.5x above live even at
ceil. True E[nonces] is a bracket, not a point. Finalist phase density MUST be
re-measured post-bake on a fresh corpus (hash change).

## D10 — finalist = ceil; bake-validation corpus PREDECLARED (before observation)

**Finalist: the +1 CEILING (`ceil`, 555 sampled indices).** Rationale: ceil
strictly dominates r300 under BOTH bracket endpoints. Independent (sum) model:
lambda_total = lambda_cls + lambda_phase, so each 1.0 of classical reduction is
worth exp(1.0) regardless of the (additive, equal-for-both) phase gap -- r300's
extra 0.84 lambda_cls is NOT wasted. Max-channel model: classical binds until
cls~=phase(~13.31); ceil's held-out cls (14.219) is still above 13.31, so its cut
is fully live. There is no model in the bracket where r300 is preferred. ceil also
brings Q1272 classical density BELOW the proven-huntable live config (14.219 vs
14.637, both n=320 exact oracle) at peak 1272. +2 is infeasible (all-soft -> peak
1278). ceil is the maximal feasible +1 repair (uses the entire peak-safe +1 pool).
Score cost vs r300 ~1.48M, against a beat that stays ~ -4.6M with ~3.6k T of
ceiling margin; the objective ranks hunt economics above score-maximization
(score is a constraint, satisfied with margin).

**PREDECLARED bake-validation corpus (committed BEFORE observing the baked
finalist's density):** nonces **444000000000 .. 444000000063** (64 draws),
deterministic, non-overlapping with A (111e9), B (222e9), C (333e9), or the
inherited fixture 251000962439. Bound to the finalist's source/config identity:
the baked default Q1272 stream = base source + a rescale-ON-gated width-repair
overlay applying the `ceil` sampled table (`/tmp/tbl_ceil.csv`, 555 peak-safe +1s
+ envelope), rounds 696/696, all other defaults unchanged. Classical density on
these 64 will be measured by ppfilter on the BAKED ops.bin + baked effective
schedule; phase density by screen_nonces full sim. No fixed-stream per-nonce win
is reused across the hash change. Pre-bake lambda_phase=13.31 (n=16) is NOT
carried into the finalist economics; it is a fresh draw post-bake.

**ppfilter oracle provenance note:** the `deficits` mode added `walk_required`
(read-only, infinite-width) and a new match arm ONLY; `walk`,
`shot_fault_mask_split`, `divide_replay`, `multiply_replay`, and all model
constants are byte-identical to the binary that validated against the trusted
18/10/0 and 22/11/0 receipts. Provenance re-confirmed by `breakdown 251000962439`
= pred_cls 17 on the new binary (sha `dfa6f76c...`).

## D11 — ceil BAKED into source; structural gates PASS; baked-stream density

**Baked operation identity.** ceil is baked into source as `WIDTH_SCHEDULE_Q1272`
(base `WIDTH_SCHEDULE` + 555 peak-safe +1s + running-max envelope), read only on
the shipped width-rescale-on path via a new `default_width_table()` gate; the
`SUB4_PP_WIDTH_RESCALE=0` opt-out reads the unrepaired base. Clean rebuild:
- default artifact: **12,944,164 ops**, ops.bin sha256
  **`95e844f318d90687d0d7088b6d70809b8a444e8227e1f95fd31b9153c137f194`**,
  peak **1272** (op 2,530,455, pp_div_replay), diag TOTAL **917491.50**,
  64-lane classical 0 / phase 0x0 / dirty 0.

**Bake == priced candidate (equivalence proof).** On the baked source,
`SUB4_PP_WSCHED_FILE=/tmp/tbl_ceil.csv` reproduces the default hash `95e844f3...`
byte-for-byte (a no-op) -> the baked table is exactly the priced `ceil` object.
`SUB4_DUMP_WSCHED` baked effective schedule == priced `cand_ceil` (0 mismatches).

**Opt-out chain preserved.** The live route
(`SUB4_PP_ROUNDS=698 SUB4_PP_ROUNDS_MUL=696 SUB4_PP_WIDTH_RESCALE=0 SUB4_PP_R1=342
SUB4_PP_R2=625 SUB4_PP_PEAK=1275 SUB4_SQUARE_LADDER=245`) still reproduces
`d9737f51...` byte-for-byte after the bake (the rescale=0 gate reads the base
table). This was the single most likely silent breakage; it is verified intact.

**Structural gates (baked source):**
- `SUB4_PRODUCT_SQUARE_SELFTEST=1`: PASS (58,980 emitted / 58,721.141 exec Toffoli,
  peak 1272; unchanged from baseline — square is width-repair-invariant).
- `SUB4_PINGPONG_POINT_ADD_SELFTEST=1`: PASS (959,400 emitted / 917,507.953 exec
  Toffoli, 1272 qubits; monotonicity assertion held on the baked table).
- PP_PROFILE 64-lane: peak 1272, classical 0, phase 0x0, dirty 0.
- `git diff --check`: clean.

**Re-derived diag->full offset (NOT reused).** Unchanged release `eval_circuit` on
the baked artifact: exact average T **917607.682** (results.tsv row read then
reverted). Offset = 917607.682 - 917491.50 = **+116.18** (baseline was +44.55; the
offset shifted with the schedule, as expected). Rounded full-T **917608 <= 921139**
(3531 T margin) -> score gate PASS. Strict-beat score if a clean nonce exists:
1272 x 917608 = **1,167,197,376** (-4,491,924 vs live 1,171,689,300).

**One inherited 9,024-shot diagnostic (allowed; after gates).** Baked eval at the
inherited nonce 251000962439: **14 classical / 12 phase batches / 0 ancilla**
(DIRTY draw). Per protocol a dirty inherited draw does NOT kill an ensemble
density improvement; the density evidence is the held-out corpora and the fresh
predeclared bake corpus below.

**Oracle re-validation on the BAKED hash (FN gates).**
- ppfilter `breakdown 251000962439` on baked ops -> **pred_cls=14** == baked eval's
  14 classical. Classical oracle certified on the new hash.
- screen_nonces `--full` @ 251000962439 on baked ops -> **cls=14 phase=12 anc=0**,
  avg_round 917608 == baked eval receipt exactly. Phase apparatus certified on the
  new hash (reproduces the paid full-eval receipt).

**Baked-stream classical density on the 64 PREDECLARED bake nonces
(444000000000..444000000063), fresh corpus after the hash change:**
- baked Q1272 finalist: lambda_cls = **13.828** (hard 705 -> hard-lambda 11.02 ~
  the infinite-width floor 11.48; soft 180 -> 2.81, the +2-needing tail).
- live on the SAME 64 nonces: lambda_cls = **14.406**.
So the baked finalist's classical density is **0.58 below the proven-huntable live
config on the same fresh nonces**, at peak 1272 vs live's 1275 — the classical win
survives the hash change (consistent with the held-out corpus-B 14.219 vs 14.637).

**Phase density on the 64 bake nonces: full-sim in progress (background).** Pre-bake
lambda_phase=13.31 (n=16) is NOT carried; the baked value is a fresh draw and is
reported next. Classical vs phase co-binding and the final economics bracket follow
once the baked-stream phase lands.

## D12 — VERDICT + CORRECTION: repair is real; live anchor was ppfilter-inflated

Full-sim (trusted screen_nonces `--full`, no early abort) on the 64 PREDECLARED
bake nonces (444000000000..063), baked stream sha `95e844f3...`, live sha
`d9737f51...`, both apparatuses re-certified on their own clean/paid receipts:

| config (n=64 full-sim) | lambda_cls | lambda_phase | lambda_anc | corr | sum | max-channel |
|---|---:|---:|---:|---:|---:|---:|
| BAKED Q1272 (ceil) | 13.812 +/- 0.503 | 10.422 +/- 0.407 | 0 | 0.675 | 24.234 | 14.000 |
| LIVE (same nonces) | 12.266 +/- 0.435 | 10.344 +/- 0.350 | 0 | 0.515 | 22.609 | 12.719 |

**CORRECTION (supersedes the D8/D9 live anchor).** ppfilter faithfully models the
Q1272 replay (pred_cls=14 == baked eval; pred_cls=10 == full-sim cls=10 at
444000000000) but OVER-counts LIVE's classical (ppfilter 18 vs full-sim 16 at
444000000000; replay_div/replay_mul flags fire that live's R1=342/R2=625 replay
does not produce). So the D8 live anchor (15.00, n=16) and the D9 anchor (14.637,
n=320 ppfilter) were INFLATED. The trusted full-sim live classical is **12.27**,
BELOW baked Q1272's 13.81. **Retract the D9/D11 claim that the baked finalist
beats live classical density.** It does not: live is ~1.5 lambda better on the
hard classical channel, and phase is essentially tied (10.42 vs 10.34).

**Corrected hunt-economics gap (full-sim, same nonces):**
- max-channel (correlated, optimistic): 14.000 - 12.719 = 1.281 -> **~3.6x harder**
- sum (independent, pessimistic): 24.234 - 22.609 = 1.625 -> **~5.1x harder**
So baked Q1272-at-ceil is ~3.6-5x harder to hunt than proven-huntable live, NOT
at parity. Uncertainty is real (n=64; cls diff 1.55 is ~2.3 sigma; phase and the
correlation are small-n).

**What the repair DID achieve (validated, durable, net-positive):**
- On the IDENTICAL baked 64-nonce corpus, the width repair cut classical lambda
  by **3.281** (base schedule 17.109 -> ceil 13.812; hard count identical at 705,
  subset property confirmed on the baked stream). ppfilter is faithful for Q1272,
  so this delta is trustworthy.
- Pre-repair Q1272 max-channel ~17.1 vs live 12.72 => ~80x harder. Post-repair
  ~3.6-5x harder. **The bake improved Q1272 huntability ~15-22x** at a strictly
  better score (peak 1272 vs 1275; strict-beat score 1,167,197,376, -4,491,924 vs
  live), inside the rounded-T ceiling (917608 <= 921139), with the opt-out chain
  intact (d9737f51 reproduces).
- The bake trades +3.58M score (vs unbaked Q1272's 1,163,616,696) for the ~20x
  huntability gain -- a strongly favorable trade for the hunt while still beating
  live by 4.5M.

**Residual gap to live = HARD classical, not width.** Baked Q1272 hard-lambda
~11.02 (ppfilter, faithful) already exceeds live's TOTAL classical 12.27 by only
~1.2; the remaining soft (2.79) needs +2 repairs that are INFEASIBLE (all-soft ->
peak 1278, T over ceiling). So width has been exhausted. The residual is the
696-round / narrower-peak structure producing more non-converging pingpong walks
than live's 698-round structure -- Route 4 (walkback/replay-tape overturn), NOT a
width lever. Phase (~10.4) is tied with live and untouched by width.

**Bottom line.** The task's structural goal is MET: the smallest peak-safe +1
width repair is fitted, validated (held-out + fresh-corpus full-sim), and baked at
Q1272 with a strict score beat and an intact opt-out chain, cutting classical
density by ~3.28 lambda and improving huntability ~20x. The task's ECONOMIC goal
(reach approximately live hunt economics) is PARTIALLY met: the gap narrows from
~80x to ~3.6-5x but not to parity, because live's true (full-sim) density is
better than the ppfilter estimate that motivated the "parity reachable" premise.
The bake is a genuine, net-positive, durable improvement worth keeping.

## Next binder (corrected, final)

1. The width channel is EXHAUSTED at Q1272 (ceil baked; +2 infeasible). Further
   huntability requires the HARD classical channel: characterize the ~11 lambda
   non-converging-walk population at 696 rounds vs live's 698 (Route 4). The
   +1.5-lambda classical gap to live is entirely here.
2. Re-audit any future live-vs-Q1272 density comparison with FULL-SIM, never
   ppfilter, for the live/foreign-replay side. ppfilter is faithful ONLY for the
   Q1272/7ca0559 replay params it embeds.
3. Phase (~10.4) is at live parity and width-invariant; no phase lever is needed
   to reach live economics -- only the hard classical residual blocks parity.

## D13 — decomposition sharpened; clean-build + census-source reproducibility closed

**Clean-build reproducibility (frozen-candidate gate).** `cargo clean` + release
rebuild of build_circuit/eval_circuit -> default artifact **12,944,164 ops**,
ops.bin sha256 **`95e844f3...`** — byte-for-byte match. The D11 bake is a frozen,
clean-reproducible candidate.

**Census-source reproducibility.** The ppfilter `deficits` census (on which the
whole fit rests) is preserved at
`/Users/olifreuler/ecdsa-ppfilter-rl/CENSUS_ADDITIONS_Q1272_LANE.rs.txt`
(that repo is not under git). It records the pre-edit oracle sha
`f763f770...`, the edited-binary sha `dfa6f76c...`, the two additions
(`walk_required` + `deficits` arm; walk/shot_fault_mask_split/replay UNCHANGED),
and the rebuild command. `breakdown 251000962439` = pred_cls 17 confirms the
model was not perturbed.

**Classical hard/soft decomposition (corrects D12's channel comparison).** Using
ppfilter's width-faithful soft channel and routing the 137 live over-counted
shots (all false replay/term flags -> ppfilter hard bucket) out of live's hard:

| config (n=64) | hard | soft | total classical |
|---|---:|---:|---:|
| baked Q1272 (ceil) | 11.02 | 2.79 | 13.81 |
| live (derived*) | ~8.11 | ~4.16 | 12.27 |

*live hard is derived under the replay-flag assumption; live total 12.27 and both
soft values are directly measured (full-sim total; ppfilter width-faithful soft).

Two consequences D12 understated:
1. **The residual to live is entirely hard-classical and LARGER than the net gap:**
   Q1272's hard floor (11.02) is ~2.91 lambda ABOVE live's (~8.11). The net 1.55
   classical gap is the hard +2.91 partly offset by Q1272's better soft. So Route 4
   (non-converging-walk / 696-vs-698 structure) is even more strongly the only
   remaining lever than D12 stated. Width is exhausted.
2. **Live carries ~4.16 lambda of unexploited SOFT width faults** (vs baked Q1272's
   2.79). A Q1272-style +1 width repair fitted on the live/698 stream is an
   unexploited width lever there, at whatever peak the 698 stream can absorb — a
   fresh campaign finding for the live lane.

**Final status.** Structural goal MET (smallest peak-safe +1 repair fitted,
validated, baked at Q1272; strict score beat -4.49M; opt-out intact; clean-build
reproducible). Economic goal PARTIALLY met (huntability ~80x -> ~3.6-5x vs live,
not parity; residual is hard-classical, width-unreachable). The bake is a genuine,
net-positive, durable improvement. Next lever: Route 4 hard-classical, NOT width.
