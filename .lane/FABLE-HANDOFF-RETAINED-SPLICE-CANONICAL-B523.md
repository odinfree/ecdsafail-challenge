# Handoff — canonical retained-word splice (B523)

Written: 2026-08-23. Lane: `research/b523-retained-splice-canonical`.
Predeclaration: `.lane/PREDECLARATION-RETAINED-SPLICE-CANONICAL-B523.md`.
Model authority: read/edit this lane only. No builds, commits, pushes, network,
providers, hunts, submission paths, `SPEND.md`, or public notes were touched.

Human adjudication after independent execution: the rounds-2..7 slice passes
exactly, but it covers only 6/1390 production fused calls and therefore does not
satisfy the predeclared complete NM64 fixture. The lane is terminally killed at
that coverage gate; see `.lane/KILL-RETAINED-SPLICE-CANONICAL-B523.md`. This
handoff is retained as the model's bounded implementation record, not as a HOLD
or authorization for an oracle-extension lane.

## What was implemented (one family, one gate)

All new behavior is behind the single env gate `SUB4_PP_RETAINED_SPLICE_CANONICAL`
and dispatches to `pingpong_div::retained_splice_canonical_selfcheck()`
(`src/point_add/mod.rs`, next to the other `SUB4_PP_*` probes; it runs the probe
then `return Vec::new()`, so it never emits the production stream). With the gate
absent, the default `build_pingpong_point_add()` path runs unchanged.

Source edits (all inert with the gate absent — no `push_op`/`alloc_*` on the
disarmed path, so the emitted stream is byte-identical):

1. `src/point_add/pingpong_div.rs`: a read-only divide-denominator recorder
   (`DIVIDE_DENOM_CAPTURE` thread-local + `retained_splice_denom_arm/capture/
   take/armed`), modeled on the existing `fused_trace` discipline. It records the
   pristine divide denominator wires and the entry op-offset only while armed.
2. `src/point_add/pingpong_div.rs`, inside `pingpong_mod_mul_div_in_place`: one
   guarded call `retained_splice_denom_capture(b, denominator)` for the `Divide`
   direction only. It emits nothing; it is the analogue of the pre-existing
   `fused_trace_set_direction` call on the line above.
3. `src/point_add/pingpong_div.rs`: `retained_splice_canonical_selfcheck()` — the
   NM64 + M64 harness described below.

The two frozen fused cell bodies `signed_mod_add_pm_halve_fused` and
`signed_mod_double_add_pm_fused` are byte-unchanged. No nonce, window, round
count, plan, square, or point-add semantics were changed. No second family,
rescue, codec, repair, or tuning route was opened. The `{0,p}` normalization
toggle from the round-0..3 zero-seed prototype is deliberately NOT used here: a
real numerator has no `{0,p}` sentinel, so XOR-ing `p` into a live value would
corrupt it; the production reference at rounds 2..7 calls the bare fused cell and
so does the candidate. The only permitted candidate/reference difference is where
`sign` comes from.

## Architecture and why NM64 is coherent (not an all-zero prototype)

The nonzero midpoint comes from the real production divide replay, not a seed.
Divide round 0 halves the numerator (nonzero production data); round 1
`seed_round_one` makes the coefficient nonzero; by rounds 2..7 both the fused
cell source and target are live and nonzero. The harness seeds the candidate
from the captured production coefficient/numerator at the round-2 entry, so the
splice runs on a genuinely nonzero coefficient midpoint.

The rounds covered are exactly the fused rounds the retained-word sign oracle can
reconstruct: 2..7 (the fused halve cell is emitted only for rounds >= 2; the
oracle `retained_denominator_sign_1_to_7_oracle` covers rounds 1..7). This is the
family's structural boundary — see Gate 3 below.

The existing `retained_denominator_multisign_selfcheck`
(`SUB4_PP_RETAINED_MULTISIGN_SELFTEST`) already proved signs 1..7 equal the
production walk exhaustively over all 512 low-9-bit residues (bits 0..8) under 8
high prefixes. Signs 1..7 depend only on denominator bits 0..8, so that census is
complete and predicts the R64 discriminating check (below) will pass. The
"census-specific" caveat in `ROUND3-RETAINED-WORD-BDF4845.md` was about the
zero-seed `expected_x` identity keyed on bit 2, NOT about the sign oracle.

