# Re-descent lane state

Updated: 2026-08-22T14:16:27Z

## Identity

- Lane: `redescent-teddy-1270`
- Worktree: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/redescent-teddy-1270`
- Branch: `research/redescent-teddy-1270`
- Clean ancestor: `897dda2b0cf267151ecd973252d2a5078cbf1b63`
- Ancestor meaning: Teddy Pender's first promoted ping-pong submission, `3616dbf2`
- Protected live leader: `36f6ca0` (`welttowelt`, submission `e9d1e00`)
- Live receipt at lane creation: Q=1278, T=924651, score=1181703978 (`70d64f5`)
- Prior live receipt refreshed 2026-08-22T12:16Z: Q=1278, T=921558, score=1177751124 (`7ca0559`)
- Current live receipt refreshed 2026-08-22T14:16Z: Q=1278, T=919793, score=1175495454 (`36f6ca0`)
- Accepted diff from `7ca0559`: multiply replay depth 700 -> 696 plus clean nonce48000070891; no other source change.

The protected leader is outside this worktree. This lane may regress temporarily and may not overwrite, submit, or claim promotion from exploratory evidence.

## Explicit target

Primary direction:

```text
Q <= 1270
original architectural charter: T < 930475 at Q=1270
current strict live gate: T <= 925586 at Q=1270
trusted score < 1175495454
```

The current universal gate is `Q * T < 1175495454`. Exact strict T ceilings are Q1278=919792, Q1277=920513, Q1270=925586, Q1266=928511, Q1148=1023950, Q1000=1175495, Q800=1469369, Q700=1679279, and Q637=1845361. At lower Q, recompute the ceiling from a freshly reopened board rather than carrying these values forward. Teddy's reported 637Q / 1.5M-T component shape would score 955,500,000 if it composed and passed the trusted contract.

## Research contract

- Preserve the benchmark ABI and trusted correctness contract.
- Treat later accepted descendants as evidence and comparison points, not axioms or patches to cherry-pick wholesale.
- Permit an intermediate score regression only when a named peak-owner invariant improves inside the saddle budget.
- No nonce or fleet hunt until the source is frozen, the measured or conservative Q/T economics clear the live gate, and a target-bound filter is calibrated.
- Any eventual candidate requires a clean rebuild and full 9024-shot classical/phase/ancilla result of `0/0/0`.
- This side lane has research authority only; submission remains outside its scope.

## Saddle budget

- First cycle: three bounded structural experiments or six elapsed research hours, whichever comes first.
- Continue a route only if it removes a measured co-resident peak allocation, moves a binder, or yields a conservative path to Q<=1270.
- Kill a route after two consecutive repairs fail to improve the same named invariant.
- A flat global Q is not an automatic kill if the experiment provably removes one co-binder and records the next binder.

## Current phase

`GLOBAL_TAPE_REPRESENTATION_REDESCENT`

## Current hypothesis

`H6`: the one-sign-per-round tape is the dominant persistent state, but neither current-walk recomputation, local tagged blocks, terminal-tail grinding, nor coefficient absorption can remove it under the existing cleanup semantics. A viable representation must preserve the whole transcript without retaining predecessor state, and it must compose with Teddy's measured square co-binder cut.

## Current falsifier

H6 fails for a proposed representation if its decoder key contains state no longer live at walkback, if modular carry/high-word dependencies are omitted, or if a reachable slice contains more accepted transcripts than decoder-visible states. Context-specific checkpoint, radix, coefficient-absorption, and alternate-inversion negatives remain closed unless a changed premise is named.

## Next action

Hold the exact prefix-code and terminal-tail lanes at their measured boundaries. The prefix family needs at least257 covered decisions before it reaches the current ping-pong binder. The terminal-tail circuit has real same-Q T economics, but394240 exact non-overlapping scans produced two classical-clean predictions, both with proven phase residuals, and zero K0 candidates. Teddy's sparse square overturn is exact at standalone Q1148 and removes the independent square co-binder for future composition, but replay still owns global Q1278. The carry-aware coefficient census now reproduces k4 and k8 maximum sign fibers of8 and128, so coefficient absorption under current cleanup semantics is KILL. The live leader's 696-round multiply depth is protected. Run one bounded 695-round falsifier for immediate score while Fable audits the smallest global square/replay composition. Next deep build only a genuinely global transcript representation or changed coefficient/cleanup semantics. Grind stays last.

## Last verified result

- Square explorer: commit `e004e5f` on `research/7ca-teddy-square-dilated`.
- Exact sparse square: standalone Q1278 -> Q1148, executed T58678.203 ->59597.625, deterministic64 value/phase/ancilla `0/0/0`; default stream remains byte-identical.
- Whole circuit with exact sparse square: global Q1278, T922501.06, deterministic64 `0/0/0`; replay is the sole remaining Q1278 binder, so the component is HOLD rather than a candidate.
- Terminal-tail explorer: cutoff697 Q1278/T921214.444 reached trusted classical/phase/ancilla `0/2/0` on nonce4300192188. Exact B-E coverage394240 produced another classical-clean nonce4300390193 with K1 and no K0 candidate. Lane CLOSED HOLD.
- Phase autopsy commit `96aa36e`: four residuals localize to old22-bit HMR carry repairs. A +8.896T local widening overfit one draw and failed reseeds, so source repair KILL.
- Coefficient-absorption audit commit `ad206c9`: current local one-tag claim KILL; a new global codec/cleanup architecture remains open.
- Carry-aware coefficient census commit `3650a13`: complete k2/k4/k8 domains reproduce SHA prefixes `740015c4f83142d2`, `8a939e3689283000`, and `a7d7f58ed2818da5`; k4/k8 maximum fibers8/128 confirm KILL.
- Live protected commit `36f6ca0`: Q1278/T919793/full9024 `0/0/0`; exact accepted diff is multiply depth696 plus nonce48000070891.

## Credit and shipping note

Fresh human advice from Teddy Pender on 2026-08-22 explicitly directed attention to the tape and mentioned a non-composing 637Q / 1.5M-T component. If a tape architecture becomes a real candidate, the research commit and Stop-Slop-reviewed public note must credit Teddy prominently. The public model sentence is exactly `Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.` The submission API attribution remains exactly `kimi`. No victory note exists before a clean full 9024-shot `0/0/0` receipt.
