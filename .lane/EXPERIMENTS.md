# Experiments ledger — fable-width-rescale-940e34a

All runs local, on this worktree at HEAD=940e34a, stock binaries unless
stated. Trusted evaluator = this tree's `eval_circuit` (stock) or the
ppfilter-rl tree's `evalall` (same trusted core, prints every mismatch —
measuring instrument only, never a submission vehicle).
Oracle = pinned ppfilter sha256 f763f770...5f58128 at
/Users/olifreuler/ecdsa-ppfilter-rl/target/release/ppfilter with
PPF_ROUNDS_MUL=696 (+PPF_WSCHED for width-modified streams).

## E0 — baseline reproduction (2026-08-23)

Default build: ops 12,918,089, md5 2476648bade253b539b41bbc2e230b7b
(== promoted candidate fingerprint). Stock eval: 9024/9024, 0/0/0,
avg executed T 917,480.917, Q1278 → score 1,172,540,718 == live gate. PASS.

## E1 — rescale fingerprint + pricing (6 draws)

Config: `SUB4_PP_WIDTH_RESCALE=1`, everything else default.
Stream: ops 12,864,810 (−53,279 emitted), Q **1278** (unchanged) on all
draws. Baked-nonce stream md5 09b1e83b6b438b31b6cd956389074f99.

| nonce | cls | ph | anc | avg exec T |
|---|---|---|---|---|
| 176078461220 (baked) | 16 | 9 | 0 | 914,069.758 |
| 6000000000 | 16 | 10 | 0 | 914,069.295 |
| 6000007919 | 18 | 11 | 0 | 914,064.653 |
| 6000015838 | 18 | 15 | 0 | 914,050.937 |
| 6000023757 | 17 | 13 | 0 | 914,060.825 |
| 6000031676 | 18 | 9 | 0 | 914,064.022 |

Mean T ≈ **914,063.2** → ΔT ≈ **−3,417.7** → Δscore ≈ **−4,368,000
(−0.373%)** at Q1278 (live gate 1,172,540,718 re-verified unchanged
2026-08-23 ~01:35Z). The 8.08M figure from the 6b5c probes was
R694-geometry-specific (schedule stops 10 rounds short there vs 6 here);
it does NOT transfer to 940e34a. λ_cls mean **17.17**, λ_ph mean **11.17**
(n=6). NOTE: the rescale-vs-base PHASE claim ("phase ~flat") is n=6-vs-n=6
only — base phase (11.50) was never powered, so treat "phase unchanged by
the width lever" as suggestive, not established. It is load-bearing for E10.

## E2 — baseline fault rate, paired protocol (6 draws, same nonce family)

Default config, nonces 6000000000+k*7919:
cls = 13,17,13,13,16,13 → λ_cls **14.17**; ph = 10,15,13,7,13,11 →
λ_ph **11.50**; anc 0/6.

**Δλ_cls(rescale) ≈ +3.0 ± ~2.3 (n=6 each); Δλ_ph ≈ 0.** Phase is
width-neutral (matches WSCHED-MODEL-COUPLING: width couples only into the
walk pop/wrap checks). Prior "+9λ" ban (R696 era) and "29 vs 22" (6b5c
combined) were unpaired/legacy-geometry readings.

## E3 — oracle agreement (the lane's core gate)

ppfilter + PPF_WSCHED=<rescaled 700-row CSV> + PPF_ROUNDS_MUL=696 against
the exact 940e34a+rescale stream:

- Counts: 6/6 exact (16,16,18,18,17,18 = measured).
- Base stream (embedded leader table): 6/6 full per-shot mask MATCH
  (predicted faulting-shot index sets == trusted evalall sets).
- Wrong-table canary: rescaled CSV vs base stream → pred 15 ≠ measured 13:
  the table override demonstrably couples into predictions.
- 32-nonce full per-shot mask agreement on the rescale stream: RUNNING.

The "PPF_WSCHED undercounts width faults / failed 0/64" wall is refuted
for the SPECIFIC tested binary — macOS ppfilter sha256
f763f770527117be409123ae23ab8ceeecac1d5b8d7ee4e698d468f375f58128 — on this
base. The g1000 0/64 was a stale fleet binary silently ignoring PPF_WSCHED
(ppfilter CALIBRATION.md addendum), NOT a model gap. IMPORTANT for the
fleet: because the original failure was binary staleness, this soundness
result does NOT transfer to a fleet host running an older ppfilter — a
canary-hash gate before promotion (already instituted per CALIBRATION.md) is
mandatory. "Screen sound" here means "this binary, this stream, verified" —
not "any binary."