## Human run commands (in the lane worktree; builds are yours to run)

1. Protected default (Gate 1 preamble / Gate 2 baseline). Fresh normal build,
   gate absent, must reproduce the inherited stream exactly:

   ```text
   cargo build --release
   ./target/release/build_circuit            # or the normal ops.bin generator
   ```

   Expected (from the parent, `PREDECLARATION` lines 18-24):
   `12,972,785` operations, `50,798,742` bytes, SHA256
   `e33245d491a16192068ef7024a2c82375047c17af3c8f802c81066de0568cb0a`.
   Any drift here is terminal and unrelated to this gate (the gate is off).

2. The single new gate (runs NM64 then M64; prints to stderr, emits no stream):

   ```text
   SUB4_PP_RETAINED_SPLICE_CANONICAL=1 ./target/release/build_circuit
   ```

## Expected receipt fields and pass conditions

The probe prints these lines (values marked `<measured>` are produced by the run;
I could not run builds, so exact hashes/counts are not pre-filled — do not accept
a green result unless every named condition holds):

- `RSC op_stream_identity=OK ops=<measured> stream_sha256=<measured>`
  Pass: line present (recorder proved byte-inert by an on/off rebuild compare).
  `ops` should equal the point-add-only count `12,972,689` (pre-tail), matching
  `FUSED_TRAJ op_stream_identity` in `KILL-FUSED-REACHABLE-INVERSE-B523.md`.

- `RSC NM64 fixture nonzero_coeff_lanes=<n>/64 nonzero_numer_lanes=<n>/64
  per_round_nonzero_coeff=[..] noncanon_boundary_values=<n> fixture_sha256=<hex>`
  Pass (gate-opening): `nonzero_coeff_lanes=64/64`, `noncanon_boundary_values=0`.
  This is the "genuinely nonzero coefficient midpoint, every lane, all boundaries
  canonical `< p`" requirement. `fixture_sha256` is the ordered digest over
  per-(shot,round) denominator/source/target_before/target_after/direction/round;
  record it as the fixture's identity. The `assert`s fire (terminal KILL) if a
  lane is zero-or-`p` or a boundary is non-canonical.

- `RSC NM64 oracle_sign_vs_production sign_mismatch_lanes=<n>/64`
  Pass (the discriminating gate): `sign_mismatch_lanes=0/64`. This is the single
  check that decides the family: the retained-word oracle sign for rounds 2..7 is
  compared to the production tape sign on the R64 production denominators. If it
  is nonzero the assert fires with
  `retained-word oracle sign disagrees with production on R64: family falsified` —
  that is the scoped terminal falsifier, and NM64/M64 stop there. (Predicted to
  pass from the exhaustive bits-0..8 census above.)

- `RSC NM64 closure candidate_phase=<n> candidate_ancilla=<n> candidate_peak_q=<n>
  candidate_abi_q=<n> candidate_extra_peak_q=<n> candidate_total_q=<n>
  candidate_ops=<n> candidate_emitted_t=<n>
  candidate_executed_t_per_lane_fwd_and_rev=<f> persistent_carrier_bits=0
  max_live_sign_bits=1 fixed_oracle_scratch_q=2 verdict=CLOSED`
  Pass: `verdict=CLOSED`, `candidate_phase=0`, `candidate_ancilla=0`. The
  forward retained-word splice (rounds 2..7, oracle signs into the unchanged
  halve cell) plus the complete reverse cleanup (unchanged double-add fused
  inverse) restores denominator, retained word, coefficient, and numerator to the
  captured midpoint, with all signs/scratch zero and phase/ancilla zero. Per-round
  asserts also require candidate target_after == captured production value and
  source-drift == 0 at every forward round, and target_before restoration at every
  reverse round; a target mismatch panic reports `got`/`expected` and whether the
  delta is exactly `+/-p` (a `+/-p` representative is ladder-dependent lazy
  reduction — harness fidelity — whereas any other delta is a family defect).
  `candidate_peak_q` and `candidate_executed_t_per_lane_fwd_and_rev` are the
  6-round-slice prototype cost, reported for scale only — not a score; the
  executed figure covers both the forward splice and the reverse cleanup.
  `persistent_carrier_bits=0`, `max_live_sign_bits=1`, and
  `fixed_oracle_scratch_q=2` are printed literals for structural invariants of the
  construction (a single reused sign qubit and a fixed two-qubit oracle
  workspace, plus `assert_eq!(cand.active_qubits, c_abi)` at teardown), not
  independently measured counters.

