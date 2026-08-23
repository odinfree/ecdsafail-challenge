# Lane state — claude-fable-burn-087cafa

Objective: from exact live source `087cafaef46a4e339644a6191ff2df2e7031cb80` (Q1275,
rounded T918972, score 1171689300), find a clean composition at Q1274 with rounded
full-eval T <= 919693. Other lane's exact Q1274 source-host composition (branch
`research/live-087cafa-exact-carry`, commit 8d261ea) reads diag T919919.48 — 963 T
hosting vs 721 allowance, 242 over. Not duplicated here.

## Ground truth (this worktree, clean rebuilds)

| item | value |
|---|---|
| baseline commit | 087cafa |
| baseline ops.bin sha256 | d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124 |
| baseline full 9024 eval | 0/0/0, avg T918972.304, Q1275, score 1171689300 |
| baseline 64-lane diag T | 918995.67 (offset full-diag = -23.37) |
| baseline paid-repair census | approx=2313 exact=285 (chunk-boundary erases) |

## RESULT: Q1274 width-rescale composition (CANDIDATE, score gate PASSED)

Config baked as source defaults (env-equivalent, opt-out restores live artifact
byte-for-byte):

- `SUB4_PP_WIDTH_RESCALE` default ON (`=0` restores live schedule)
- `SUB4_PP_PEAK` 1275 -> 1274
- `SUB4_PP_R1` 342 -> 340, `SUB4_PP_R2` 625 -> 628
- `SQUARE_LADDER` 245 -> 244

| item | value |
|---|---|
| candidate ops.bin sha256 | 60b6fe451b0cea31c2deffee907c74a1327e175f1adbe9dd41d6e9d76e6ea933 |
| emitted ops | 12,913,783 (semantic; +96 X tail + tail nonce) |
| Q (max id, analyze_ops) | 1274 |
| 64-lane PP_PROFILE diag T | 915,905.50; 0 classical / phase 0x0 / 0 dirty |
| production selftest | PASS: 916,063.359 executed T on its 64-input gate, Q1274 |
| paid-repair census | approx=2290 exact=276 — FEWER approximate repairs than live |
| B0 binding census | pp_div_replay op 2,527,796: tape 340 + y 256 + coeff 256 + u 145 + v 145 + ladder 130 + 2 misc = 1274 |
| est. full T | ~915,882 +/- ~15 (diag - 23.4 offset) |
| score gate (<=919,693) | PASS, margin ~3,800 T |
| predicted score | ~915,882 x 1274 = ~1,166,833,668 (-4.86M / -0.41% vs live) |

Mechanism: ROUNDS was cut 704->698 in earlier accepted commits but the sampled
WIDTH_SCHEDULE was still indexed by raw round, leaving the tail of the walk wider
than the tuned curve at every depth point. `width_round_index` compression
(shipped env-gated, default-off, since the ROUNDS=698 commits) re-maps
round -> round*(703)/(697), recovering the dead bit-rounds: -3,418 diag T at
Q1274 (rescale alone at Q1275: diag 915,609.41, approx=2266). The Q1274 peak cut
itself (PEAK=1274 + SQUARE_LADDER=244) costs +622 diag T of purely EXACT work
(walk splits + narrower exact chunks): the approximate boundary-repair count is
IDENTICAL to live (2313/285) without rescale and LOWER (2290/276) with it. So
this composition adds no new approximate chunk-boundary exposure; the residual
risk channel is the width schedule itself (rescale narrows some walk widths 1-6
schedule indices) — the same channel the fleet's earlier screen on 940e34a
(SUB4_PP_WIDTH_RESCALE candidate, "sound + screen-OK", -4.37M score) already
covered at ROUNDS=698.

## Experiment ledger (all 64-lane deterministic diag, PP_COUNT_PAID censuses)

