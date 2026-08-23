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

`NUMERATOR_ABI_FALSIFIER_RESOLVED` (bdf4845 lane).

The round-3 falsifier is answered: the exact rounds-0..3 retained-word replay
prefix is clean at Q1114 (this lane, commits on
`research/fable-clanker-round3-bdf4845`; see
`.lane/ROUND3-RETAINED-WORD-BDF4845.md` and
`.lane/PREDECLARATION-ROUND3-BDF4845.md`). The minimal component uses the flag
at round 2 ONLY; round 3 is provably flag-free (its `p` sentinel is the halve
target, not a modular-add source), so it improves on `40d0170`'s unnecessary
round-3 toggle. `SUB4_PP_R3_FORCE_TOGGLE=1` reproduces `40d0170` byte-for-byte
from the independently re-derived `384823f` base.

The `KILL_LIVE_NUMERATOR_ABI_CLOSURE` production-splice falsifier (`34c1b50`,
9805dee line) is now RESOLVED on the `a9af194` base (see
`.lane/FALSIFIER-NUMERATOR-ABI-BDF4845.md` and
`.lane/PREDECLARATION-NUMERATOR-ABI-BDF4845.md`). A four-pair forward∘inverse
probe (`SUB4_PP_NUMERATOR_ABI_PAIR_PROBE=1`) localized the reverse-cleanup
failure to ONE shared cell pair, `signed_mod_add_pm_halve_fused` /
`signed_mod_double_add_pm_fused` (incomplete modular reduction → `value + p`
representative off the production trajectory). The three retained-word-specific
pairs are exact inverses. So the reference-side failure is a property of a shared
nonce-tuned production arithmetic cell, NOT the retained-word architecture. The
splice gate stays closed until that cell is characterized on its production
trajectory or rebuilt bit-exact (priced next overturns in the falsifier doc).

## Current hypothesis

`H9`: retaining one exact 256-bit original denominator word makes the bounded component map injective without a persistent per-round carrier. The full-field prefix now reconstructs/uses/uncomputes signs1/2 through production rounds0..2. Round1's `p` sentinel is reversibly normalized to canonical zero with one local flag, production round2 runs on canonical state, inverse normalization restores the continuation, and the retained sign1 oracle clears the flag. Across4,096 denominators the candidate is Q1114/T550.247 with replay match, phase0, ancilla0, flag0, max_live_sign_bits1, and carrier0. Round3 with the same single cleared flag is the next falsifier.

## Current falsifier

H9 fails if round3 needs a concurrent second normalization flag, cannot clear the one local flag before reconstructing the next sign, grows live state with round count, assumes unavailable predecessor state, or leaves phase/ancilla debt. Extra fixed scratch and T regression are explicit prototype debt rather than automatic KILL. The exact Q1114 full-field prefix is HOLD but does not yet prove production replay replacement. Context-specific free-outer-key, local-terminal, checkpoint, radix, coefficient-absorption, and materializing-decoder negatives remain closed unless a changed premise is named.

## Next action

