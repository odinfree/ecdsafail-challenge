# Overturn ledger

## Objective contract

- Objective: minimize `peak_qubits * rounded_average_executed_Toffoli`.
- Live gate at creation: `1278 * 924651 = 1181703978`.
- Current live gate refreshed 2026-08-22T11:43Z: `1278 * 923463 = 1180185714`.
- Original target direction: Q<=1270 while preserving T<930475 at Q=1270; the refreshed live gate now requires T<=929280 there.
- Trusted verifier: unchanged repository `eval_circuit`, all 9024 Fiat-Shamir shots.
- Correctness channels: classical, phase garbage, ancilla garbage.

## Protected leader

| field | value |
|---|---|
| source | `b5796ce` |
| qubits | 1278 |
| Toffoli | 923463 |
| score | 1180185714 |
| submission | `7b6ad5c` |
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

## Closure rule

An assumption may be marked `survived` only with the exact ancestor, code/config identity, measured result, and falsifier evidence. “The accepted lineage already tried it” is insufficient.
