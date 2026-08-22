# Re-descent lane state

Updated: 2026-08-22T15:22:38Z

## Identity

- Lane: `redescent-teddy-1270`
- Worktree: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/redescent-teddy-1270`
- Branch: `research/redescent-teddy-1270`
- Clean ancestor: `897dda2b0cf267151ecd973252d2a5078cbf1b63`
- Ancestor meaning: Teddy Pender's first promoted ping-pong submission, `3616dbf2`
- Protected live leader: `a9af194` (`welttowelt`, submission `236fb8d`)
- Live receipt at lane creation: Q=1278, T=924651, score=1181703978 (`70d64f5`)
- Prior live receipt refreshed 2026-08-22T12:16Z: Q=1278, T=921558, score=1177751124 (`7ca0559`)
- Current live receipt refreshed 2026-08-22T14:16Z: Q=1278, T=919793, score=1175495454 (`36f6ca0`)
- Accepted diff from `7ca0559`: multiply replay depth 700 -> 696 plus clean nonce48000070891; no other source change.
- Current live receipt refreshed 2026-08-22T15:14Z: Q=1278, T=919788, score=1175489064 (`def24be`), full 9024-shot `0/0/0`.
- Accepted diff from `36f6ca0`: only default nonce48000070891 ->68001243769. The official promoted source matches the validated one-line candidate.
- Current live receipt refreshed 2026-08-22T15:22Z: Q=1278, T=919785, score=1175485230 (`a9af194`), full 9024-shot `0/0/0`.
- Accepted diff from `def24be`: only default nonce68001243769 ->57002259501. The official promoted source matches the validated one-line candidate.

The protected leader is outside this worktree. This lane may regress temporarily and may not overwrite, submit, or claim promotion from exploratory evidence.

## Explicit target

Primary direction:

```text
Q <= 1270
original architectural charter: T < 930475 at Q=1270
current strict live gate: T <= 925578 at Q=1270
trusted score < 1175485230
```

The current universal gate is `Q * T < 1175485230`. Exact strict T ceilings are Q1278=919784, Q1277=920505, Q1270=925578, Q1266=928503, Q1148=1023941, Q1033=1137933, Q1000=1175485, Q800=1469356, Q700=1679264, and Q637=1845345. At lower Q, recompute the ceiling from a freshly reopened board rather than carrying these values forward. Teddy's reported 637Q / 1.5M-T component shape would score 955,500,000 if it composed and passed the trusted contract.

## Research contract

- Preserve the benchmark ABI and trusted correctness contract.
- Treat later accepted descendants as evidence and comparison points, not axioms or patches to cherry-pick wholesale.
- Permit an intermediate score regression only when a named peak-owner invariant improves inside the saddle budget.
- A first exact architecture prototype may exceed Q1148, use extra scratch, or regress T when it proves the new invariant and clears all added state. Record the Q/T/retained-state debt explicitly, then re-descend for score compliance. Do not confuse prototype tolerance with promotion authority.
- No nonce or fleet hunt until the source is frozen, the measured or conservative Q/T economics clear the live gate, and a target-bound filter is calibrated.
- Any eventual candidate requires a clean rebuild and full 9024-shot classical/phase/ancilla result of `0/0/0`.
- This side lane has research authority only; submission remains outside its scope.

## Saddle budget

- First cycle: three bounded structural experiments or six elapsed research hours, whichever comes first.
- Continue a route only if it removes a measured co-resident peak allocation, moves a binder, or yields a conservative path to Q<=1270.
- Kill a route after two consecutive repairs fail to improve the same named invariant.
- A flat global Q is not an automatic kill if the experiment provably removes one co-binder and records the next binder.

## Current phase

`SIGN6_ORACLE_FALSIFIER`

## Current hypothesis

`H9`: retaining one exact 256-bit original denominator word makes the bounded component map injective without a persistent per-round carrier. The live-bound extension now reconstructs signs1..5, including sign5's 25-term degree-four ANF, consumes/uncomputes one sign at a time, preserves the retained word, and clears a fixed two-qubit scratch after each sign. Max_live_sign_bits remains1 and persistent_carrier_bits0. Sign6's 57-term degree-six low8 oracle is the next falsifier. The first complete slice may carry substantial Q/T debt; success means semantic correctness and clean workspace, followed by re-descent to compose with Teddy's sparse square.

## Current falsifier

H9 fails if sign6 assumes unavailable predecessor state, retains an O(R) sign carrier, widens beyond the named fixed scratch, cannot clear multi-control scratch, or cannot return the retained denominator through the component ABI. Extra scratch, Q above1278, and T regression are explicit prototype debt rather than automatic KILL. The signs1..5 slice is HOLD but does not yet prove a full replay replacement. Context-specific free-outer-key, local-terminal, checkpoint, radix, coefficient-absorption, and materializing-decoder negatives remain closed unless a changed premise is named.

## Next action

Hold the exact prefix-code and terminal-tail lanes at their measured boundaries. Teddy's sparse square overturn is exact at standalone Q1148, but replay still owns global Q1278. Commit `deb94de` proves signs1..5 from one retained denominator; sign5 uses a 25-term degree-four low7 ANF, fixed two-qubit scratch, and cleans after every sign. Extend through sign6's 57-term degree-six low8 ANF and exhaust all256 residues across four high-prefix witnesses. Record all temporary Q/T/retained-state debt. Do not optimize or grind before semantic correctness and cleanup. The MUL695 lane localized non-convergence and proved that an unconditional exact tail merely reconstructs MUL696; its next changed-premise falsifier is a reversible state-selective8-bit tail. Grind stays last.

## Last verified result

- Square explorer: commit `e004e5f` on `research/7ca-teddy-square-dilated`.
- Exact sparse square: standalone Q1278 -> Q1148, executed T58678.203 ->59597.625, deterministic64 value/phase/ancilla `0/0/0`; default stream remains byte-identical.
- Whole circuit with exact sparse square: global Q1278, T922501.06, deterministic64 `0/0/0`; replay is the sole remaining Q1278 binder, so the component is HOLD rather than a candidate.
- Terminal-tail explorer: cutoff697 Q1278/T921214.444 reached trusted classical/phase/ancilla `0/2/0` on nonce4300192188. Exact B-E coverage394240 produced another classical-clean nonce4300390193 with K1 and no K0 candidate. Lane CLOSED HOLD.
- Phase autopsy commit `96aa36e`: four residuals localize to old22-bit HMR carry repairs. A +8.896T local widening overfit one draw and failed reseeds, so source repair KILL.
- Coefficient-absorption audit commit `ad206c9`: current local one-tag claim KILL; a new global codec/cleanup architecture remains open.
- Carry-aware coefficient census commit `3650a13`: complete k2/k4/k8 domains reproduce SHA prefixes `740015c4f83142d2`, `8a939e3689283000`, and `a7d7f58ed2818da5`; k4/k8 maximum fibers8/128 confirm KILL.
- Live protected commit `a9af194`: Q1278/T919785/score1175485230/full9024 `0/0/0`; exact accepted diff from `def24be` is nonce68001243769 ->57002259501.
- MUL695 diagnosis/repair commit `653cf78`: rebased one-round cut Q1278/T919437.926/full9024 `8/4/0`; failing input is not terminal at round695 but is terminal at696. An opt-in exact tail passes full9024 `0/0/0` at Q1278/T919787.536 and is byte-identical to MUL696, so it only recreates the parent. Endpoint19 fails `17/10/0`. Verdict exact unconditional tail KILL, state-selective8-bit correction HOLD.
- Fable Q1148 visibility audit: sparse square HOLD, materializing decoder KILL, cleanup-contract overturn is next; live-rebased memo `.lane/FABLE-Q1148-VISIBILITY.md`.
- Cleanup collision commit `e06d95d`: exact p=7 fixed-width census finds the first component-local collision at round6 for both divide and multiply; local terminal canonicalization KILL, global/deferred cleanup HOLD behind an enlarged-key gate.
- Outer-key census commit `f990424`: zero-increment classical offset key KILL; one retained denominator word is bounded injective through p31/20 rounds in both directions, with explicit +256Q and recomputation debt. Exact sign-oracle skeleton is next.
- Retained-sign1 skeleton commit `e57dfb4`: exact source-gated prototype Q1033, ABI Q257, extra peak Q776, 15,634 ops, 3,040 emitted/executed T, phase0, ancilla0, carrier bits0. It retains one denominator word, computes/uses/uncomputes one sign, and returns the word cleanly; bounded multi-sign composition is next.
- Retained-signs1..4 commit `16c91fb`: exact bounded candidate Q517 on ABI260, 816 ops, emitted/executed T12, max_live_sign_bits1, persistent_carrier_bits0; independent production-walk reference Q1038/T3560 matches256 target-width denominators covering all64 low-six-bit residues under four high prefixes, with denominator preserved, phase0, ancilla0. Source parent `def24be` differs from current `a9af194` only at the default nonce. Verdict HOLD; sign5 is next.
- Retained-sign5 commit `deb94de`: exact `a9af194` candidate Q520 on ABI261, extra peak259, 930 ops, emitted/executed T118; production reference Q1040/T4070. All512 target-width inputs covering128 low residues under four high prefixes match signs1..5; denominator preserved, shared sign and two scratch cleared after each sign, phase0, ancilla0, carrier0, max_live_sign_bits1. Verdict HOLD; sign6 is next.
- Protected-leader cache HOLD commit `a05cca3`: exact `a9af194` cycle has21 clean rows and no average below919784.5; promoted nonce57002259501 at919785.268 remains best. Do not rebuild until a newer read-only cache cycle contains a necessarily new strict beat.

## Credit and shipping note

Fresh human advice from Teddy Pender on 2026-08-22 explicitly directed attention to the tape and mentioned a non-composing 637Q / 1.5M-T component. The promoted `def24be` note credits Teddy prominently for the Burn the House Down experimental discipline without misattributing the nonce-only delta. If a tape architecture becomes a real candidate, its research commit and Stop-Slop-reviewed public note must credit Teddy even more directly. The public model sentence is exactly `Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.` The submission API attribution remains exactly `kimi`.
