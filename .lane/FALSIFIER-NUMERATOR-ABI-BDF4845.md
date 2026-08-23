# Falsifier — `KILL_LIVE_NUMERATOR_ABI_CLOSURE` is a shared fused-cell defect, not a retained-word failure

Resolved: 2026-08-23. Lane: `research/fable-clanker-splice-audit-bdf4845`.
Base: `a9af194` production defaults, imported via `384823f` (see
`PREDECLARATION-ROUND3-BDF4845.md`). Predeclaration for this audit:
`PREDECLARATION-NUMERATOR-ABI-BDF4845.md`.

## Question

Commit `34c1b50` (line `9805dee`, parent `90a2175`) recorded
`KILL_LIVE_NUMERATOR_ABI_CLOSURE`: on the nonzero-numerator stress corpus the
complete reverse-and-clear ABI failed for BOTH the candidate AND the "unchanged
reference" (candidate final classical/phase/ancilla `1688/2351/0`, reference
`1688/2025/0`). The prior lane note guessed the failure "most likely lives in
the walk-back / ABI-closure harness." This audit determines the true cause.

## Method (correct framing)

A gate-level `G ∘ G⁻¹` circuit restores its input for EVERY input; the all-zero
seed is a fixed point that hides any non-inverse cell. So a closure failure can
only mean some forward/reverse primitive pair is **not an exact gate-level
inverse**. The identical classical count (1688 for both candidate and
reference) points at a primitive the two paths SHARE, not at the retained-word
decoder. Rather than port the whole production-prefix harness, this lane probes
each shared replay/reverse pair directly on the `a9af194` base with a
deterministic nonzero corpus in `[0, p)` (16 seeds: `0, 1, 2, 3, p-1, p-2,
p>>1`, and nine SHAKE256-derived values reduced mod p; source seeds rotated by
one). Env gate: `SUB4_PP_NUMERATOR_ABI_PAIR_PROBE=1 ./target/release/build_circuit`
(add `SUB4_PP_NUMERATOR_ABI_PAIR_PROBE_VERBOSE=1` for per-seed detail).

## Result (predeclared kill gates → outcomes)

```text
NUMERATOR_ABI_PAIR name=mod_halve_pm|mod_double_pm                                     restore_fail=0 phase_fail=0 ancilla_fail=0 verdict=EXACT_INVERSE
NUMERATOR_ABI_PAIR name=seed_round_one|seed_round_one_inverse                          restore_fail=0 phase_fail=0 ancilla_fail=0 verdict=EXACT_INVERSE
NUMERATOR_ABI_PAIR name=signed_mod_add_pm_halve_fused|signed_mod_double_add_pm_fused   restore_fail=3 phase_fail=2 ancilla_fail=0 verdict=NOT_INVERSE
NUMERATOR_ABI_PAIR name=retained_normalization_toggle^2                                restore_fail=0 phase_fail=0 ancilla_fail=0 verdict=EXACT_INVERSE
```

- Gate 1 (`mod_halve_pm`/`mod_double_pm`): CLEAN.
- Gate 2 (`seed_round_one`/`seed_round_one_inverse`): CLEAN.
- Gate 3 (`signed_mod_add_pm_halve_fused` / `X;signed_mod_double_add_pm_fused;X`):
  **FIRED.** These are the fused round-≥2 replay cell (forward) and its fused
  inverse — cells BOTH the candidate and the reference use identically. The
  inverse's doc comment calls it "dormant," but that is stale: `replay_doubling_round`
  (pingpong_div.rs:1145-1150) and `replay_doubling_inverse` (1953-1964) select
  `signed_mod_double_add_pm_fused` by DEFAULT (fused unless `SUB4_PINGPONG_UNFUSED_INVERSE`
  is set), and the promoted `build()` divide reverse traversal calls
  `replay_doubling_round` (pingpong_div.rs:314-335) — so this inverse is on the
  live production trajectory, not dormant.
- Gate 4 (`retained_normalization_toggle` involution): CLEAN — the retained-word
  normalization machinery is an exact involution on general values.
- Gate 5 (walk cells): not reached; the defect is in the replay pair.

The three retained-word-specific machineries the component adds (the sign
oracle's inputs via `seed_round_one`, the `{0,p}` normalization toggle, and the
round 0/1 target arithmetic) are all exact inverses. **No retained-word-specific
cell appears in the failing pair.**

## Root cause (both readings collapse to one)

Per-seed detail on the failing pair, default windows (fold=54, flag=22,
endpoint=20):

```text
FAIL shot=1 target_seed=0x1 source_seed=0x2                 sign=1 got=0x…fefffffc30   (= p + 1)
FAIL shot=3 target_seed=0x3 source_seed=0x…fefffffc2e       sign=1 got=0x…fefffffc32   (= p + 3)
FAIL shot=6 target_seed=0x7fff…7ffffe17 source_seed=big     sign=0 got=0x8000…7ffffe17 (truncation)
```