## E4 — rescale λ decomposition (ppfilter breakdown, 6 nonces)

width ≈ **13.0** (vs ~5.5 leader-table), term ≈ 0.83 (vs ~2.9 — narrower
tail converts would-be terminal faults into width faults first), replay
folds ≈ 3.3, walkback 0, shell 0. The surplus is width-dominated as
expected; no hidden channel.

## Schedule fingerprint

Rescaled 700-row CSV regenerated from THIS tree's source
(WIDTH_SCHEDULE unchanged since 9805dee; only CC 22→20 + nonce changed):
CSV sha256 d1700e214dadd4554b941432b682f3f8d82cdc7fb68472c5ff31facc9c8560ed,
u16le sha256 843d0c2d7c04bb8aad7d4c0323d2a24bdc04b675310a616440fbc2f4e6e06595
(identical to the Q1274 pilot's frozen artifact). Row-for-row verified
against an env-gated `SUB4_DUMP_WSCHED` dump through the real `value_width`
code path in `build_circuit`: 700/700 rows equal (see E5). [NOTE: an earlier
attempt via `cargo test --lib` was VOID — the dump test lives in the
`point_add` tree compiled only into the build_circuit bin, whose test target
has 165 pre-existing compile errors, so it silently ran 0 tests. Corrected
with the build_circuit dump path.]
Rescale factor is 703/697 for BOTH traversals (multiply also indexes via
`rounds()`), which the CSV encodes.

## E5 — schedule verification + executed-round Σ (real code path)

`SUB4_DUMP_WSCHED=1 build_circuit` dumps base+rescale widths through the
actual `value_width`. Rescale column == generated CSV: **700/700 rows**.
Σ over EXECUTED rounds (divide 0..697, multiply 0..695):

| traversal | base Σ | rescale Σ | Δ bit-rounds |
|---|---|---|---|
| divide (0..697) | 98,482 | 97,816 | −666 |
| multiply (0..695) | 98,466 | 97,800 | −666 |
| **both** | 196,948 | 195,616 | **−1,332** |

WSCHED.md rate (measured on this geometry): +3.20 executed T / bit-round →
predicted ΔT −4,262; measured ΔT −3,418 (0.80×). The reindex removes width
UNIFORMLY-IN-INDEX, not where census slack is largest.

## E6 — zero-false-negative bound (replaces the mis-sized boundary scan)

The pred≤4 boundary scan was mis-sized (P(cls≤4) at λ≈17 ≈ 1.6e-4/nonce;
401 nonces → E[hits] 0.06; pred=0 ≈ 3.4e-8 is unreachable locally — that
regime IS the fleet hunt). Killed it. Stronger claim from data in hand:
the per-shot mask run reached **24/32 nonces before an OOM kill** (the shared
machine was running another lane's evals concurrently), giving 24×9024 =
**216,576 exact shot-level predictions with 0 disagreements** (no FP, no FN,
all 24 MATCH). Rule-of-three 95% UCB on the per-shot disagreement rate ≈
3/216,576 = **1.39e-5**.

Translated to hunt economics (framing from cross-lane peer, adopted):
- FALSE POSITIVES ARE FREE — every screen survivor gets a trusted full-shot
  confirm, so a spurious "clean" costs one eval, not a lost win.
- Only FALSE NEGATIVES cost. Over 18,048 walk decisions/nonce at the 1.39e-5
  UCB, P(a truly clean nonce survives) ≥ **0.779**, i.e. an FN hunt-cost
  multiplier ≤ **1.28×**. Negligible against the ≥6× margin gaps between
  candidates.
- Structural bound on "unmodelled channel": a channel absent from the model
  would undercount at EVERY count level, not only at zero; 0 disagreements
  across 216k decisions at counts 13–25 bounds that hard. Residual risk is
  ordinary per-shot model error, not a missing mechanism.
CAVEAT retained: shots within a nonce share one code path; the pred=0 regime
the fleet hunt actually consumes is not directly reachable locally.

## E7 — reconciliation of the base λ gap (advisor flag)

Advisories quote base 940e34a "19.8 (n=5, measured as cc20)" and "22.1
(n=10)"; my paired base is cls 14.17 + ph 11.50 = combined **25.67** (n=6).
Independent cross-lane data (Einstein_Claude, 2026-08-23) reads base
cls 14.2 + ph 12.8 = **27.0** (n=4) — matching mine, not the 19.8. The 19.8
was a different config (cc20) and/or a classical-mostly convention. The
load-bearing number (combined λ ≈ 26–27 base, ≈ 28 rescale) is now
corroborated across two independent lanes. WR-alone margin also matches
cross-lane: mine −4,368,000, Einstein's −4,366,926.

## E8 — greedy-table head-to-head (channel-split, powered)

Measured on 940e34a, all Q1278 (verified from all 15 logs — no peak
movement), via the byte-neutral SUB4_PP_WSCHED_FILE hook.

n=5 paired trusted (nonces 6e9+k*7919):
| table | ΔScore vs gate | cls λ (n=5) | phase λ (n=5) |
|---|---|---|---|
| base | 0 | 14.2 | 11.5 |
| greedy_m452 | −1,396,854 | 16.6 | 16.0 |
| rescale | −4,369,482 | 17.4 | 11.6 |
| greedy_m1000 | −4,851,288 | 18.6 | 13.2 |

Powered classical (oracle, n=500 paired, nonces 6.1e9+k*7919; oracle first
reproduced my 5 held greedy1000 trusted counts 21,16,17,24,15 EXACTLY):
| table | mean_cls | ±SE |
|---|---|---|
| rescale | 14.594 | 0.172 |
| greedy_m1000 | 19.472 | 0.192 |
→ Δλ_cls = **+4.88 (greedy1000 higher), t≈19, decisive**.

RESULTS, by strength of evidence:
1. Rescale strictly dominates greedy_m452 (3× the score, −4.37M vs −1.40M) —
   settled on the SCORE axis alone regardless of λ. SOLID.
2. Rescale vs greedy_m1000 CLASSICAL: rescale is +4.88 λ_cls LOWER (powered,
   decisive). But under a classical-prescreen pipeline this advantage is
   largely absorbed as cheap scans (E10).
3. Rescale vs greedy_m1000 SCORE: greedy_m1000 leads by a CERTAIN +490k
   (deterministic, nonce-stable).
4. Rescale vs greedy_m1000 PHASE (the binding channel under a screen): n=5
   diff only +1.6, t≈1.6 — NOT separated. Powering with 24 paired draws (E8b).

CORRECTION (twice-revised, logged for honesty): (a) an early draft called
rescale "dominated" — false, interpolated from WSCHED walk-only λ. (b) the
next draft over-corrected to "rescale is the BEST operating point / stack on
rescale not greedy1000" — that rested on a COMBINED-λ n=5 gap of +2.8 that is
t=0.99, p≈0.38, i.e. NULL, while greedy1000's +490k score is certain. Both
were headline-stronger-than-caveat (advisory-calibration gate 2). The honest
label: rescale dominates greedy452; rescale vs greedy1000 is a genuine
tradeoff — rescale much lower CLASSICAL λ (screenable), greedy1000 higher
certain score; phase pending. Retracted to peer c9.

## E8b — powered phase + combined (24 paired trusted draws)

Nonces 6.2e9+k*7919, k=0..23, rescale vs greedy_m1000, all trusted evalall:

| channel | rescale | greedy1000 | diff (g−r) | t | verdict |
|---|---|---|---|---|---|
| classical λ | 14.96 | 19.54 | +4.58 | (n=500 oracle: +4.88, t≈19) | decisive |
| phase λ | 11.25 | 13.42 | +2.17 | 1.79 (p≈0.09) | marginal |
| combined λ | 26.21 | 32.96 | **+6.75** | **4.04** | **decisive** |

SETTLED: greedy_m1000 has decisively HIGHER combined λ than rescale
(Δ+6.75, t=4.04) for a CERTAIN +490k more score. So rescale IS the better
operating point of the two — the n=5 combined gap (t=0.99) was underpowered,
not absent; at n=24 it is real and sizable. The economic read splits by
pipeline (E10):
- Un-screened full-eval: rescale wins big (Δ6.75 combined ≈ e^6.75 ≈ 850×
  cheaper hunt) for −490k score. Clear rescale win.
- Classical-prescreen (phase-limited): classical absorbed; binding channel
  is phase, where rescale's edge is only MARGINAL (Δ2.2, p≈0.09 ≈ 9×). vs
  greedy_m1000's +490k certain score, this is a closer call that hinges on a
  p≈0.09 phase advantage. Honest: lean rescale, but not locked under this
  pipeline.

Mechanism (per Einstein): width→phase coupling is via
`allowance = plan.peak − (tape_len + 2N + 2·walk_width)` feeding the replay
chunk ladder (phase-only repairs) — measured per table, NOT inferred from
"smoothness". rescale's lower phase is empirical (marginal), not structural.

## E9 — dose-response soundness (Einstein cross-lane, adopted)

The SCHED_BIAS cliff discriminator (my local run was starved by machine
contention; Einstein's red-team returned it first, and it matches my
structural read): trusted-eval bias sweep on the leader/rescale tables —
bias +1 → 18.7, base → 24.2, rescale → 27.6, bias −1 → CLIFF 4,741–4,788 cls
+ all 141 phase batches dead, −2 → 8,961, −3 → 9,024. The cliff exists
because the leader table sits AT the census max in rounds 1–25; a uniform −1
breaks exactly those. The rescale index shift is <1 round until ~round 100,
so it never enters the cliff region. Confirms rescale is a SOUND width cut
(ordinary huntable width-violation dirt), NOT a FOLD_WINDOW-class
deleted-arithmetic trap — corroborated by my E4 (faults are width-channel,
nonce-varying 13–25) and E3 (model predicts them exactly, which
deleted-arithmetic faults would not be).

## E10 — hunt economics: PIPELINE-DEPENDENT, not a free lever

CORRECTED after cross-lane challenge (Einstein_Claude) + skeptical re-read.
An earlier draft here claimed rescale's marginal hunt cost is ≈0.72×. That
was an EV-overclaim resting on an unverified pipeline assumption. The honest
statement is conditional:

Rescale's classical Δλ ≈ **+3.1** (my E2 +3.0; Einstein 128-nonce +3.11±0.44;
census ε 1.89× leader). Phase Δλ ≈ 0 (unchanged, both lanes). The COST of
that +3.1 depends entirely on the fleet's pipeline:

- **If the fleet full-evals every nonce** (no classical prescreen): the hunt
  is governed by combined λ, so rescale costs ≈ e^3.1 ≈ **22× more full
  evals** than base. The standing advisories' "1 in 3.7e9" hunt figure ≈
  e^(combined λ) — consistent with THIS pipeline being the operative one.
- **If the fleet classical-prescreens then confirms survivors** (ppfilter
  scan → trusted eval): the expensive full-eval count is phase-limited
  (Δλ_ph≈0), so rescale's marginal full-eval cost ≈ **1×**, and the +3.1 is
  ~20× more CPU-cheap scans (× a ≤1.28× FN penalty from E6).

I do NOT know which pipeline the fleet runs, so I do not assert a single
multiplier. THIS LANE'S ACTUAL DELIVERABLE on economics is narrower and
solid: the classical width screen is **sound on the rescale stream** (E3/E6),
which is the precondition that UNLOCKS the cheaper prescreen pipeline. Whether
to adopt it is a fleet-ops decision I don't own. Take Einstein's 22× as the
conservative (un-screened) price; the screen is how you'd beat it.

Applies to the whole width-table family — so the greedy-vs-rescale choice
(E8) is about maximizing score per unit Δλ, independent of pipeline.

## Frontier context (prior art, 7ca0559 geometry == this geometry)

WSCHED.md (q1275-packet): +3.20 executed T per bit-round; leader table has
zero fat vs 1e8 census; greedy (Σ,ε) WALK frontier: −452 bits → λ_walk 6.9,
−1000 → 11.4, −2000 → 27.6. NOTE: those λ_walk figures are the WALK sub-
channel only. E8 shows they do NOT predict the full trusted λ — the greedy
tables carry a phase penalty the walk census never modeled, so on the full
score+λ measurement rescale beats them (see E8). Prior-art framing kept for
provenance; superseded by E8's direct 940e34a measurement.
