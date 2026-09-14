# PRO closeout — Pareto head-to-head 2026-09-14

Role PRO, model deepseek-v4-pro, effort max (resumed context verified via
`ps` launch flags). Session 01a0a139-9e50-75a1-987c-24314aabc050.
START 2026-09-14T18:55:43Z, DEADLINE 2026-09-15T02:55:43Z (immutable).

## Result

**NO NEW VERIFIED PARETO POINT** was submitted by PRO in this window.
Two load-bearing construction pieces for the Q792 leftward move were derived
and exactly verified; the third (the fourth omitted Work1 rail) is precisely
blocked on a geometric A-cargo issue and is the named next phase.

## Bound parent and binding evidence

- Official parent: 88dc9f4 (welttowelt) Q793 / T682,564,189.
- Worktree: /Users/odin/DeepSeek/pareto-head-to-head-20260914/worktrees/pro-bench
  branch codex/pro-20260914. Baseline commit 38c7fe6b (reset 88dc9f4 onto
  harness 9700396).
- Local binding: whole-count census reproduces the canonical exactly:
  peak=793, ops=1,243,369,959, structural_T=692,077,100.
- Live frontier recomputed at 18:56Z from 1,227 public rows: Q<=791 unclaimed;
  low-Q envelope (792, 893,988,754), (793, 682,564,189), (794, 415,821,960),
  (795, 300,862,444), (807, 276,427,457), (822, 250,088,365).

## Peak anatomy (named-peak census, TRACE_NAMED_PEAK_TARGETS=793)

Five distinct 793 plateaus:
- families 0/1/2/4 (EEA step/rebuild, fwd+cancel):
  work1=256 phys + work2=259 + passenger=256 + rank5 state=22 = 793.
- family 3 (cancel-path mod_mul/undo): quotient-check=257 + dy=257 + tx=255
  + halve ancillas 13 + state 9 = 793.

## Route pro-q792-peak verdicts

- H3a (+2 dirty-helper loan): REFUTED by census. Peak counts ALLOCATED lanes;
  helpers alias allocated passenger lanes, so lending more does not move Q.
- Family-3 quotient-top borrow (`Q792_QUOTIENT_TOP_BORROW`): VERIFIED
  (whole-count named census): every mod-mul family drops 793 -> 792.
  Cost at Q793: ops +537,854, structural_T +267,008 (T-negative alone; it is
  the family-3 half of Q792).
- mod16 exit chart (q792_mod16.rs): VERIFIED exhaustive in Rust selftest
  (65,536 lanes: 4096 codes x 2 guards x 8 dirty patterns; T=2644 exact,
  literal inverse and phase 0, dirty restored). Composition:
  k3 chart on low planes o conditional affine plane-3 map o reachability-
  gated constant plane. Derivation: runtime/pro-k4-chart-derivation.md.
- Fourth omitted rail (work1 255 phys + 4 holes): BLOCKED (ADMIT next phase).
  Geometric blocker: A-value gather space needs 255 lanes (v=0..254);
  with hole at w1[255] and four chart wires w1[0..4), w1 offers 251 lanes
  and w2[256..258] offers 3 -> 254 total; A=254 has no physical home.
  Resolution requires re-deriving the per-offset sentinel/parking exclusions
  (v = 255-offset loses its w1 lane at each gather offset), parking those
  A-cargo values in the sm/parking protocol, and refitting A_SUPPORTS.

## Source hashes

- baseline: 38c7fe6b (verified canonical Q793 binding)
- probes: d682ea31 (q792_mod16 chart + Q792_QUOTIENT_TOP_BORROW flag, OFF by
  default)
- chart contract fix: f9fbe19a (7-dirty contract, exhaustive selftest pass)
- final HEAD: <fill at closeout>

## Resource use

- 48 GiB host / 16 cores. Count-only censuses ~25 min each, ~1 GiB RSS.
- Heavy lock discipline: acquired/released per job (builds, full counts).
- No submission was made by PRO; no official receipt.

## Best next experiment (ADMIT)

Implement the fourth rail as a new LOWQ_Q792_EEA lifecycle: (1) resolve the
A=254 (and offset-shifted 255/254/253/252) cargo homes via the existing
parking protocol; (2) swap q793_mod8 for the verified q792_mod16 chart in
q793_metadata_exit; (3) refit A_SUPPORTS for the 255-physical geometry;
(4) gates: whole-count peak==792, whole-stream 0/0/0, whole-9024, refreeze,
submit under the shared submission lock. With the chart and borrow already
verified, this is the only remaining structural piece for Q792.
