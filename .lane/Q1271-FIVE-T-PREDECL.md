# Q1271 five-Toffoli boundary predeclaration

Status: `PREDECLARED / NO ADAPTIVE GRIND / HOLD PROVIDER / HOLD SUBMISSION`.

## Frozen evidence

- live source: `4eb93cb33bbf6a93229fe166b8d511c5e52ee253`
- Fable evidence commit: `9006bcac12a4c6c8cf4c6b17e3135f9898ddd1fb`
- live score: `1,163,831,339` (Q1273 / rounded T914243)
- Q1271 strict rounded-T ceiling: 915681
- measured Q1271 geometry: default-off `doubled_out` eviction plus
  `SUB4_PP_PEAK=1271` and `SUB4_SQUARE_LADDER=241`
- inherited full result: Q1271 / exact T915685.693 / rounded T915686 /
  score `1,163,836,906` / channels `13/11/0`
- boundary: 5 rounded Toffoli above the strict live-beat ceiling

The inherited eviction was implemented and reverted in the Fable lane and was
not independently falsified. This lane must reconstruct it from the named
identity, not recover an unreviewed temporary diff.

## One structural family

The only semantic source change is a default-off lifecycle for `doubled_out`
inside `signed_mod_double_add_pm_fused`: prove its live value equals the parity
of still-live wires, clear and free it only across the idle fused-fold interval,
then allocate and rematerialize the identical value before inverse cleanup.
No second carrier, tape, retained word, ladder rewrite, width repair, selector
change, or unrelated arithmetic optimization is allowed.

## Ordered gates

1. Rebuild the default source byte-exact and reproduce Q1273/T914242.763 and
   the 0/0/0 incumbent before edits.
2. Implement the default-off lifecycle and add a focused forward/inverse,
   value, relative-phase, and ancilla miter covering both signs, carry edges,
   zero/one, field boundaries, and every branch that reads `doubled_out`.
3. Reproduce Q1271 with the exact 1271/241 environment. Require the focused
   miter plus the full ping-pong component and square component to pass.
4. Reproduce the inherited default-nonce full result within exact operation
   identity and evaluator determinism before opening calibration rows.

## Frozen eight-nonce calibration

Only after gates 1-4 pass, run the unchanged 9,024-shot evaluator exactly once
on each of these predeclared tail nonces, in this order, with no adaptive
extension:

1. `65700024945641`
2. `65700024945642`
3. `65700024945643`
4. `65700024945644`
5. `65700024945645`
6. `65700024945646`
7. `65700024945647`
8. `65700024945648`

For each row record operation count/hash, Q, exact and rounded T, full
classical/phase/ancilla channels, and first mismatch. Restore `results.tsv`
after sealing hashes. Stop after row eight even if no row crosses the ceiling.

A dirty row with rounded T <= 915681 proves only `SCORE_GO / VALIDATION_DIRTY`
and may justify a later source-bound screen lane. A candidate requires a fresh
live refresh and unchanged full `0/0/0`; this lane has no submission authority.

No web search, provider compute, range declaration, fleet action, adaptive
nonce scan, submission, public note, or external message is authorized. Do not
commit `ops.bin`, binaries, evaluator rows, raw logs, traces, caches, or helper
artifacts. Commit and push durable source, miter, receipts, and state only.