| # | config delta vs live | Q | diag T | approx/exact | verdict |
|---|---|---|---|---|---|
| 0 | none (baseline) | 1275 | 918995.67 | 2313/285 | matches official receipt |
| 1 | PEAK=1274 SQ=244 | 1274 | 919617.72 | 2313/285 | passes gate; exact-only cost +622 |
| 2 | PEAK=1274 only | 1275 | 919638.27 | — | square still binds 1275 |
| 3 | SQ=244 only | 1275 | 918997.56 | — | square side nearly free (+1.9) |
| 4 | #1 + R2=620 | 1274 | 919683.33 | — | worse; kill R2=620 |
| 5 | PEAK=1273 SQ=243 | 1273 | 920438.20 | 2339/657 | gate-edge (<=920415), approx UP — kill |
| 6 | PEAK=1272 SQ=242 | 1272 | 922113.55 | 2350/1008 | fails gate by ~950 — kill |
| 7 | PEAK=1270 SQ=240 | 1272! | 924242.34 | 2522/872 | schedule can't reach 1270 — kill |
| 8 | #1 + WIDTH_RESCALE | 1274 | 916199.16 | 2290/281 | -3,418; the lever |
| 9 | #8 + R1/R2 grid (12 pts) | 1274 | best 915905.50 @ R1=340 R2=628 | 2290/276 | FROZEN as candidate |
| 10 | #8 + R1=360 / R1=355 | 1274 | +751 / +2757 | 2290/969+ | exact-host blowup above r1~346 |
| 11 | RESCALE only (Q1275) | 1275 | 915609.41 | 2266/287 | score 1,167,335k — worse than #9 |
| 12 | #8 at Q1273 (PEAK1273 SQ243) | 1273 | 917069.08 | 2304/620 | marginal +870 > 719 break-even — kill |

Dead ends recorded: R2=620 (worse both with and without rescale); Q1273 and below
(marginal T cost exceeds per-qubit score break-even, approx exposure rises);
R1 far from 340 (walk-split exact cost explodes).

## Validation status

- [x] Baseline reproduced exactly (full 9024: 0/0/0, T918972.304, Q1275).
- [x] Bake faithfulness: baked binary with `SUB4_PP_WIDTH_RESCALE=0 SUB4_PP_R1=342
      SUB4_PP_R2=625 SUB4_PP_PEAK=1275 SUB4_SQUARE_LADDER=245` reproduces the live
      artifact sha256 d9737f51... byte-for-byte.
- [x] No structural primitive changed (knobs steer existing exact machinery:
      schedule remap, plan geometry, ladder budgets) — no new miter surface; the
      exact split/chunk cells in use are the shipped, previously-accepted ones.
- [x] Production 64-lane self-check (SUB4_PINGPONG_POINT_ADD_SELFTEST): PASS.
- [x] Peak co-binders profiled (B0): single binding profile at pp_div_replay;
      square/mul_replay/mul_walkback all <= 1274 (peak_qubits=1274 global).
- [x] Score gate passed before full eval (est. T915,882 <= 919,693).
- [ ] One inherited-nonce full 9024-shot eval (nonce 251000962439 baked):
      RUNNING — result to be appended below.

## Full-eval receipt (one authorized run, inherited nonce 251000962439)

- artifact sha256 60b6fe451b0cea31c2deffee907c74a1327e175f1adbe9dd41d6e9d76e6ea933,
  12,913,879 loaded ops
- trusted evaluator: **qubits = 1274** (max-id scan confirms the width cut)
- fingerprint: **18 classical / 10 phase / 0 ancilla** over 9,024 shots
- NOT 0/0/0 -> per the pre-registered gate, NO hunt is proposed from this lane;
  the inherited-nonce route is closed. The evaluator exits before printing avg
  T on failure, so the exact full-count T receipt awaits a clean draw; the
  deterministic diag T915,905.50 (offset -23.4, draw SD ~9) prices rounded full
  T at ~915,882, score ~1,166,833,668 (-4.86M vs live).

