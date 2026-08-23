# Predeclaration — production-reachable fused replay inverse

Written: 2026-08-23T07:56:59Z, before any model or semantic source edit.

## Frozen source

- Worktree: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/b523-fused-reachable-inverse`
- Branch: `research/b523-fused-reachable-inverse`
- Exact parent: `9fb89d3e6d0cf1c26a880dcacd3c560c3970ef7a`
- Parent tree: `ba9a1dd6e23a110166c77e9d4718669ce29e40a3`
- `src/point_add/pingpong_div.rs` SHA256:
  `6175fb744e2a9a95f537db0bbd5d7e7d9b0d89e34ca1664e7e54e37a2405bbe8`
- `src/point_add/mod.rs` SHA256:
  `f3cc65a5d49052a5f6388cd8348324174f0c022d0a028fb8d363e985163c466f`
- `Cargo.lock` SHA256:
  `42ff16919e551891ad1b21821329b116d133194245a0e0734a33573dfe598e07`
- Protected parent default stream, independently recorded at `9fb89d3`:
  50,798,742 bytes, SHA256
  `e33245d491a16192068ef7024a2c82375047c17af3c8f802c81066de0568cb0a`.
  This lane must reproduce it freshly before candidate comparison.

## One family only

Characterize the actual production call-boundary trajectory shared by
`signed_mod_add_pm_halve_fused` and
`signed_mod_double_add_pm_fused`, then do exactly one of:

1. implement one default-off inverse specialized to a bit-exact predicate
   proved on that production-reachable trajectory; or
2. terminally falsify that family when the reachable support is not closed,
   the needed representative bit is not recoverable from inverse-live state,
   the focused miter fails, or exact Q/T pricing fails.

No second inverse design, generic `[0,p)` repair, fold-window tuning, nonce
change, rescue family, or unrelated retained-word/square/tape edit is in scope.
The existing arbitrary-input pair probe remains a negative control, not a
license to broaden the family.

## Frozen fixtures

### P64 — complete production composition trace

Reuse the exact 64 valid secp256k1 affine point pairs already defined by
`pingpong_point_add_simulator_selfcheck`:

- point source: `SHAKE256("pingpong full affine point-add composition gate")`;
- draw two little-endian 256-bit scalars, multiply the secp256k1 generator;
- reject infinity and equal-x pairs exactly as the existing selfcheck does;
- simulator randomness:
  `SHAKE256("pingpong full affine point-add simulator randomness")`.

Under one diagnostic-only env gate, record every production round-`>=2` entry
and exit for both fused cells in both public directions. A row is fixed as:

```text
direction, call_index, round, sign, source[256], target_before[256], target_after[256]
```

The recorder may observe builder op offsets and live wire IDs but may add no
operation and allocate no circuit wire. The receipt must state row count, call
count by cell/direction, canonical/noncanonical counts, exact range/parity/high-
window invariants, and one SHA256 over rows in the order above. Raw trace files,
logs, and binaries are not committed.

### C64 — focused cell replay

Freeze the unique `(round, sign, source, target_before)` tuples observed by P64
and replay each through the old forward cell, the proposed inverse, and their
composition. Preserve duplicate multiplicities in the receipt while hashing
the deduplicated corpus separately. This fixture must validate target value,
source, sign, phase, and every non-ABI qubit.

### A16 — negative control

Keep `SUB4_PP_NUMERATOR_ABI_PAIR_PROBE=1` unchanged. At the parent it reports
the shared pair as `restore_fail=3 phase_fail=2 ancilla_fail=0`; full-width
windows leave the two known `seed+p` representative failures. A reachable-set
candidate need not repair A16, but it may not weaken, delete, or relabel it.

Fixture definitions are frozen here. Claude may implement their diagnostic
harness, but may not replace their seeds, filter failed rows, or substitute a
hand-picked corpus.

## Kill gates

1. **Source/default gate.** Before and after the experiment, a fresh normal
   build must reproduce the protected parent byte count and SHA256 exactly when
   the candidate flag is absent. Any default drift is terminal.
2. **Trajectory gate.** P64 must be the unmodified production composition and
   trace all shared fused calls without changing its op stream. P64 itself must
   finish classical/phase/ancilla `0/0/0`. If the trace is incomplete or a
   claimed invariant has a counterexample, kill the claim.
3. **Visibility/closure gate.** Any specialization predicate must be computable
   only from state live at that inverse call (plus its compile-time round and
   direction). If two reachable rows with the same inverse-visible state demand
   different bit-exact predecessors, or if the predicate needs a stored branch,
   hidden transcript, oracle, or added persistent carrier, terminally falsify
   this family.
4. **Focused miter gate.** On every C64 row, require exact forward value and
   proposed inverse value, preserved `source` and `sign`, phase `0`, ancilla
   `0`, and bit-exact forward-then-inverse identity. No equality merely modulo
   `p` is accepted. Run both call orientations used by production.
5. **Economic gate.** Fresh leader score is `1,169,101,620`; a candidate must
   satisfy `Q * rounded_T < 1,169,101,620`. Independently recomputed strict
   ceilings are:

   | Q | maximum rounded T | accepted product | first losing product |
   |---:|---:|---:|---:|
   | 1148 | 1,018,381 | 1,169,101,388 | 1,169,102,536 |
   | 1114 | 1,049,462 | 1,169,100,668 | 1,169,101,782 |

   Measure emitted operations, CCX/CCZ, average executed Toffoli, and peak
   owner; do not project a score from a cell-only delta. If the exact candidate
   cannot clear a strict ceiling at its measured Q, kill it without tuning.
6. **Composition gate.** Only after gates 1-5 pass: run the protected square
   component, deterministic point-add64, then a fresh full 9,024-shot trusted
   evaluation. Required channels are classical/phase/ancilla `0/0/0`, with
   exact Q/T/ops/hash recorded. A failure seals the one family; no rescue edit.

## Model and authority boundary

One Claude Fable 5 session at high effort may characterize and implement this
single family. It may read/edit only the isolated lane and must not commit,
push, access network services, change nonces/default bytes, launch providers or
hunts, submit, or publish. Human-side verification owns builds, evaluation,
receipts, spend append, commit, and push.

## Terminal receipt

The lane ends with either a strict-score, full-clean candidate or a durable
`KILL` falsifier naming the first fired gate. Failed candidate source is removed
before the terminal commit. Commit only source (if it wins) and compact `.lane`
evidence; exclude `target/`, `ops.bin`, `score.json`, logs, binaries, generated
traces, and `results.tsv` rows.
