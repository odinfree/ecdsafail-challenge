# Paired H64 density: protected b523 versus Q1274 control

Date: 2026-08-23

## Verdict

`DENSITY_PASS`; `GO_CPU_MODEL`; `HOLD_PARITY`; `HOLD_SCAN`; `HOLD_HUNT`;
`HOLD_PROVIDER`; `HOLD_SUBMIT`.

The Q1274 control passes both predeclared 1.10 engineering
non-inferiority margins.  This authorizes the bounded exact CPU-model port, not
a search.

## Frozen identities

- corpus/source predeclaration commit: `056fa8d`;
- byte-exact bake commit: `3b965b8`;
- H64 corpus SHA-256:
  `f8d1cfb4d281c08f69778c7e634ebd4fc9addf2870816cc4ef2bad23800bcf57`;
- Q1274 default: 12,935,433 operations, inherited SHA `61a57ce6...`, Q1274;
- protected opt-out: 12,876,472 operations, inherited SHA `4cb1787b...`, Q1278.

Every nonce has its own operation SHA because the tail nonce is embedded in the
circuit.  The raw receipt SHA below binds every per-nonce operation SHA, count,
Q, channel count, and complete classical mismatch-shot list.

## Full-shot results

Each stream was force-rebuilt and passed through the unchanged 9,024-shot
trusted evaluator at all 64 nonces `444000000000..444000000063`.

| stream | rows | Q | operations/row | classical | phase | ancilla |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| protected b523 | 64 | 1278 | 12,876,472 | 1,069 | 848 | 0 |
| Q1274 control | 64 | 1274 | 12,935,433 | 1,032 | 872 | 0 |

- classical ratio, candidate/protected: `0.965388213`;
- phase ratio, candidate/protected: `1.028301887`;
- combined ratio: `0.993218571`;
- frozen classical ceiling: `1,175.9` candidate faults; observed `1,032`;
- frozen phase ceiling: `932.8` candidate batches; observed `872`;
- paired classical lower/equal/higher rows: `34/4/26`;
- paired phase lower/equal/higher rows: `25/2/37`;
- structural violations: `0`;
- raw 128-row receipt SHA-256:
  `10ecb3139f4280bdf61b44a4416fc6ce301119f259f1e2a343ed283b7862b947`;
- compact per-nonce density ledger SHA-256:
  `4f27faf5daf9d85fcd5e088d55d5d79fd3fe4a5205f638af1e970adf8357b8fa`.

Complete classical masks were retained outside Git for the exact-model gate.
Cross-stream mask equality is neither expected nor claimed: changing the
operation stream changes the Fiat-Shamir ensemble.  Density is adjudicated by
the frozen aggregates above.

## Evaluator and repository guards

- untrusted builder binary SHA-256:
  `c9dd06d538072e58fb665b1165c32b9829af6e2e8b10298f295ebd38f4ed2084`;
- temporary shot-index/no-write evaluator source SHA-256:
  `3c9cce35ae2f6feb6e090d90d62bdff4e70d743854c0b654a287f3c7be1b7890`;
- temporary evaluator binary SHA-256:
  `5f034f9da5295532114210b93578f62e31cf85701cf3f200919831fcc06c7aa9`;
- restored evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- tracked `results.tsv` SHA-256 before and after:
  `eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

The temporary evaluator change only exposed existing mismatch indices and
suppressed writes.  It was removed byte-for-byte before this evidence was
committed.  No generated operation stream, binary, raw log, or result row is in
Git.

## Next gate

Port the source-bound b523 predictor with exact defaults and the generic
low53/high203 coordinate-shell correction already qualified on Q1276.  Require
complete classical mask equality across the candidate H64.  Commit the generic
correction before revealing the frozen disjoint32 evaluator outcomes, then
require 32/32 exact set equality there.
