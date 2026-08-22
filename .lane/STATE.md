# Lane: fable-width-rescale-940e34a

Owner: Fable 5 (background lane). Scope: structural/modeling attack on
`SUB4_PP_WIDTH_RESCALE=1` at exact source `940e34a`. No submission, no
provider/fleet actions, no spend. Local bounded work only.

## Anchor (verified live 2026-08-23 ~00:00Z)

- Live promoted head: submission `38563a2` (welttowelt), commit `940e34a`,
  score **1,172,540,718** = Q1278 x T917,481 (avg executed 917,480.917).
- This worktree HEAD == 940e34a, branch `research/fable-width-rescale-940e34a`.
- Baked defaults at 940e34a (read from source, not notes):
  ROUNDS=698, ROUNDS_MUL=696, REPLAY_CHUNK=96, CHUNK_COMPARE=20,
  FOLD_WINDOW=54, ENDPOINT_FOLD_WINDOW=20, FLAG_COMPARE=22,
  R1=356, R2=625, PEAK=1278, tail nonce 176078461220.
- 940e34a vs 6b5c82c: ROUNDS 694->698, CC 22->20, EFW 26->20, new nonce.
  **The ~8.08M rescale projection was measured on 6b5c's R694 geometry and
  does NOT transfer; on R698 the prior-base measurement was ~3,482 exec T.**

## The lever

`SUB4_PP_WIDTH_RESCALE=1` compresses the width-schedule index by
`round * (704-1)/(rounds()-1)` (pingpong_div.rs:39-48) so the sampled
700-row WIDTH_SCHEDULE reaches its floor at the actual round count instead
of stopping short. Both traversals index via `rounds()` (=698), including
the 696-round multiply — the rescale factor is 703/697 for BOTH.
T saving: narrower per-round adds across walk+replay. Fault cost: eats
envelope margin on slow-converging shots (width violations).

## Prior evidence (provenance-checked)

- ADVISORY-20260822-2300 (9805dee, R698): rescale alone Q1278,
  T 916,261 (n=11) vs 919,754 base; fault 24.2 vs 22.1.
- NEXT-STEP-20260823 (6b5c82c, R694): rescale alone -8,083,350 score,
  fault 29.0 vs 22.0 (~1,100x hunt). Flagged "do not deploy until the
  width model is fixed", citing the g1000 0/64 PPF_WSCHED failure.
- ppfilter CALIBRATION.md addendum (2026-08-22 PM): the g1000 0/64 was
  root-caused as a STALE FLEET BINARY silently ignoring PPF_WSCHED; fixed
  model is 64/64 exact on g1000, 64/64 on rl-696, canary-clean. The
  "model undercounts width faults" claim is UNRESOLVED-vs-SUPERSEDED —
  settling this on the exact 940e34a+rescale stream is this lane's job.
- Q1274-PILOT-GATE (9805dee + PEAK/SQ/R1/R2 + rescale): CPU oracle
  reproduced 5/5 trusted counts and 15/15 failing-shot indices through
  PPF_WSCHED rescaled CSV. So the PPF_WSCHED path has already agreed once
  on a rescaled stream — evidence against a structural model gap.

## VERDICT (calibrated 2026-08-23)

**SUB4_PP_WIDTH_RESCALE=1 on 940e34a = CANDIDATE (not GO).**

- WHAT IT IS: a sound, correctly-priced, classically-screenable width-schedule
  CUT worth **−4,369,482 score** (ΔT −3,419 avg-Toffoli at Q1278 unchanged;
  gate 1,172,540,718 RE-VERIFIED live 2026-08-23 ~01:35Z, unchanged),
  costing **+3.2 λ_cls; phase Δ vs base ≈ 0 (n=6 only, NOT powered — base
  phase 11.5 was never re-measured at scale)**. Strictly dominates census
  greedy_m452 (3× score, lower λ). Vs greedy_m1000 (powered, E8b n=24):
  rescale has DECISIVELY lower combined λ (Δ+6.75, t=4.04) — classical Δ+4.6
  decisive (oracle n=500 Δ+4.88), phase Δ+2.2 marginal (t=1.79, p≈0.09).
  greedy_m1000 leads on CERTAIN score by +490k (0.04%). Net: rescale is the
  better operating point — greedy1000's tiny score edge costs 9–850× hunt by
  pipeline. Direction matches the earlier "rescale better" read, but that was
  only JUSTIFIED once powered to n=24; n=5 combined (t=0.99) was underpowered.
- SOUND, not a trap: E4 (faults are width-channel, nonce-varying 13–25),
  E3 (model predicts every count exactly — a deleted-arithmetic trap would
  not be predictable), E9 (dose-response: rescale sits far from the bias −1
  cliff). Contrast FOLD_WINDOW/SCHED_BIAS which delete required arithmetic.
