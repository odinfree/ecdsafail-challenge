# Overturn ledger

## Objective contract

- Objective: minimize `peak_qubits * rounded_average_executed_Toffoli`.
- Live gate at creation: `1278 * 924651 = 1181703978`.
- Current live gate refreshed 2026-08-22T12:16Z: `1278 * 921558 = 1177751124`.
- Original target direction: Q<=1270 while preserving T<930475 at Q=1270; the refreshed live gate now requires T<=927363 there.
- Trusted verifier: unchanged repository `eval_circuit`, all 9024 Fiat-Shamir shots.
- Correctness channels: classical, phase garbage, ancilla garbage.

## Protected leader

| field | value |
|---|---|
| source | `7ca0559` |
| qubits | 1278 |
| Toffoli | 921558 |
| score | 1177751124 |
| submission | `2b8d6ce` |
| lane relationship | protected external leader; never replaced by an exploratory result |

## Assumptions and overturns

| id | inherited assumption | wall produced | overturn observation | cheapest falsifier | status | next action |
|---|---|---|---|---|---|---|
| O-001 | Divide and multiply traversals should share one terminal-depth policy. | The shallower-converging traversal pays unnecessary terminal walk and replay work. | The two walks have different convergence tails while preserving the same ABI and inverse recurrence. | Instrument terminal state and independently vary only scheduling/depth in a later bounded experiment. | open | Do not import the later `rounds()-4` default; first recover the mechanism from the ancestor trace. |
| O-002 | The full replay/walk state must remain resident across each replay cell. | Replay co-residence keeps Q above the target. | Fourteen terminal passenger wires can be released and exactly reacquired for converged affine fixtures, although the 9024-shot gate shows the convergence condition is not universal at the fixed depth. | Allocation timeline, affine gate, then trusted fixed-nonce run. | partially overturned | Keep the lifetime cut only inside the bounded saddle; do not ship without a universal convergence proof or replacement. |
| O-003 | Lowering one peak phase is enough to lower global Q. | A co-binder immediately preserves the old peak. | Endpoint, replay, square, seed, and fused-fold ladders each became the ceiling in turn; only the composition reached Q=1266. | Trace every phase within 8 qubits of the maximum. | overturned | Preserve the composition and judge new cuts against the full co-binder set. |
| O-004 | Uniform replay widths are the safest architecture. | Worst-case widths are paid at steps that do not need them. | A proof-backed step or region schedule preserves the invariant with less co-resident state. | Derive magnitude/liveness envelopes from the exact fixed-round recurrence. | open | Attempt only after X000 identifies a width-owned binder. |
| O-005 | A late accepted negative result closes the structural route everywhere. | Earlier clean ancestors and different composition orders are never retested. | The same lever changes Q/T or correctness differently on `897dda2` than on a late descendant. | Pairwise ancestor/order ablation with exact source receipts. | open | Maintain the composition matrix; never record a context-free floor. |
| O-006 | Measured carry plots are a nearly free way to buy qubits. | Boundary reconstruction repeats across every replay round and consumes the entire T saddle. | Six replay plots plus split fused folds reach Q=1266 but add about 84k executed T over Teddy's clean baseline; the baseline itself remains about 22k above the lane's T target. | Width/fold A/B matrix under the same 64 deterministic affine lanes. | overturned | X005 must delete a boundary-repair family or fuse replay work; more plot splitting is not a descent. |
| O-007 | One sign qubit per round must remain resident until both replay and reverse walk finish. | Roughly 700 tape qubits dominate every replay peak and force all later work into width/T trades. | A coherent denominator code can exactly donate local prefix decisions and terminal-orbit suffixes can share one sign approximately. However exact reverse blocks still require one tag per decision, and current-walk global decoding exceeds the scratch/product budget. | Exact reachability/rank decoder without walk materialization, plus the bounded cutoff697 nonce pilot. | partially overturned | Exact Bennett and local tagged-block width claims are killed. The immediate terminal-tail circuit remains economically live; general tape replacement needs a changed decoder premise. |
| O-008 | The square requires two materialized129-qubit zero-pad vectors. | The square independently pins Q1278, so a tape cut alone cannot lower global Q. | Teddy's sparse structural-zero adder removes both vectors and lowers the exact standalone square to Q1148 at deterministic64 `0/0/0`. | Env-gated sparse tri-correction with protected default hash, standalone selfcheck, and whole-circuit census. | overturned / HOLD | Compose only after tape/replay falls below Q1148; replay currently remains Q1278. |
| O-009 | Tail phase dirt is caused by the shared terminal sign. | The same-Q T win appears to need a new sign-specific phase repair. | Four old22-bit HMR carry repairs own the residual; a local widening fixes one frozen corpus but fails reseeds. | Localize residual rounds, widen only the eight required positions, then reseed twice. | source repair killed | Keep frozen zero-gate phase selection on HOLD; do not extend the grind before structural work. |
| O-010 | Replay coefficient lows plus one tag can absorb the tape transcript. | A local census appears to bypass the recomputation wall and collapse replay toward the walk binder. | The proposed decoder retains unavailable predecessor residuals and omits modular boundary/high-word state. A reachable zero-numerator slice has at most32 decoder-visible states with one tag, below transcript demand. | Decoder-lifecycle audit and full-width zero-numerator capacity witness before writing the low-word tool. | killed | Reopen only for a global codec keyed solely by walkback-live state or changed coefficient/cleanup semantics. |
| O-011 | `KILL_LIVE_NUMERATOR_ABI_CLOSURE` (both candidate and reference failing reverse cleanup) indicts the retained-word production splice. | The full production splice reads as architecturally dead on the nonzero midpoint. | A four-pair forward∘inverse probe on `[0,p)` shows the failure is ONE shared cell pair `signed_mod_add_pm_halve_fused`/`signed_mod_double_add_pm_fused` (incomplete reduction → `value+p` off the production trajectory); the three retained-word-specific pairs are exact inverses. Both paths share the cell, so both fail identically (1688 each). | `SUB4_PP_NUMERATOR_ABI_PAIR_PROBE=1` per-pair inverse census (done); full-width verbose confirms `got==seed+p` survivors. | overturned (reference-side, not architecture) | Characterize the fused pair's production trajectory, or rebuild a bit-exact fused inverse and price Q/T; only then does the nonzero-midpoint splice retest open. See `FALSIFIER-NUMERATOR-ABI-BDF4845.md`. |

## Closure rule

An assumption may be marked `survived` only with the exact ancestor, code/config identity, measured result, and falsifier evidence. “The accepted lineage already tried it” is insufficient.
