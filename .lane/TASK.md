# Q1271 operandless fused-fold descent

Predeclared: 2026-08-23, before the PEAK1271/LADDER241 baseline build and
before any operandless candidate edit or output.

## Scope and identity

- Isolated worktree:
  `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/b523-q1271-operandless-fold`.
- Branch: `research/b523-q1271-operandless-fold`.
- Exact base/source seal:
  `14608572e84daf89397768c43ac0d812c714c3bd`, tree
  `d56979a2d5b4ac32bb429dd5858211d3bb7eb196`.
- Protected Q1272 candidate geometry:
  `SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242
  SUB4_PP_FOLD_SELECTOR_EVICT=1`.
- Protected Q1272 identity: 12,908,488 operations, SHA-256
  `678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0`,
  Q1272/T914727.660, full `18/13/0`.
- Live anchor reopened immediately before the base seal: source `b523ecf`,
  score 1,169,101,620. The dispatched strict Q1271 rounded-T ceiling is
  919,828.

No network, provider, remote, predictor, range, nonce hunt, submission,
public note, incumbent edit, or second structural family is authorized.
Generated operations, results, binaries, logs, and temporary evaluators stay
outside Git.

## Overturn ledger and exchange rate

| assumption | wall | overturn | cheapest falsifier |
|---|---|---|---|
| `fused_fold_maskfree` needs one roving materialized operand qubit across all 51 internal carry positions | after selector eviction, the requested PEAK1271/LADDER241 row may remain at Q1272 | distribute the selector XOR algebra directly into the carry and reverse-phase corrections, retaining no operand wire | first freeze the exact Q1271 owner census, then an env-gated exhaustive small-width/multi-selector miter and a measured full owner profile |

At T about 914,728, one qubit is worth about 720 T at constant product. The
live Q1271 gate permits roughly +5,100 rounded T over the protected Q1272 row.

For secp256k1 `f = 0x1000003d1`, fold width 53 has 51 internal positions,
all selector-nonempty, with selector multiplicity sum 58. Relative to the
roving-operand path, the prescribed forward GF(2) expansion statically adds
`2*58 = 116` emitted CCX per fused-fold call. Reverse correction adds only
classically conditioned CZ operations, not Toffoli. Using the previously
measured 698 live fused calls, the first-order price is therefore about
+80,968 emitted/executed T, far above the score headroom, while removing about
423 Clifford operations per call. This is a deliberately hostile static price
falsifier; the exact implementation is still measured once because it tests
whether removing the operand changes the binding composition and validates the
algebraic family. No tuning may follow a price failure.

## Stage A: freeze the unmodified Q1271 co-binders

Before Claude or any source edit:

1. clean release-build the unchanged sealed source;
2. build with exactly
   `SUB4_PP_PEAK=1271 SUB4_SQUARE_LADDER=241
   SUB4_PP_FOLD_SELECTOR_EVICT=1`;
3. record operation count, complete operation SHA, measured Q, unchanged full
   9,024-shot T and channels;
4. run `PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1`, record every peak owner,
   exact peak operation index and phase;
5. rerun a bounded B0 census around that exact peak and record every live
   source owner summing to the measured Q.

This stage is characterization, not a gate fitted after the candidate. Its
receipt is committed and pushed before Claude starts.

## Single authorized candidate family

Add one default-off env flag, named `SUB4_PP_FOLD_OPERANDLESS=1`, only inside
`fused_fold_maskfree`. Keep the selector-empty branch byte-for-byte protected.
For selector-nonempty positions, remove the allocated roving `operand` qubit
and use this exact GF(2) expansion.

Let `S = xor(selectors)`, previous carry `p`, and pre-toggle accumulator bit
`a`. The current carry delta is

```text
(S xor p)(a xor p) xor p = S*a xor S*p xor p*a.
```

Forward at each selector-nonempty position:

1. for every selector `c`, emit `CCX(c,a,carry)` and
   `CCX(c,p,carry)`;
2. emit `CCX(p,a,carry)`;
3. emit `CX(p,a)`.

Reverse at each selector-nonempty position, after `carry ^= p` and `Hmr`:

1. correct `(S xor p)&acc` with `cz_if(p,acc,m)` and one
   `cz_if(c,acc,m)` for every selector `c`;
2. emit `CX(c,acc)` for every selector `c`.

No other arithmetic, fold width, rounds, R1/R2, BREAK values, tape/replay
geometry, selector lifecycle, carry schedule, erasure, or source default may
change. Candidate geometry combines the existing selector eviction with
`PEAK1271/LADDER241` and this operandless flag.

## Claude implementation lane

Use Claude Fable 5 at high effort, with Opus fallback and maximum modeled cost
$20. Claude receives the exact Stage-A receipt plus the algebra above. It may
edit only the bounded source/selftest/evidence files in this worktree. Claude
must not commit, push, use network/provider resources, hunt, submit, or modify
tracked generated files permanently; Codex independently reviews and seals.

## Frozen gate order

Stop at the first failure and remove any failed candidate source while
retaining durable evidence.

1. Protected opt-out reproduction: exact Q1272 count/SHA/Q/T/channels above.
2. Focused exhaustive/miter gate covering widths small enough for exhaustive
   input states plus the real 53-bit multi-selector schedule: protected and
   operandless lane values identical, classical model exact, full phase mask
   zero, every non-input ancilla zero, selector-empty path exercised, every
   selector multiplicity exercised, and exact op deltas attributed.
3. Clean candidate artifact and complete owner/census profile. Require measured
   Q <=1271; every square, divide replay, multiply replay/walkback, and new fold
   owner must be <=1271. If the walk binder does not descend automatically,
   freeze its exact live set and stop with no rescue edit.
4. Require exact average T with rounded T <=919,828. A static or measured price
   failure stops before broader composition work.
5. Existing product-square and complete point-add 64-lane selftests: exact
   values, phase zero, ancilla zero, Q<=1271.
6. Unchanged full 9,024-shot evaluator: Q<=1271, rounded T<=919,828, ancilla
   zero; record classical and phase counts and first reported failure. A dirty
   result remains `HOLD_HUNT` and is never a submission candidate.
7. Restore `results.tsv`, remove generated artifacts/build products, review the
   complete diff and provenance, append exact Claude cost to
   `/Users/olifreuler/ecdsa-ops/SPEND.md`, then commit/push only useful clean
   source/evidence. If the family fails, commit/push the terminal falsification
   without failed source.
