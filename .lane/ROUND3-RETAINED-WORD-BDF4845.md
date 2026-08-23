# Round-3 retained-word component (bdf4845 lane)

Updated: 2026-08-23

## Verdict

**HOLD** the exact rounds-0-through-3 retained-word replay prefix. The minimal
exact component uses the one local normalization flag at round 2 ONLY; round 3
is provably flag-free. Round 2's `p` sentinel is the SOURCE of the fused
modular add and needs the atomic toggle (the raw probe reproduces the phase
debt without it). Round 3 is odd: its source is the canonical `y=0` and the
`p` sentinel is only the halve TARGET, which the fused halve maps `p -> p`
reversibly with no phase debt. So round 3 adds a clean replay cell at no flag
cost and Q does not grow.

This refines the prior `40d0170`, which applied an (unnecessary) round-3
toggle. Applying it is harmless but costs 508 candidate operations for zero
benefit; the default here omits it. `SUB4_PP_R3_FORCE_TOGGLE=1` re-applies it
and reproduces the `40d0170` receipt exactly.

This is a bounded semantic prototype. It does not prove the full divide, does
not quantify a live-score-beating static composition price, and does not
authorize a submission, scan, or hunt. This lane is research-only.

## Source and isolation

- Branch base: `3370f66` (documented protected baseline) with `384823f`'s src
  imported as the round-0..2 foundation (see the predeclaration).
- Semantic edit: `src/point_add/pingpong_div.rs`, function
  `retained_denominator_full_replay_selfcheck`, plus the new
  `retained_normalization_toggle` helper. Nothing outside the env-gated
  self-check changed; the normal `build()` path is byte-for-byte the imported
  `384823f`/`a9af194` production path (protected defaults preserved). Normal
  build produced a 50,798,742-byte `ops.bin` at SHA256
  `e33245d491a16192068ef7024a2c82375047c17af3c8f802c81066de0568cb0a` (generated
  artifact, not committed).
- Passing gate: `SUB4_PP_RETAINED_MULTISIGN_SELFTEST=1 ./target/release/build_circuit`.
- Raw negative: add `SUB4_PP_RETAINED_FULL_REPLAY_PHASE_PROBE=1`; it still panics
  deterministically at `pingpong_div.rs` "replay-slice phase dirty after round 2
  in batch 0", binding the normalization fix.

## Contract (tightened, single flag)

State after round 1 with the all-zero seed: `x` in the `{0, p}` continuation
representation keyed by sign 1, `y` canonical zero. Round 2 (even) reads `x` as
the SOURCE of a fused modular add — a raw `p` source leaves phase debt, so it
needs the toggle. Round 3 (odd) reads the canonical `y=0` source and only
halves the `p`-sentinel TARGET `x`, which is reversible (`p -> p`) with no debt,
so round 3 is flag-free. The round-2 toggle is:

1. Reconstruct sign 1 from the retained word into the flag.
2. XOR `p` into `x` under the flag, mapping `{0, p}` to canonical zero.
3. Re-run the sign-1 oracle into the flag, clearing it (flag = 0).

Reconstruct the round's sign into the shared sign qubit, run the production
replay cell on canonical zero, erase the sign, then repeat the atomic toggle to
restore the `{0, p}` continuation. The flag is a fixed one-bit witness, not
indexed by the round.

## Exhaustive miter result (default: flag-free round 3)

```text
TEDDY_RETAINED_FULL_REPLAY_NORMALIZED PASS rounds=0..3 reconstructed_signs=1..3
lanes=4096 low_residues=512 high_prefixes=8
candidate_peak_q=1114 candidate_abi_q=768 candidate_extra_peak_q=346
candidate_total_q=1114 candidate_classical_bits=925
candidate_ops=13659 candidate_emitted_t=960
candidate_round_emitted_t=0:65,1:141,2:377,3:377
candidate_executed_t=894.054
reference_peak_q=1546 reference_abi_q=768 reference_total_q=1546
reference_classical_bits=2967 reference_ops=41110
reference_emitted_t=4010 reference_executed_t=3945.219
denominator_preserved=1 retained_word_preserved=1 replay_state_match=1
normalization_flag_peak=1 normalization_flag_final=0
normalization_flag_cleared_before_sign=1 concurrent_normalization_flags=0
normalization_toggle_rounds=2 round3_flag_free=1
phase=0 ancilla=0 persistent_carrier_bits=0 max_live_sign_bits=1
fixed_oracle_scratch_q=2
```

