# Claude Fable takeover: direct rank/unrank Burn lane

Status: `KILL_DIRECT_DECODER` — closed 2026-08-22. The direct reversible
rank/unrank decoder for the 280-wire round-356 checkpoint is killed in every
constructive class: backward sign recovery carries exactly zero local
information (both predecessors are always self-consistent, verified on 71,000
of 71,000 backward steps), the wrapped registers make width violations locally
unobservable, and refuting a wrong sign is an unpruned `2^r` search terminated
only by the round-0 boundary. Full evidence: `.lane/DIRECT-DECODER-KILL-6B5C82C.md`.
Production `src/` remains byte-identical to `6b5c82c`. No hunt, no submission.

Base: exact live source `6b5c82c`

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

Worker: Claude Fable 5, xhigh effort.

## Objective

Test a direct reversible rank/unrank decoder for the round-356 ping-pong checkpoint. The checkpoint is exactly 280 `u/v` wires. Do not rebuild the existing walk with Bennett reconstruction: that route is already killed at a deterministic `+143,000 T` floor.

The open composition target is the sparse-square checkpoint at `Q=1148` with no more than about `102,983` additional deterministic Toffolis. A proposal must jointly account for `pp_div_replay`, square, and multiply co-binders; a local width cut that leaves the global peak unchanged is a falsifier, not a win.

## Gates

- Read the evidence on branch `research/burn-compact-history-6b5c82c` before editing production source.
- Use a strict paired oracle/reference test before any full circuit measurement.
- Preserve the exact gate-off fingerprint from `6b5c82c`.
- Measure Q, emitted T, executed T, operations, and logical/phase/ancilla residuals.
- No nonce hunt unless the architecture clears the fresh live product gate.
- No submission from this lane.
- Temporary evaluators and generated operations never ship at HEAD.
- Finish with production `src/` byte-identical to the intended candidate or exact base, a concise evidence ledger, a neutral commit, and a clean pushed branch.

## Credit policy

Do not add individual credit to ordinary evidence, commits, or experiment notes. If this lane produces a genuine winning result, add one concise attribution in the final winning commit or submission only.

## Current frontier at dispatch

Live SOTA: score `1,173,661,524`, source `6b5c82c`, `Q=1278`, rounded `T=918358`.

This value is only the dispatch snapshot. Refresh it before any score decision.