Hold the exact prefix-code and terminal-tail lanes at their measured boundaries. Teddy's sparse square overturn is exact at standalone Q1148. Commit `384823f` now proves a full-field replay prefix at Q1114, below that component target: rounds0..2, one local sentinel-normalization flag, exact continuation match, and full cleanup. Extend through production round3 with the same single flag cleared before the next sign. Record the binder and per-round T; KILL on concurrent flag, width growth, or phase debt. If clean, name the cheapest production divide-replay slice rather than continuing blind prefix depth. Do not optimize or grind before semantic correctness and cleanup. The separate MUL695 state-selective product route is CLOSED KILL after its fused cell restored Q1278 but missed the T ceiling by2745. Grind stays last.

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
- MUL695 selector commit `343ff86`: predecessor-free 8-bit predicate distinguishes localized terminal `(03,01)` from all four converged `{01,ff}^2` states, cleans Boolean scratch immediately, retains one selector bit, gates the omitted replay cell, and clears after walkback. Deterministic repair-16 passes `0/0/0` at Q1986/T922936.08, but the promoted draw is `16/10/0` and projected score1832950896. Universal repair claim fails at `(03,03)`. Verdict semantic HOLD, current controlled replay shape KILL; a fused controlled replay cell plus selector peak hosting is the only reopen gate.
- MUL695 fused-cell commit `afb10f1`: first repair Q1534/T920514.44; final directly controlled fused cell Q1278/T922528.67 with deterministic repair-16 `0/0/0`. Multiply replay peaks at Q1264 below the unchanged divide Q1278 binder, closing708Q of prototype debt, but rounded T exceeds the strict ceiling by2745. Coherent quantum control cannot skip emitted gates when selector=0. Verdict state-selective product route CLOSED KILL; env-gated code remains only a semantic witness.
- Fable Q1148 visibility audit: sparse square HOLD, materializing decoder KILL, cleanup-contract overturn is next; live-rebased memo `.lane/FABLE-Q1148-VISIBILITY.md`.
- Cleanup collision commit `e06d95d`: exact p=7 fixed-width census finds the first component-local collision at round6 for both divide and multiply; local terminal canonicalization KILL, global/deferred cleanup HOLD behind an enlarged-key gate.
- Outer-key census commit `f990424`: zero-increment classical offset key KILL; one retained denominator word is bounded injective through p31/20 rounds in both directions, with explicit +256Q and recomputation debt. Exact sign-oracle skeleton is next.
- Retained-sign1 skeleton commit `e57dfb4`: exact source-gated prototype Q1033, ABI Q257, extra peak Q776, 15,634 ops, 3,040 emitted/executed T, phase0, ancilla0, carrier bits0. It retains one denominator word, computes/uses/uncomputes one sign, and returns the word cleanly; bounded multi-sign composition is next.
- Retained-signs1..4 commit `16c91fb`: exact bounded candidate Q517 on ABI260, 816 ops, emitted/executed T12, max_live_sign_bits1, persistent_carrier_bits0; independent production-walk reference Q1038/T3560 matches256 target-width denominators covering all64 low-six-bit residues under four high prefixes, with denominator preserved, phase0, ancilla0. Source parent `def24be` differs from current `a9af194` only at the default nonce. Verdict HOLD; sign5 is next.
- Retained-sign5 commit `deb94de`: exact `a9af194` candidate Q520 on ABI261, extra peak259, 930 ops, emitted/executed T118; production reference Q1040/T4070. All512 target-width inputs covering128 low residues under four high prefixes match signs1..5; denominator preserved, shared sign and two scratch cleared after each sign, phase0, ancilla0, carrier0, max_live_sign_bits1. Verdict HOLD; sign6 is next.
- Retained-sign6 commit `6177eda`: exact `a9af194` candidate Q521 on ABI262, extra peak259, 1,551 ops, emitted/executed T724; production reference Q1042/T4580. All1,024 target-width inputs covering256 low residues under four high prefixes match signs1..6. Degree-five/six monomials use the same two scratch plus retained bits8/9 as arbitrary-state dirty bridges, restored within each monomial; denominator preserved, phase0, ancilla0, carrier0, max_live_sign_bits1. Verdict HOLD; T growth is now the named debt.
- Fable scaling audit commits `3e68e90`/`f841bcc`: exact production truth tables through sign14 measure ANF terms2,2,5,11,25,57,115,244,481,1001,2013,4041,8177,16433. This KILLs literal expanded-monomial enumeration as a full698-sign score route. It does not prove a Boolean-circuit lower bound or a scratch-width lower bound; sign6's restored dirty bridges directly falsify that stronger claim. Bounded retained-word replay slices remain HOLD.
- Sign7/replay commit `d4f08d2`: exact low9 sign7 ANF has115 terms/degree7 and passes4,096 target-width cases at candidate Q522/T4000 with two allocated scratch, at most three restored retained dirty bridges, phase0, ancilla0, carrier0, max_live_sign_bits1. The first real two-round F7 replay consumer passes the same4,096 inputs at Q521/T0 with only six intended coefficient continuation bits live. Naive full-field round2 leaves deterministic phase debt; reversible round1-sentinel normalization is the changed-premise reopen.
- Full-field normalization commit `384823f`: production rounds0..2 pass4,096 denominators at candidate Q1114 on ABI768, extra peak346, 8,622 ops, emitted T583, executed T550.247; reference Q1546/T3089.817. One local flag reconstructs sign1, maps the round1 `p` sentinel to canonical zero for round2, restores the continuation, and clears through the same retained sign oracle. Denominator/retained preserved, replay state match, sign/scratch/flag0, phase0, ancilla0, carrier0, max_live_sign_bits1. Raw unnormalized mode fails deterministically, binding the fix.
- Protected-leader cache HOLD commit `a05cca3`: exact `a9af194` cycle has21 clean rows and no average below919784.5; promoted nonce57002259501 at919785.268 remains best. Do not rebuild until a newer read-only cache cycle contains a necessarily new strict beat.

## Credit and shipping note

Fresh human advice from Teddy Pender on 2026-08-22 explicitly directed attention to the tape and mentioned a non-composing 637Q / 1.5M-T component. The promoted `def24be` note credits Teddy prominently for the Burn the House Down experimental discipline without misattributing the nonce-only delta. If a tape architecture becomes a real candidate, its research commit and Stop-Slop-reviewed public note must credit Teddy even more directly. The public model sentence is exactly `Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.` The submission API attribution remains exactly `kimi`.