With `SUB4_PP_R3_FORCE_TOGGLE=1` the receipt is byte-identical to `40d0170`:
`candidate_ops=14167`, `reference_ops=41614`, `normalization_toggle_rounds=2,3`,
`round3_flag_free=0`; every other field, including emitted/executed Toffoli and
all cleanliness counters, is unchanged (the toggle is linear). The raw probe
(`SUB4_PP_RETAINED_FULL_REPLAY_PHASE_PROBE=1`) still panics after round 2,
binding the round-2 flag as necessary.

Every batch stops after replay rounds 0/1/2/3 and after each toggle-in
boundary, checking the shared sign, both oracle scratch qubits, the flag, the
retained word, and phase. The independent reference obtains signs 0..3 from the
exact production value walk, runs the same replay cells, and reverses the walk
exactly. Candidate `x`/`y` match the reference on every shot; all non-output
qubits return to zero.

## Kill conditions — none triggered

1. Second concurrent flag: NO (`concurrent_normalization_flags=0`).
2. Flag not clearable before the next sign: NO
   (`normalization_flag_cleared_before_sign=1`, `max_live_sign_bits=1`).
3. State growing with round count: NO (`persistent_carrier_bits=0`; round 3 adds
   377 emitted Toffoli and 0 peak qubits over round 2).
4. Missing predecessor: NO (reference is a real walk; `replay_state_match=1`).
5. Phase/ancilla debt: NO (`phase=0 ancilla=0`).
6. Cannot compose toward a strict live beat: DEFERRED (out of scope; see below).

## Independent cross-check

This lane re-derived the round-3 extension from the `384823f` round-2 base
rather than cherry-picking `40d0170`'s patch. Under `SUB4_PP_R3_FORCE_TOGGLE=1`
the receipt is byte-identical to `40d0170` (Q1114, ops 14167, emitted 960,
round split 0:65/1:141/2:377/3:377, executed 894.054, same reference figures) —
independent confirmation, not a copy. The default receipt then improves on it
by dropping the unnecessary round-3 toggle (13659 vs 14167 candidate ops, same
emitted Toffoli and same cleanliness).

## Static composition price — not yet cleared

The whole prefix sits at Q1114 (base 1028 + 86 transient in the fused
`signed_mod_add_pm_halve_fused` cell). This is prototype debt. It is a zero-seed
continuation: the coefficient registers are zero, so the replay only ever
handles the `{0, p}` sentinel, not a general nonzero numerator. No live Q/T
improvement is claimed. The current live gate is `Q*T < 1175485230`; the global
binder remains the Q1278 production divide, which this local component does not
yet touch.

## Next falsifier

The production splice (nonzero numerator, full component ABI closure) is the
next gate and is already recorded KILLED on the adjacent `9805dee` line as
`KILL_LIVE_NUMERATOR_ABI_CLOSURE` (commit `34c1b50`): the nonzero-numerator
midpoint matches the unchanged continuation, but complete reverse cleanup fails
for BOTH candidate AND reference. Because the *reference* (unchanged production
path) also fails there, the failure most likely lives in the walk-back / ABI
closure harness rather than in the retained-word component. The next bounded
experiment is to audit that reference-side reverse-cleanup failure directly on
the a9af194 base before treating the production splice as architecturally dead.
Do not integrate globally, run a nonce/fleet hunt, or claim any credit until
that closure is exact and the static price clears the live gate.

Model: Claude Opus 4.8, single-lane research worktree.
