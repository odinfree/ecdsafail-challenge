# Predeclaration — round-3 retained-word component (bdf4845 lane)

Written: 2026-08-23, before any semantic source edit.

## Lane identity and base

- Branch: `research/fable-clanker-round3-bdf4845`.
- Documented protected baseline: clean commit `3370f66`.
- Foundation import: `3370f66`'s `src/` is a stale credit-line snapshot (rooted at
  `897dda2b`) that lacks the retained-word prototype and carries a diverged
  `mod_halve_pm` arity. The exact component "proven for production rounds 0..2 at
  Q1114 / T550.247" is commit `384823f`, which descends from the live leader
  `a9af194`. Per this lane's `STATE.md`, `a9af194`'s promoted values are the
  protected defaults. So the first commit on this branch imports `384823f`'s
  `src/` verbatim (which restores those protected defaults: default nonce
  `57002259501`, square `GUARD=24`). Verified `git diff 384823f -- src/` is empty.
  Non-`src` files are already byte-identical between `3370f66` and `384823f`.

## Admitted representation

- One retained exact 256-bit original denominator word (the ABI denominator).
- One shared sign qubit, reconstructed one round at a time from the retained
  word via `retained_denominator_sign_1_to_7_oracle`, then uncomputed.
- Two shared oracle scratch qubits (fixed).
- One local normalization flag used only as an atomic sentinel toggle
  (reconstruct sign1 into flag, XOR `p` into `x` under flag, clear flag by
  re-running the sign1 oracle). The flag is zero before any new sign enters the
  shared sign qubit and after every restored boundary. No second concurrent
  flag. No state indexed by the round number.

## Exchange-rate / static price bound

- Prototype-debt tolerance: peak may sit at Q1114 (ABI 768 + retained 256 +
  sign 1 + oracle scratch 2 + flag 1 = base 1028; the fused
  `signed_mod_add_pm_halve_fused` replay cell adds ~86 transient qubits).
- Round 3 must NOT raise peak Q above the round-0..2 value (Q1114) and must not
  add a persistent (round-indexed) wire.
- Emitted-Toffoli is the stable structural price; executed-Toffoli is reported
  as an average over the exhaustive census, not a per-gate ablation.

## Exact value / phase / ancilla corpus

- Exhaustive census: 4,096 target-width denominators = every low nine-bit
  residue (512) under eight high prefixes covering the sign-7 borrowed-bit joint
  states.
- Independent reference obtains signs 0..3 from the exact production value walk,
  executes the same production replay cells, and reverses the walk exactly.
- Required at every checkpoint (after replay rounds 0,1,2,3; after each
  normalization and before the next sign): shared sign = 0, both oracle scratch
  = 0, normalization flag = 0, retained word == ABI denominator, phase = 0.
- Terminal: candidate replay state matches production walk, every non-output
  qubit = 0, phase = 0, ancilla = 0.

## Kill conditions (any one ⇒ KILL)

1. A second concurrent live normalization flag at round 3.
2. Inability to clear the one local flag before the next sign is reconstructed.
3. Live/persistent state that grows with the round count.
4. A missing/unavailable predecessor state assumption.
5. Any phase or ancilla debt at any checkpoint or terminal.
6. Inability to compose toward a strict live-score beat (deferred; this lane is
   research-only and NOT authorized for providers, scans, submissions, hunts, or
   public notes).

## Relationship to existing evidence (comparison points, not axioms)

- `40d0170` (a9af194 line) already reports a clean rounds-0..3 zero-seed
  continuation at Q1114 with the same one-flag atomic-toggle contract
  (emitted_t 960; round emitted 0:65,1:141,2:377,3:377). I will implement round 3
  independently on the `384823f` base and treat `40d0170` as a cross-check, not a
  patch to cherry-pick.
- `34c1b50` / `90a2175` (9805dee line) record the production-splice frontier:
  the full-word splice is KILLED on cost (Q1376 vs Q1182 ceiling), and the
  five-bit re-descent hits `KILL_LIVE_NUMERATOR_ABI_CLOSURE` — reverse cleanup
  fails on the nonzero-numerator midpoint for BOTH candidate and reference. That
  production splice is out of scope here (task forbids global integration until
  the local component is exact and the static price is quantified) and its
  "reference also fails" signal is flagged as the next falsifier to audit.

## What I will do

Reproduce the round-0..2 baseline and its raw-probe negative, then extend
`retained_denominator_full_replay_selfcheck` through replay round 3 using the
tightened atomic-toggle flag contract, run the exhaustive miter, verify all
counters clean at Q1114, compare to `40d0170`, and record the verdict, the
static composition price, and the next falsifier.
