# Burn explorer: collapse the multiply-walkback co-binder

Created: 2026-08-22
Source: `6b5c82c`
Branch: `research/fable-burn-6b5c-mulwalkback`
Status: CLOSED 2026-08-22 — falsifier KILL; protected leader untouched
(gate-off hash `c0eddceaca5a76fc2307a68efc7a2aa1` verified before/during/after;
evidence: `src/point_add/memory/12-mulwalkback-replay-lifetime.md`)

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

Execution provenance: Claude Fable 5, max effort, took over this unfinished
objective after the Kimi account reached its cycle limit. The campaign model
declaration above is preserved verbatim; this lane does not conceal who ran the
actual experiment.

## Protected leader

- Live source: `6b5c82c`.
- Trusted metrics: Q1278 / rounded T918358 / score1173661524.
- Trusted contract: forced clean build followed by the unchanged 9,024-shot
  evaluator with classical/phase/ancilla exactly `0/0/0`.
- This explorer cannot hunt, spend provider credit, push, publish, or submit.

## Teddy Pender overturn

Wall: exact-live profiling places `pp_mul_walkback` on the three-way Q1278
plateau. Its live set includes the resident walk/sign history, caller `y`, the
replay allocation, and walkback ladders.

Assumption to overturn: the full 256-wire replay allocation must remain live
through multiply walkback after its last replay consumer, and its storage
cannot host any walkback state without changing the affine ABI.

Overturn condition: a source-indexed dependency/lifetime proof finds a clean
interval in which all or part of the replay allocation can be released,
aliased, or used as restored scratch while the normal stream remains exact.

Cheapest falsifier: map every read/write/free of the replay allocation across
`pp_mul_replay` and `pp_mul_walkback`, identify its last semantic consumer and
the first walkback peak, and kill immediately if any live dependency crosses
the entire binding interval. Only if the map survives, build a 4-8-round
symmetric forward/reverse slice with fixed scratch and explicit phase/ancilla
cleanup.

## Direction and saddle budget

- First invariant: remove or host at least one replay-allocation lane at the
  measured `pp_mul_walkback` peak without increasing another Q1278 owner.
- Composition target: combine a surviving multiply cut with Fable's streamed
  history and the exact-live sparse-square lane; no single-wall Q claim.
- Strict complete-circuit ceilings: Q1270 T<=924142; Q1182 T<=992945.
- Budget: two lifetime/dependency falsifiers plus one bounded symmetric slice,
  or four hours. No parameter sweep and no nonce work.

## Outcome (2026-08-22, Claude Fable 5)

The census was reproduced and the last-consumer/first-peak falsifier run on the
exact leader stream. Verdict: **KILL** — the assumption's premise does not exist
in the live stream. Measured: the replay allocation is freed at a zero-op gap
after its last semantic consumer (op 11,990,464 → free by 11,990,720), before
the final 356 walk-back rounds; all 619 `pp_mul_walkback` binding instants
(ops 8,976,984 .. 11,985,135) lie inside the allocation's live span with zero
after the free; at the replay and lower-batch binders the allocation is an
operand of the binding add itself. Alias is algebraically dead from round one;
dirty hosting is blocked by the measured-cleanup clean-ancilla requirement on
every binding ladder; the tie law (pp_div_replay + square also at 1278) makes
any multiply-only width cut zero-score. The gated 4-8-round slice was therefore
NOT built. Full source-indexed map, censuses, and composition numbers:
`src/point_add/memory/12-mulwalkback-replay-lifetime.md`. Temporary census
instrumentation was hash-verified neutral and reverted; no hunt, spend, push,
or submission occurred.

Credit Teddy Pender for the protected leader, bounded saddle, falsifier-first
discipline, and grind-last rule.
