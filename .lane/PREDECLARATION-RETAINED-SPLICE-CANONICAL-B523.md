# Predeclaration — canonical retained-word splice

Written: 2026-08-23T08:32:18Z, before any model or semantic source edit.

## Frozen source and protected control

- Worktree:
  `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/b523-retained-splice-canonical`
- Branch: `research/b523-retained-splice-canonical`
- Exact parent: `ab578fe491f7d4988cb1dca7191199758178020e`
- Parent tree: `036e015eccdb292c30578a002b02374ae5f7c893`
- `src/point_add/pingpong_div.rs` SHA256:
  `39ccb1c8b71e4fc6c7bcb670680a6b1a02034a10dc6c2364c6ac0a040f3a0129`
- `src/point_add/mod.rs` SHA256:
  `5dc6709325f0b4b28dd8c1780ab3b98df7ae68e8cb45d73fb83bd7310f6288c8`
- `Cargo.lock` SHA256:
  `a898022e584c7bba293bc5c459c7a02bcd88c498e9b2013c1498ee66df5ab7e2`
- Protected absent-flag stream inherited from the exact parent: 12,972,785
  operations, 50,798,742 bytes, SHA256
  `e33245d491a16192068ef7024a2c82375047c17af3c8f802c81066de0568cb0a`.
  It must be reproduced freshly after the experiment.
- Protected full control inherited from the exact parent: Q1278,
  average executed T919785.268 (rounded 919785), full 9,024-shot
  classical/phase/ancilla `0/0/0`.

The parent is the terminal production-trajectory audit, not a speculative
source line. Its P64/C64 receipts establish that the existing pair
`signed_mod_add_pm_halve_fused` and
`signed_mod_double_add_pm_fused` is bit-exact on the frozen canonical
production support:

```text
P64 calls halve|divide=696 double|multiply=694 rows=88960
P64 noncanon_source=0 noncanon_target_before=0 noncanon_target_after=0
P64 rows_sha256=798b8c1c2f92b8af4b95a2b2df7ec7a7b7238e8a957614ccda993ccb77d4e63e
C64 unique_tuples=79205
C64 corpus_sha256=2e3ca70d1879b85ddcaae72fa571424e955a4b92ea3523ac4fa0bc8659ef5126
C64 target/source/sign/phase/ancilla=0/0/0/0/0
```

The arbitrary-input A16 probe remains the immutable negative control
(`restore_fail=3 phase_fail=2 ancilla_fail=0`). This lane may not broaden the
pair's domain or relabel that failure.

## Exactly one family

Attempt one default-off **retained-word splice**: keep one exact 256-bit
original denominator word, reconstruct and immediately uncompute replay signs
from that word, and use the current fused halve/double pair unchanged while
removing resident per-round sign state. The splice may recompute a sign or a
bounded value-walk prefix from the retained word, but it may not retain a
round-indexed carrier, hidden transcript, selector vector, or second denominator
copy across replay.

The following are explicitly outside this family: editing either fused cell;
adding a final modular reduction; changing fold/compare/chunk windows, rounds,
plans, nonces, tail bytes, square code, or point-add semantics; switching to an
arbitrary-`[0,p)` inverse; opening a second decoder, tape codec, rescue family,
or tuning pass.

All candidate behavior must be behind one new diagnostic/candidate environment
gate. With that gate absent, the production path and bytes must remain exact.

## Frozen fixtures

### R64 — canonical production support

Reuse the exact 64 valid secp256k1 affine point pairs and rejection procedure
already frozen by P64:

- point source: `SHAKE256("pingpong full affine point-add composition gate")`;
- two little-endian 256-bit scalars multiplied by the generator;
- reject infinity and equal-x pairs exactly as
  `pingpong_point_add_simulator_selfcheck` does;
- simulator randomness:
  `SHAKE256("pingpong full affine point-add simulator randomness")`.

The untouched reference must re-create the ordered P64 boundary corpus above.
For every candidate fused-cell call, `(direction, round, sign, source,
target_before)` must equal a reference boundary from the same shot and call
position, not merely be congruent modulo `p`. Every source, target-before, and
target-after must remain canonical `< p`.

