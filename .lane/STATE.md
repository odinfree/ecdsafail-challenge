# Re-descent lane state

Updated: 2026-08-22T15:14:42Z

## Identity

- Lane: `redescent-teddy-1270`
- Worktree: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/redescent-teddy-1270`
- Branch: `research/redescent-teddy-1270`
- Clean ancestor: `897dda2b0cf267151ecd973252d2a5078cbf1b63`
- Ancestor meaning: Teddy Pender's first promoted ping-pong submission, `3616dbf2`
- Protected live leader: `def24be` (`welttowelt`, submission `4269cf6`)
- Live receipt at lane creation: Q=1278, T=924651, score=1181703978 (`70d64f5`)
- Prior live receipt refreshed 2026-08-22T12:16Z: Q=1278, T=921558, score=1177751124 (`7ca0559`)
- Current live receipt refreshed 2026-08-22T14:16Z: Q=1278, T=919793, score=1175495454 (`36f6ca0`)
- Accepted diff from `7ca0559`: multiply replay depth 700 -> 696 plus clean nonce48000070891; no other source change.
- Current live receipt refreshed 2026-08-22T15:14Z: Q=1278, T=919788, score=1175489064 (`def24be`), full 9024-shot `0/0/0`.
- Accepted diff from `36f6ca0`: only default nonce48000070891 ->68001243769. The official promoted source matches the validated one-line candidate.

The protected leader is outside this worktree. This lane may regress temporarily and may not overwrite, submit, or claim promotion from exploratory evidence.

## Explicit target

Primary direction:

```text
Q <= 1270
original architectural charter: T < 930475 at Q=1270
current strict live gate: T <= 925581 at Q=1270
trusted score < 1175489064
```

The current universal gate is `Q * T < 1175489064`. Exact strict T ceilings are Q1278=919787, Q1277=920508, Q1270=925581, Q1266=928506, Q1148=1023945, Q1033=1137937, Q1000=1175489, Q800=1469361, Q700=1679270, and Q637=1845351. At lower Q, recompute the ceiling from a freshly reopened board rather than carrying these values forward. Teddy's reported 637Q / 1.5M-T component shape would score 955,500,000 if it composed and passed the trusted contract.

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

`EXACT_SIGN_ORACLE_PROTOTYPE`

## Current hypothesis

`H9`: retaining one exact 256-bit original denominator word makes the bounded component map injective without a persistent per-round carrier. The exact one-sign skeleton has now recomputed, used, and uncomputed sign1, returned the retained word through the ABI, and cleared phase/ancilla. The next falsifier is a bounded multi-sign or replay slice. The first complete slice may carry substantial Q/T debt; success means semantic correctness and clean workspace, followed by re-descent to compose with Teddy's sparse square.

## Current falsifier

H9 fails if the bounded multi-sign slice assumes unavailable predecessor state, retains an O(R) sign carrier, cannot clear oracle/terminal workspace, or cannot return the retained denominator through the component ABI. Extra scratch, Q above1278, and T regression are explicit prototype debt rather than automatic KILL. The one-sign skeleton upgrades the exact-source route to HOLD but does not yet prove a full replay replacement. Context-specific free-outer-key, local-terminal, checkpoint, radix, coefficient-absorption, and materializing-decoder negatives remain closed unless a changed premise is named.

## Next action

Hold the exact prefix-code and terminal-tail lanes at their measured boundaries. Teddy's sparse square overturn is exact at standalone Q1148, but replay still owns global Q1278. The free outer offset key collides for divide and multiply, so that route is KILL. Commit `e57dfb4` proves an env-gated one-sign retained-denominator skeleton at Q1033 with phase/ancilla clean and no O(R) carrier. Extend it to the smallest bounded multi-sign or replay slice, one sign at a time, and record all temporary Q/T/retained-state debt. Do not optimize or grind before semantic correctness and cleanup. The one-round MUL695 stream remains a separate economic HOLD at trusted dirty12/7/0. Grind stays last.

## Last verified result

- Square explorer: commit `e004e5f` on `research/7ca-teddy-square-dilated`.
- Exact sparse square: standalone Q1278 -> Q1148, executed T58678.203 ->59597.625, deterministic64 value/phase/ancilla `0/0/0`; default stream remains byte-identical.
- Whole circuit with exact sparse square: global Q1278, T922501.06, deterministic64 `0/0/0`; replay is the sole remaining Q1278 binder, so the component is HOLD rather than a candidate.
- Terminal-tail explorer: cutoff697 Q1278/T921214.444 reached trusted classical/phase/ancilla `0/2/0` on nonce4300192188. Exact B-E coverage394240 produced another classical-clean nonce4300390193 with K1 and no K0 candidate. Lane CLOSED HOLD.
- Phase autopsy commit `96aa36e`: four residuals localize to old22-bit HMR carry repairs. A +8.896T local widening overfit one draw and failed reseeds, so source repair KILL.
- Coefficient-absorption audit commit `ad206c9`: current local one-tag claim KILL; a new global codec/cleanup architecture remains open.
- Carry-aware coefficient census commit `3650a13`: complete k2/k4/k8 domains reproduce SHA prefixes `740015c4f83142d2`, `8a939e3689283000`, and `a7d7f58ed2818da5`; k4/k8 maximum fibers8/128 confirm KILL.
- Live protected commit `def24be`: Q1278/T919788/score1175489064/full9024 `0/0/0`; exact accepted diff from `36f6ca0` is nonce48000070891 ->68001243769.
- MUL695 falsifier commit `dff3f66`: Q1278/T919434.045/full9024 `12/7/0`; exact stream KILL, architecture HOLD.
- Fable Q1148 visibility audit: sparse square HOLD, materializing decoder KILL, cleanup-contract overturn is next; live-rebased memo `.lane/FABLE-Q1148-VISIBILITY.md`.
- Cleanup collision commit `e06d95d`: exact p=7 fixed-width census finds the first component-local collision at round6 for both divide and multiply; local terminal canonicalization KILL, global/deferred cleanup HOLD behind an enlarged-key gate.
- Outer-key census commit `f990424`: zero-increment classical offset key KILL; one retained denominator word is bounded injective through p31/20 rounds in both directions, with explicit +256Q and recomputation debt. Exact sign-oracle skeleton is next.
- Retained-sign1 skeleton commit `e57dfb4`: exact source-gated prototype Q1033, ABI Q257, extra peak Q776, 15,634 ops, 3,040 emitted/executed T, phase0, ancilla0, carrier bits0. It retains one denominator word, computes/uses/uncomputes one sign, and returns the word cleanly; bounded multi-sign composition is next.

## Credit and shipping note

Fresh human advice from Teddy Pender on 2026-08-22 explicitly directed attention to the tape and mentioned a non-composing 637Q / 1.5M-T component. The promoted `def24be` note credits Teddy prominently for the Burn the House Down experimental discipline without misattributing the nonce-only delta. If a tape architecture becomes a real candidate, its research commit and Stop-Slop-reviewed public note must credit Teddy even more directly. The public model sentence is exactly `Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.` The submission API attribution remains exactly `kimi`.
