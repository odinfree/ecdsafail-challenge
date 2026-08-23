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