- SCREEN: the classical width-fault screen (ppfilter PPF_WSCHED path) is SOUND
  on this stream — the task's "undercounts / failed agreement gate" premise is
  REFUTED (stale-binary incident, since fixed). Bounded FN ≤1.28× at counts
  13–25; pred=0 regime is the fleet hunt, untestable locally.
- DOMINANT UNDISCHARGED GATE: an actual **0/0/0 clean nonce** does not exist
  yet — that hunt is fleet-scale (phase-limited ~e^11.6 full-evals per clean;
  or 22× base if the fleet full-evals un-screened). This lane does NOT hunt,
  submit, deploy, or spend. To ship it a human would bake the winning nonce +
  the env as source defaults at mod.rs build() and pass the full 9024 gate.
- NOT a burn-scale move: it lives inside the pingpong width-schedule surface.
  The structural prize (walk/replay fusion, tape peak ~30–50%) is untouched
  and out of this lane's scope.
- COMPOSES with the sibling q1275 peak-cut packet (additive, interaction
  −5.75 T per Einstein) → stack on rescale, not on greedy1000.

## Objectives (in order)

1. Reproduce baseline 940e34a: ops fingerprint + trusted eval 0/0/0,
   T 917,480.917, Q1278.
2. Fingerprint + price rescale on 940e34a: emitted ops, md5, Q, avg T and
   per-channel faults over >=5 fresh draws. No single-draw ranking.
3. Generate the exact rescaled width CSV from THIS tree's source; verify
   row-for-row against a source-extracted value_width dump (both
   traversals, incl. round-0 pin and >=700 floor).
4. Agreement gate for ppfilter PPF_WSCHED on the rescale stream:
   n>=32 nonces exact classical counts + failing-shot indices, boundary
   cases (pred 0..4), zero false negatives. Wrong-table canary must move.
5. Verdict: viable hunt packet spec (config, stream digests, schedule
   hash, lambda economics, screen receipt) OR a documented kill with the
   exact failing channel.

## Status log

- 2026-08-23 00:xx UTC: lane opened; doctrine + live CLI re-read; prior
  evidence located and provenance-checked.
- Baseline E0 reproduced: md5 2476648..., 0/0/0, T917480.917, Q1278 == gate.
- E1 rescale priced on 940e34a: ΔT −3,418 (−4.37M score), Q1278, +3λ_cls,
  λ_ph flat. NOT the 8.08M 6b5c figure (that was R694 geometry).
- E3/E6 PPF_WSCHED screen SOUND on this base: 6/6 counts, 21/32 masks
  0-disagreement (~190k shot decisions), wrong-table canary moves. Task
  premise ("screen undercounts/failed agreement gate") REFUTED — the g1000
  0/64 was a stale fleet binary (CALIBRATION.md addendum), fixed binary
  64/64. Zero-FN 95% UCB ≈ 1e-5 (pred=0 regime untestable locally).
- E5 schedule verified through real code path (700/700); Σ −1,332 bit-rounds
  total (−666/traversal), a smooth reindex of the leader table.
- E8 greedy head-to-head (940e34a, all Q1278): rescale DOMINATES greedy_m452
  (3× score, lower λ — solid). Rescale vs greedy_m1000 is a genuine tradeoff:
  classical λ decisively favors rescale (n=500 oracle 14.6 vs 19.5, Δ+4.88,
  t≈19) but greedy_m1000 leads on certain score (+490k); phase channel
  pending (E8b, 24 paired draws). Two prior drafts were miscalibrated (first
  "dominated" from walk-only census; then "BEST" from a null n=5 combined-λ
  gap, t=0.99) — both retracted to peer c9. Oracle reproduced my 5 held
  greedy1000 trusted counts exactly (calibration confirmed on this stream).
- E9 dose-response (Einstein cross-lane): rescale is a SOUND width cut, not
  a deleted-arithmetic trap — bias −1 cliffs at 4,741 cls; rescale's <1-round
  index shift never enters that region.
- E10 hunt economics are PIPELINE-DEPENDENT: 22× un-screened (Einstein's
  honest price) / ~1× if the fleet classical-prescreens (the screen this lane
  validated is what unlocks that). Earlier confident "0.72×" was corrected.
- Added byte-neutral tooling: SUB4_DUMP_WSCHED (schedule dump),
  SUB4_PP_WSCHED_FILE (runtime table override). Default md5 unchanged after
  all edits (re-verified 2476648...).
- Sent blocker-2 clearance + additivity/FN acks to advisory lane
  claude-code-c9.
- Provenance correction: an earlier `cargo test --lib` schedule check was
  VOID (0 tests ran — bin test target has 165 errors); redone via
  SUB4_DUMP_WSCHED. Ledger corrected.