Calibration context for whoever owns density: the other lane's EXACT L-001 cut
read 13/17/0 on its inherited draw; e928-era fresh-draw calibration on an
accepted-class config measured lambda ~10.9 (1 clean per ~52k nonces).
18/10/0 here is one Poisson-ish draw from a config whose paid-boundary census
is BELOW live (2290 vs 2313) but whose width schedule is ~+3.2 lambda_cls
hotter (the 940e34a rescale screen's number). Density calibration (FN-gated
screener, GPU lane) decides huntability; this lane does not start it.

## Verdict / next binder

The composition stands as the priced Q1274 candidate: it passes the score gate
with ~3.8k T margin where the exact carry-host composition missed by 226, and
it does so with FEWER approximate boundary repairs than the live stream. The
next binder is not schedule geometry (R1/R2/PEAK grid is at a sharp local
optimum; Q1273 is score-negative) — it is the width-violation lambda of the
compressed schedule: a per-round +1-bit repair of the ~6 narrowest rescaled
rounds (SUB4_PP_WSCHED_FILE-style table edit, tooling exists on the 940e34a
lane) could buy back most of the +3.2 lambda_cls for tens of T, well inside
the 3.8k margin. That is the highest-EV next experiment before any fleet
density run.

---

# Lane continuation — rescale-repair (from checkpoint 82a742b)

Objective: keep Q1274/T915905.50 composition, cut the compressed width
schedule's classical-fault density (~+3.2 lambda_cls) with a sparse +1-bit
repair of the narrowest/highest-exposure rescaled rounds.

## R0 — starting candidate reproduced (clean rebuild)

- cargo clean -p quantum_ecc + rebuild at 82a742b; build_circuit emitted
  12,913,879 ops, ops.bin sha256
  60b6fe451b0cea31c2deffee907c74a1327e175f1adbe9dd41d6e9d76e6ea933 — exact
  match to the lane receipt. VERIFIED.

## R1 — tooling recovered (route 1)

- Ported ca85409's byte-neutral tooling from the 940e34a lane, adapted to
  default-on rescale: SUB4_DUMP_WSCHED (dump through real value_width),
  SUB4_PP_WSCHED_FILE (sampled-table override, default-off). Commit 320e278.
- Byte-neutrality re-verified after port: same ops.bin sha256 60b6fe45....
- Schedule dump matches old lane's E5: rescale removes 666 bit-rounds per
  traversal across 457 narrowed rounds.

## R2 — classical fault model validated on THIS stream

- ppfilter binary sha256 f763f770... (the exact binary the 940e34a lane
  screen-validated: 32 nonces, zero FN) with PPF_OPS=<candidate ops.bin>,
  PPF_WSCHED=<effective rescaled schedule from SUB4_DUMP_WSCHED>,
  PPF_ROUNDS_DIV=698, PPF_ROUNDS_MUL=696:
  breakdown @ inherited nonce 251000962439 -> pred_cls=18
  == the paid trusted full-eval receipt (18/10/0). Width channel 12/18.
- Scratch instrumented copy (NOT committed; /tmp only): "deficit" mode
  computes per-shot schedule-independent walk trajectories, records for every
  faulting shot the exact (round, excess-bits) width deficits vs the current
  schedule plus a hard-fault flag for schedule-independent channels
  (terminal/walkback/replay/square-zero/result). Cross-checked per shot
  against the validated shot_fault_mask path: pred=18 xchk=18 at the
  inherited nonce. Because walk trajectories do not depend on the schedule,
  widening-only candidate schedules are exactly evaluable from these deficit
  profiles (widening can never create a new classical fault in the model).
- Key structural observation at the inherited nonce: 6/18 faults have no
  width deficit at all (hard channels), most width-deficit shots are ALSO
  hard-faulted non-converging walks with deficits growing to +8 (unrepairable
  by +1); exactly one shot (4815) is hard=0 with all-excess-1 deficits
  (div rounds 432,444,445,446) — the repairable class.

## R3 — width-violation structure measured (320 fresh classical draws, sample A)

Deficit census on the candidate stream (corpus = its own Fiat-Shamir prefix),
zero cross-check mismatches vs the validated shot_fault_mask path:

- lambda_cls = 15.116 (n=320). Composition of the 4,837 faulting shots:
  1,315 hard-channel only (term/walkback/replay/square-zero/result — width
  repair cannot touch these), 2,007 hard AND width (non-converging walks,
  deficits grow to +8 — unrepairable), 1,515 width-only ("soft").
- Of the soft shots, 795 would be clean under the UNRESCALED schedule
  (rescale-induced repairable lambda = 2.48); 884 are fixable by +1-bit
  widening (2.76 lambda ceiling for any +1 repair).
- KEY NEGATIVE (kills the task's ~6-round hypothesis): the soft faults are
  NOT concentrated. Median repairable shot needs ~3 distinct sampled-table
  indices; best single index fixes 9/884; the best 6-index set fixes 46/884
  in-sample and HALF that out-of-sample (-0.081 lambda for +217 diag T).
  There is no cheap pocket: lambda vs T is a smooth near-linear frontier.

## R4 — repair frontier measured (all clean rebuilds, PP_PROFILE 64-lane diag)

Greedy cost-weighted set cover fitted on sample A (320 draws), validated on
held-out sample B (320 fresh draws); then REFIT on A+B (640 draws) and
validated on held-out sample C (320 fresh draws). All candidates: Q=1274,
peak binding unchanged (pp_div_replay), diag 0 classical / phase 0x0 / 0 dirty.

| set | indices | diag T | dT vs 915905.50 | holdout d_lambda_cls | rate |
|---|---|---|---|---|---|
| c6 (A-fit) | 6 | 916122.78 | +217 | -0.081 (B) | 0.37/kT |
| c40 (A-fit) | 40 | 916332.09 | +427 | -0.500 (B) | 1.17/kT |
| c100 (A-fit) | 100 | 916602.62 | +697 | -0.906 (B) | 1.30/kT |
| c200 (A-fit) | 200 | 917063.78 | +1158 | -1.413 (B) | 1.22/kT |
| r40 (AB-fit) | 40 | 916207.27 | +302 | -0.541 (C) | 1.79/kT |
| **r100 (AB-fit)** | **100** | **916424.62** | **+519** | **-0.947 (C)** | **1.82/kT** |
| r150 (AB-fit) | 150 | 916801.16 | +896 | -1.281 (C) | 1.43/kT |
| r200 (AB-fit) | 200 | 916892.09 | +987 | -1.541 (C) | 1.56/kT |

Uniform tail ranges (+1 on k[a..703]) are strictly worse (~1.0 lambda/kT).
Real diag T per widened index is ~3-36x the naive 3.2/bit-round rate (chunk
layout interactions); all pricing above is measured, not modeled.

## R5 — FROZEN: r100 baked as source default (commit follows)

- `WIDTH_REPAIR` const (100 sampled-table indices, +1 bit each) applied in
  `value_width` on top of the embedded table when the rescale is active;
  `SUB4_PP_WIDTH_REPAIR=0` opts out.
- Bake faithfulness (clean rebuild, byte-for-byte):
  default -> sha256 4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c
  (== the env-driven r100 stream), 12,919,977 emitted ops (12,920,073 loaded);
  SUB4_PP_WIDTH_REPAIR=0 -> 60b6fe45... (starting candidate, exact);
  full opt-out chain (REPAIR=0 RESCALE=0 R1=342 R2=625 PEAK=1275 SQ=245)
  -> d9737f51... (live artifact, exact).
- Gates on baked default: diag T916,424.62 (== pre-bake measurement), Q1274,
  peak_phase pp_div_replay, 0 cls / 0x0 ph / 0 dirty; production selftest
  PASS (916,510.469 executed T on its gate, 1274 qubits).
- Score: est. full T ~916,401 (diag - 23.4 offset) at Q1274 ->
  ~1,167,494,874; still ~-4.19M vs live leader 1,171,689,300. Ceiling margin
  ~3,290 T below 919,693.
- Paid-repair census: NOT re-measured on the repaired stream (census tooling
  was external to this tree); flagged for the density lane.
- ppfilter on baked stream @ inherited nonce: pred_cls=22 (fresh corpus draw
  at lambda ~14.2 — the ops prefix changed, so the corpus is a new draw;
  ensemble receipts below are the metric).

## R6 — receipts on the frozen artifact (commit fe0b7ba)

- Baked-stream ensemble (own corpus, 192 fresh draws, instrumented oracle,
  0 cross-check mismatches): lambda_cls = 13.77 +/- 0.27, vs 15.12/15.09 on
  the unrepaired candidate — measured drop ~-1.3, consistent with (slightly
  better than) the -0.95 held-out estimate.
- One authorized inherited-nonce full 9024 trusted eval (benchmark.sh,
  clean rebuild): loaded ops 12,920,073, **qubits = 1274** (trusted),
  fingerprint **22 classical / 11 phase / 0 ancilla**. Dirty draw as
  expected at this density — per the pre-registered gate no hunt follows;
  the count AND the first failing shot (474) match the ppfilter prediction
  on this stream exactly (pred_cls=22, first=474). Phase channel unmoved
  (10-11 both streams, as with the original rescale).

## Verdict / next binder

FROZEN at fe0b7ba: Q1274, diag T916,424.62 (est. full ~916,401, ceiling
margin ~3.3k), est. score ~1,167,494,874 (-4.19M vs live leader), classical
width-fault density bought down by ~1 lambda for +519 diag T, all gates
clean, three-level byte-faithful opt-out chain preserved.

The task's premise is REFUTED with data: the rescale's extra classical
lambda does NOT sit in ~6 narrow rounds — it is a diffuse population of
1-bit-marginal violations across the whole compressed curve (best 6-index
repair: -0.08 lambda out-of-sample). Density and T trade on a smooth
~1.2-1.8 lambda/kT frontier; r100 is the measured knee. Remaining density
levers if the fleet wants more: r200 (-1.54 lambda, +987 T, measured, Q1274,
tables in this lane's ledger) — beyond that the +2-bit population (~1.1
lambda more) and the hard channels (term/replay, ~12 lambda) bind, which are
not schedule-repairable. Paid-repair census on the repaired stream is the
one unmeasured box (external tooling). Next binder is not the width
schedule: it is phase lambda (~11, untouched by any width move) and the
hard classical channels.

---

# Lane re-descent — PHASE channel (predeclared 2026-08-23, before instrumentation)

Frozen target identity (unchanged): source `fe0b7ba`, evidence `d793aa2`,
HEAD `4aebb8b`, 12,920,073 ops, ops.bin SHA-256
`4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c`, Q1274,
diag T916424.62, inherited full `22/11/0`. Classical predictor is qualified
(gpu-port-q1274-repair-r100); NOT rebuilt here.

## Why phase is now the binding constraint (from existing receipts)

The hunt needs a nonce terminal `0/0/0`. The qualified classical predictor
finds classical-zero nonces (~1 per 10^6); its sole confirmed canary,
`100000035106674`, was terminal `0/2/0` — classical-clean but phase-dirty.
From the 22 FIXTURES.md receipts: 323 classical / 248 phase-shot faults over
198,528 shots -> lambda_cls ~14.7, lambda_phase ~11.3 per 9024-shot eval.
Joint-clean ~ exp(-23) even with the union discount. A phase-channel REPAIR
that zeroes the leak makes every classical-clean nonce a `0/0/0` candidate
(~10^4-10^5x the value of a phase predictor alone), so a bounded reversible
repair is the primary objective; a source-bound exact phase predictor is the
fallback search-economics result.

## Mechanism hypothesis (to be proven exactly, not inherited)

`sim.rs` R/Hmr: `phase ^= qubit(q_target) & rng & cond; qubit &= !cond`. A
lane holding 1 at an R/Hmr free kicks a random phase bit then force-zeroes the
qubit (so it never shows as ancilla garbage). `dirtyscan.rs` asserts:
- **H1 (linchpin):** Hmr dirty-frees are benign — the kickback `q&rng` is
  cancelled by a following bit-conditioned CZ fixup (Gidney uncompute), so
  only unrecoverable `R` dirty-frees produce net phase garbage.
- **H2:** the earliest phase-garbage cause on any fixture is the first `R` op
  (in stream order) that frees a qubit dirty on a live lane.

Predeclared FALSIFIERS:
- H1 falsified if the observed final `sim.phase` on a batch is NOT reconstructed
  by XOR of the R-dirty contribution masks alone (i.e. Hmr/deterministic
  channels contribute net phase). Test: partition every phase-contributing
  event (R-dirty, Hmr-dirty, Z/CZ/CCZ/Neg) by op index and check subset XOR ==
  final phase, per 64-lane batch.
- H2/"earliest" is ILL-DEFINED on any shot where two leaks XOR to parity 0;
  the report will list the full per-shot event set and state whether such
  cancellation actually occurs before naming an "earliest" op.

## Repair-vs-predictor decision rule (predeclared)

Score = round(avg_tof) x qubits; R/Hmr/CZ/CX/Swap are Cliffords and are NOT
scored. Converting a leaking `R` into `Hmr` + a bit-conditioned `CZ` fixup
costs 0 Toffoli and 0 qubits IF the fixup cancels. Cancellation (advisor
algebra): Hmr leaves bit c = rng&cond and kicks phase ^= q_before&rng; a
following `CZ(a,b)` conditioned on c contributes rng & q_a & q_b, cancelling
iff `q_a & q_b == q_before` at the free — i.e. the freed qubit is an
AND-ancilla whose two controls are still live and unmodified at the free.
DECISION:
- If every leaking R site's controls survive unmodified to the free -> the
  repair is ~free on score (T and Q); pursue the bounded reversible repair.
- If controls are recycled (keeping them live costs qubits and Q<=1274 binds)
  -> deliver the source-bound exact phase predictor instead.
Any repair must preserve Q<=1274 and rounded full-eval T<=918822 and keep the
byte-faithful opt-out chain (default-off env restores the frozen artifact).
Must confirm `Op::validate` accepts `CZ` with `c_condition` set (R/Hmr reject
it, per the loader).

## Predeclared corpus (nonces only; non-adaptive)

The 23 nonces with existing ground-truth receipts, drawn only from
FIXTURES.md + the canary receipt. NO new nonce search, NO adaptive selection.

Inherited: 251000962439 (22/11/11/0).
Fixtures 0-4: 216979462201002, 236196892829662, 271225631924494,
  12909430816056, 65511261373299.
Mask-ext 0-15: 248914870509046, 200464614537294, 269472481077161,
  107056343334753, 109186235979289, 12679622957485, 153431043467723,
  30329995037154, 63846899198573, 71599102709711, 205769309325701,
  236213025161514, 117850942287407, 56005648468635, 151276714938924,
  227714064851892.
Canary: 100000035106674 (classical 0, phase-dirty; cls/phase/anc form 0/2/0,
  batches-vs-shots ambiguous — nothing fit tightly to it).

VALIDATION PROTOCOL: the unchanged trusted evaluator (or a logging-only mirror
proven byte-identical in behavior) run over these 23 nonces PATCHED INTO
WHATEVER STREAM IS UNDER TEST. Receipts validate a phase MODEL on the frozen
stream. A repair changes the Fiat-Shamir seed, so each fixture becomes a fresh
draw on the repaired stream — a repair is validated by full-shot re-eval on the
same 23 patched nonces (phase batches must drop toward 0), not by the frozen
receipts.

## Instrument hygiene (predeclared)

- Job A (structural localization): `dirtyscan` via `TLM_DIRTY_SCAN_FINAL=1
  TRACE_OP_SITES=1` (+ CONSTPROP_DISABLE / SINGLE_CCX_FANOUT_DISABLE for 1:1
  op-site mapping) gives file:line of leaking R sites. Those disables REWRITE
  the stream (different count/SHA/seed) so any hit is a POINTER; re-confirm the
  same R site/qubit is a dirty free on the frozen default stream. Re-verify
  ops.bin SHA still 4c68597... after any source edit.
- Job B (exactness on inherited fixture): needs an EXTERNAL logging-only mirror
  of `run_tests` seeded from `fiat_shamir_seed(ops)` (NOT dirtyscan's
  measure_xof). xof order is load-bearing: run_tests draws ALL 2x32B test
  inputs first (including discarded `continue` pairs) THEN Simulator::new
  consumes 8B per R/Hmr. Build the mirror in an external crate — the trusted
  evaluator writes results.tsv/score.json into CARGO_MANIFEST_DIR.
- Keep all experiments opt-in. Do NOT commit ops.bin, results rows, binaries,
  logs, temp evaluators, caches, or artifacts.

---

# Lane re-descent — PHASE channel RESULTS (2026-08-23)

Instrument (NOT committed; external crate in /tmp, path-dep on this worktree):
a logging mirror of `eval_circuit::run_tests` seeded from the REAL
`fiat_shamir_seed(ops)`, cross-checked FAITHFUL against `quantum_ecc::sim::
Simulator` on every 64-lane batch (final qubits/bits/phase asserted equal),
with per-event phase attribution partitioned into {R-dirty, Hmr-dirty,
deterministic Z/CZ/CCZ/Neg}. Runs on the SHA-verified frozen streams
(build_circuit with SUB4_PINGPONG_TAIL_NONCE=<corpus nonce>).

## Source-exactness of the phase model (validated, non-adaptive)

Reproduced `cls/phase-batches/phase-shots` EXACTLY on 6 predeclared corpus
points with zero mirror-vs-Simulator divergences:
- inherited 251000962439 -> 22/11/11 (receipt 22/11/11/0) MATCH
- canary   100000035106674 -> 0/2/2 (receipt 0/2/0; the "2" is 2 batches AND
  2 shots) MATCH; my canary ops.bin SHA = 305663f6... == the receipt's
  "patched survivor operation SHA-256". MATCH
- 236196892829662 -> 16/9/10 MATCH; 271225631924494 -> 6/5/5 MATCH;
  151276714938924 -> 19/16/17 MATCH; 12679622957485 -> 11/5/5 MATCH.

## Mechanism (PROVEN exactly, not inherited)

`free(q)` == `self.r(q)` (mod.rs:502): every qubit free is a bare `R`
measurement with NO fixup; a lane holding 1 at the free leaks a random phase
bit (`phase ^= q & rng`) and is force-zeroed (so it never shows as ancilla
garbage). Measured-erasure uncomputes use the Gidney pattern
`hmr(carry, m); cz_if(a, b, m)` (pingpong_div.rs and_uncompute:1384, carry
uncomputes 820/854/926/1465): the Hmr kick `q_before & rng` is cancelled by
the fixup `rng & (a&b)` EXACTLY when `q_before == a&b`; the residual per site
is `rng & (q_before XOR (a&b))`.

Two DISTINCT phase sub-channels, cleanly separated on the corpus:
1. **Bare-R vent leaks** (R-only XOR reconstructs the whole batch phase,
   hmr^det==0). On the inherited fixture: 8/11 phase-dirty batches
   (15,40,41,55,83,104,110,140). EVERY one is classical-COINCIDENT
   (classical_in_batch>=1, clean_phase_lanes=0). The same gross truncation
   residue that corrupts the result register also dirties the vented qubit.
2. **Gidney measured-uncompute divergence** (hmr^det != 0, single bit ==
   dirty lane, 0 R-dirty events on that lane). Inherited batches 58,68,72.
   THIS is the ONLY channel that produces CLASSICAL-CLEAN phase faults:
   inherited batches 68 (classical_in_batch=0) and 72 (clean lane), AND both
   canary clean shots (lanes 25 and 9). Each is one Gidney site whose
   deliberately-truncated carry (pingpong_div.rs:1364 "the carry window is the
   deliberately measured approximation") did not equal its control-AND, so the
   fixup CZ failed to cancel.

## Repair vs predictor — DECISION: source-bound exact phase model (predictor)

A "free" reversible repair (advisor's R->Hmr+CZ) requires the freed value to
be a reconstructable clean `a&b` with surviving controls. It does NOT apply
here: the phase-leaking frees carry APPROXIMATE-ARITHMETIC RESIDUE (a
deliberately truncated carry), not a clean AND — the Gidney fixup already
EXISTS at these sites and fails precisely because the value is wrong. Zeroing
the leak == making the truncated carries exact == the WIDTH channel, which is
Q<=1274/T-bound and already exhausted (see r100 frontier above). Confirming
data: the r100 width repair cut classical lambda ~1 but left phase UNMOVED
(10-11) — because it widened result-hotspot indices, NOT the carry sites that
feed the measured-uncompute frees. So classical and phase are two different
projections of the same truncation residue at DIFFERENT sites.

Delivered: the external mirror is a SOURCE-EXACT phase model (both channels,
validated on 6 corpus points + canary + inherited). It is exact but costs a
full sim (~26s/nonce), so it is a diagnostic/screening oracle, not a
cheaper-than-eval predictor. Score contract note: R/Hmr/CZ/CX/Swap are
Cliffords and UNSCORED (score = round(avg_tof) x qubits); the T<=918822 room
is ~irrelevant to any Clifford-only phase fix — but no such fix exists because
the fault is a wrong VALUE, not a missing gate.

## Falsifiers and next bounded overturn (predeclared)

- REPAIR-REJECTION FALSIFIER (would overturn "predictor"): a free/uncompute
  site that leaks on a classical-clean shot UNDER EXACT ARITHMETIC (a
  structural bug, not truncation). Cheapest test: run the mirror on a stream
  with the phase-leak carry sites widened to exact and check if any
  classical-clean phase fault survives. If zero -> all phase leaks are
  truncation residue (predictor confirmed); if nonzero -> a Clifford-only
  reversible fix exists at that site. Not run here (no single "exact
  arithmetic" switch; full exactness blows Q).
- NEXT BOUNDED OVERTURN (positive-EV, blocked by corpus, NOT run): a TARGETED
  carry-width repair of only the Gidney sites that diverge on CLASSICAL-CLEAN
  shots would raise hunt yield within the ~2,400 T ceiling room (at the
  measured ~1.5 lambda/kT that is ~3.6 lambda, but the clean-conditioned phase
  lambda is only ~2, so a few hundred T could roughly halve it). BLOCKED: it
  needs a CLASSICAL-CLEAN-CONDITIONED carry-divergence census, and the fixed
  23-nonce corpus contains only ONE classical-clean member (canary, 2 shots) —
  insufficient to fit, and adaptive nonce search is forbidden. This is the
  hand-off: with an authorized classical-clean sample (from the qualified
  classical predictor's survivor stream, no new grind), census the
  clean-conditioned Gidney-divergence carry sites and price a targeted widen.
- FAST PREDICTOR (search economics, NOT built): phase parity factors as
  XOR over measured-uncompute sites of (per-site truncation-divergence &
  rng-bit). The divergence mask is the schedule-independent walk profile the
  qualified classical model already computes; bolting a per-free rng draw +
  parity accumulator onto it would yield a sub-eval phase screen. Falsifier:
  if the per-site divergence does NOT factor cleanly onto the classical
  model's state (needs extra carry state the model discards), the predictor is
  not cheaper than the mirror and the diagnostic oracle stands as the result.

## Verdict

Phase channel re-descended and fully mechanised: two sub-channels (bare-R vent
= classical-coincident; Gidney measured-uncompute divergence = the sole
classical-clean channel, hence hunt-binding). Both are approximate-arithmetic
truncation residue at frees, not repairable by any Clifford-only reversible
fix; zeroing them is the exhausted Q/T-bound width channel. A source-exact
phase model (the mirror) is delivered and validated on 6 corpus points. The
priced next step is a targeted carry-widen of the clean-conditioned Gidney
sites, blocked only by the fixed corpus's single classical-clean member.