- `RSC M64 miter boundary_mismatch=<n> reference_phase=<n> reference_ancilla=<n>
  reference_total_q=<n> verdict=MATCH`
  Pass: `verdict=MATCH`, `boundary_mismatch=0`, `reference_phase=0`,
  `reference_ancilla=0`. An independent production-sign reference (signs read from
  a tape register, not reconstructed) drives the same cells; every splice boundary
  matches the candidate and the captured production values, forward and reverse.

- `RSC Gate3 economics NOT_MEASURED reason=no_sign_source_past_round_7`
- `RETAINED_SPLICE_CANONICAL done`

## Gate 3 boundary — stated, not faked

A complete default-off 696-round candidate would need a reconstructed sign for
every replay round. No sign source exists past round 7 in the frozen source, and
the frozen ANF census (`2,2,5,11,25,57,115,244,481,1001,2013,4041,8177,16433`
through sign 14; see STATE.md `3e68e90`/`f841bcc`) rules out literal enumeration.
Therefore the Q<=1114 / rounded-T<=1,049,462 economics of ordered Gate 3 are NOT
measured here, and no projection is offered. Extending coverage past round 7 by
keeping a live denominator-derived value-walk register across the replay would be
a persistent second denominator carrier — the forbidden second family — so it was
not built. The measurable result of this lane is the exact NM64/M64 closure on
the real nonzero production midpoint over rounds 2..7; the economic ceiling is
the open frontier and is bounded by the missing sign source, not by any measured
failure of the splice.

## Verdict for the human gate-runner

- If `sign_mismatch_lanes=0/64`, `nonzero_coeff_lanes=64/64`,
  `noncanon_boundary_values=0`, NM64 `verdict=CLOSED` with `0/0` phase/ancilla,
  and M64 `verdict=MATCH` with `0/0/0`: the retained-word splice is exact on the
  frozen canonical nonzero midpoint **for the rounds-2..7 divide slice** with
  value/phase/ancilla `0/0/0`. Read this carefully before authorizing Gate 2/3:
  this is NOT the complete-divide NM64 the predeclaration names. Two scoped
  deviations, both forced by the frozen evidence and neither a measured failure:
  (a) coverage is 6 of the 696 divide fused calls — the rounds the sign oracle
  can reconstruct; and (b) the fixture is seeded from the round-2 entry state, not
  the round-0 pre-replay entry (at round 0 the coefficient is still zero, so
  round-2 entry is the correct place to exhibit a genuinely nonzero coefficient
  midpoint). The gap to the complete divide is exactly the missing sign source
  past round 7, i.e. the Gate 3 economics frontier, and is a bound on the family,
  not a defect in the splice. A complete-divide NM64 (and its Q<=1114 /
  T<=1,049,462 economics) requires a predeclared oracle-extension lane, not this
  one.
- If the discriminating assert fires, that is the scoped terminal falsifier: the
  retained-word oracle is not the production sign on R64 denominators, and the
  family is killed for these inputs. No candidate economics or rescue follows.

## Reproduction / protected-default identity

- Gate: `SUB4_PP_RETAINED_SPLICE_CANONICAL=1 ./target/release/build_circuit`.
- Protected default (gate absent) must stay byte-identical to the inherited
  stream (12,972,785 ops / 50,798,742 bytes / SHA256 `e33245…0568cb0a`).
- Existing controls remain unchanged and available:
  `SUB4_PP_FUSED_TRAJECTORY_TRACE=1` (P64/C64 `EXACT_INVERSE_ON_REACHABLE`),
  `SUB4_PP_RETAINED_MULTISIGN_SELFTEST=1` (signs 1..7 census),
  `SUB4_PP_NUMERATOR_ABI_PAIR_PROBE=1` (A16 negative control).

Model: Claude Fable 5, single-lane research worktree, no build/commit/network
authority.