Widening all windows to 256 (`SUB4_PP_REPLAY_FOLD_WINDOW=256
SUB4_PP_REPLAY_FLAG_COMPARE=256 SUB4_PP_ENDPOINT_FOLD_WINDOW=256`) drops the
failure to `restore_fail=2 phase_fail=1`, and the two survivors are exactly
shots 1 and 3 — both `got == seed + p`. Shot 6 was a pure truncation artifact
and vanishes at full width.

So there is a single defect: `signed_mod_double_add_pm_fused` performs an
**incomplete (lazy) modular reduction**, returning a non-canonical
representative `value + p` for inputs near the reduction boundary. The value is
always correct mod p; the register is simply not canonically reduced, which
breaks the bit-exact restoration a reversible-ABI check demands. Truncation
width only changes WHICH inputs hit the boundary; the representative defect
itself survives full width.

## Verdict

`KILL_LIVE_NUMERATOR_ABI_CLOSURE` is a property of the SHARED, nonce-tuned
production fused arithmetic cell pair
(`signed_mod_add_pm_halve_fused` / `signed_mod_double_add_pm_fused`) driven off
its production coefficient trajectory. It is **NOT** evidence against the
retained-word architecture. The forward and inverse fused cells are not
bit-exact inverses on arbitrary `[0, p)`; they coincide on the production
coefficient trajectory, which the promoted build validates at 9024-shot
`0/0/0`. The stress corpus fed values off that trajectory, and because both the
candidate and the reference use this cell, both failed identically (1688 each).

**Important scope note.** This is NOT a claim that production is buggy: the
promoted 9024-shot `0/0/0` result is direct evidence the production trajectory
never lands on these boundary representatives. This is a latent property of the
cell outside its production domain, exposed only by an out-of-trajectory stress.

## Why the predeclared repair was NOT taken

The predeclaration reserved "the smallest gate-level fix to whichever pair is
not an exact inverse." The defect is in a tuned production arithmetic cell whose
non-canonical output is absorbed by the production nonce trajectory — repairing
it means adding a full modular reduction (extra Q/T) to a promoted primitive,
which is explicitly LARGER than "the smallest demonstrably incorrect harness
assumption" and would regress the live economics. It is also not a harness
assumption: nothing in `signed_mod_double_add_pm_fused` documents a restricted
domain, so narrowing the corpus to make the receipt green would be certificate
lock-in, not a repair. The splice gate ("only if exact at the nonzero midpoint")
therefore does not open, and per the task the deliverable is the exact falsifier
plus the next overturn.

## Retest status

The minimal flag-free round-3 component's ABI closure at a nonzero midpoint
CANNOT be established without first specifying or fixing the shared fused cell:
the round-3 self-check has no reverse-replay section, and a valid nonzero
midpoint requires the production-trajectory characterization named as the next
overturn below. Building one would be a new architecture, not a retest.

## Next overturn (priced experiments)

1. **Characterize the production coefficient trajectory** the fused pair is
   bit-exact on (odd, canonically-reduced operands within the pseudo-Mersenne
   carry window). Falsifier: seed the pair only with trajectory-valid values and
   confirm `restore_fail=phase_fail=0`; then a manifold-restricted nonzero
   round-3 ABI-closure retest becomes meaningful. Cost: probe-only, hours.
2. **Build a bit-exact fused inverse** (`signed_mod_double_add_pm_fused` with a
   full final reduction) and price its Q/T against the current cell. Falsifier:
   the new pair returns `EXACT_INVERSE` on all `[0, p)`; kill if the added
   reduction pushes the divide replay peak above the Q1114 prototype budget or
   the strict live T ceiling. Cost: one cell rewrite + census.

Either is a real, scoped experiment. Global integration, nonce/fleet hunts,
submissions, and public notes remain out of scope.

## Reproduction and protected-default identity

- Probe: `SUB4_PP_NUMERATOR_ABI_PAIR_PROBE=1 ./target/release/build_circuit`.
- Round-3 census unchanged: `SUB4_PP_RETAINED_MULTISIGN_SELFTEST=1` still reports
  `candidate_peak_q=1114 candidate_ops=13659 candidate_emitted_t=960
  candidate_executed_t=894.054 round3_flag_free=1 phase=0 ancilla=0`.
- Fresh normal build byte-identical to the recorded baseline: `ops.bin`
  50,798,742 bytes, SHA256
  `e33245d491a16192068ef7024a2c82375047c17af3c8f802c81066de0568cb0a` (generated
  artifact, not committed). All edits are behind
  `SUB4_PP_NUMERATOR_ABI_PAIR_PROBE`; the normal `build()` path changed no byte.

Model: Claude Fable 5, single-lane research worktree.