### NM64 — nonzero production midpoint

The first and load-bearing fixture is the complete retained splice on the R64
divide/multiply inputs, started from the exact untouched production pre-replay
state. The harness must capture the actual denominator, numerator/coefficient
registers, round, direction, and cell boundaries from that reference execution;
it may not inject a hand-picked numerator or reuse the old all-zero sentinel
prototype as evidence.

The receipt must prove that each of the 64 lanes has a genuinely nonzero
coefficient midpoint (report zero/nonzero counts and a SHA256 over ordered
denominator, numerator, x, y, direction, round checkpoint values). A fixture
with any lane silently filtered, replaced, or left only in `{0,p}` does not
open the gate.

Run the retained-word forward splice and its complete reverse cleanup using
only the unchanged fused pair at the frozen matching call boundaries. Require
bit-exact restoration of denominator, numerator, both coefficient words, and
retained word; all reconstructed signs, oracle scratch, normalization flags,
and other non-ABI qubits must finish zero; phase and ancilla channels must be
zero. Equality only modulo `p` is a failure.

### M64 — focused candidate/reference miter

Only after NM64 closes exactly, compare the default-off candidate with the
untouched production reference on all R64 lanes and every splice boundary.
Require exact ABI values, exact source/target values, exact retained-word
restoration, phase `0`, ancilla `0`, and no persistent state whose width grows
with the round count. Preserve the P64 multiplicity and ordered digest in the
receipt; no failed row may be filtered.

## Ordered kill gates

1. **Nonzero-midpoint closure first.** NM64 must be production-derived,
   nonzero in every lane, call-position-identical to the frozen canonical
   support, and close bit-exactly with value/phase/ancilla `0/0/0`. Any
   noncanonical boundary, corpus drift, missing reverse predecessor, persistent
   round-indexed state, representative `value+p`, phase debt, or dirty qubit is
   a terminal KILL. No candidate economics or rescue edit follows.
2. **Protected default, then focused miter.** Only after Gate 1 passes, build
   once with the candidate flag absent and reproduce 12,972,785 operations,
   50,798,742 bytes, and the protected SHA256 exactly. Then run M64 and require
   exact value/phase/ancilla closure at every boundary. Any drift or mismatch is
   terminal.
3. **Measured economics only after exactness.** Only after Gates 1 and 2 pass,
   build the complete default-off candidate and measure, rather than project,
   emitted operations, CCX/CCZ, average executed Toffoli, peak qubits, and peak
   owner. The fresh leader is `1,169,101,620`. This family must reach Q<=1114;
   at Q1114 its strict rounded-Toffoli ceiling is:

   ```text
   T <= 1,049,462
   1114 * 1,049,462 = 1,169,100,668  (accepted)
   1114 * 1,049,463 = 1,169,101,782  (losing)
   ```

   For Q<1114 recompute the strict product ceiling. Q>1114, an unmeasured
   projection, or a rounded T above the applicable strict ceiling is terminal.
   There is no tuning pass.
4. **Composition only for an economic exact candidate.** Run the protected
   square component, deterministic point-add64, then a fresh full 9,024-shot
   trusted evaluation. Require classical/phase/ancilla `0/0/0` and record exact
   Q/T/ops/hash. Failure seals the family.

## Model and authority boundary

Use exactly one Claude Fable 5 high-effort session with a maximum total spend
of `$20` for this single family. The model may read and edit only this isolated
lane. It may not execute builds, commit, push, access network services, launch
providers or hunts, change a nonce, submit, or publish. Human-side verification
executes the gates in the order above and owns the spend receipt, durable memo,
commit, and push.

The lane ends as either one strict-score, full-clean candidate or a scoped
terminal `KILL` naming the first fired gate. Failed candidate source is removed
before the terminal commit. Commit only durable source (if it wins) and compact
`.lane` evidence; exclude `target/`, generated operation streams, scores,
traces, logs, binaries, and `results.tsv` rows.
