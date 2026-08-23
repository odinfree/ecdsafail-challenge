# Q1272 selector eviction: paired H64 result

Date: 2026-08-23

## Verdict

`DENSITY_PASS`; `STRICT_T_PASS`; `GO_CPU_MODEL_GATE`; `HOLD_HOLDOUT`;
`HOLD_PARITY`; `HOLD_SCAN`; `HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The Q1272 selector-eviction stream passes both frozen 1.10
non-inferiority ceilings against its immediate Q1273 parent.  Every one of the
128 rows passes its Q, operation-count, 9,024-shot, ancilla, and strict-T
guards.  This permits a separately predeclared exact CPU-model qualification;
it does not authorize a range or hunt.

## Source, corpus, and harness binding

- exact source commit:
  `14608572e84daf89397768c43ac0d812c714c3bd`;
- exact source tree: `d56979a2d5b4ac32bb429dd5858211d3bb7eb196`;
- density predeclaration commit: `deb81b0b4ba0345687e681c447c245c51dce5adb`;
- H64 corpus SHA-256:
  `f8d1cfb4d281c08f69778c7e634ebd4fc9addf2870816cc4ef2bad23800bcf57`;
- predeclaration SHA-256:
  `edc381e4ddd36b9158e50f2f2fc0147009b831e1d37c60bddc558fe3149471dc`;
- clean builder binary SHA-256:
  `0aecd50563ddf9c25a61b9e8edf8c1539adc7417fa4c0458b5f1d484d7c3bce6`;
- stock evaluator binary SHA-256:
  `6c4aa7f5622f180d20433d8b3b2812b036592c91e24ebdd27048393dd83d4b92`;
- temporary output-only evaluator source SHA-256:
  `706a50f5e23aefed04aaeb7a6fbe66a201ec6f0a53ba52026bd19730c2832248`;
- temporary output-only evaluator binary SHA-256:
  `06e56929e9c6ccbc9399682df34bb593e32875f78ddd1ba004b7c195c5cbcc14`;
- restored evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- tracked `results.tsv` SHA-256 before and after:
  `eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

The temporary evaluator only emitted existing mismatch indices and exact
integer statistics before the normal failure exit, and suppressed result-row
writes.  It did not change operation loading, Fiat-Shamir state, inputs, RNG,
simulation, comparisons, channel accounting, gate totals, or exit status.  Its
source was restored byte-for-byte before this evidence commit.

## Byte reproduction before H64

At the inherited nonce `81327465284`:

| stream | operations | operation SHA-256 | Q | total Toffoli / shots | classical/phase/ancilla | receipt SHA-256 |
| --- | ---: | --- | ---: | ---: | --- | --- |
| Q1273 parent | 12,892,399 | `f225dae80d6d81a5e1d61d9ac32b74df48ca1b40d9ff5905bb61acf66c9ceb15` | 1273 | `8249811492 / 9024` | `29/15/0` | `174c0556852309dc37adf210fc960c50c6e86e538aebf6f3d3ead682461f7554` |
| Q1272 candidate | 12,908,488 | `678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0` | 1272 | `8254502402 / 9024` | `18/13/0` | `74efae8fd3be2c4784bb9c3c15cbf4fa566c175d6e30952ad1fd23eb37e7c597` |

Both reproduce their independently sealed structural receipts exactly.

## Frozen H64 totals

| stream | rows | Q | operations/row | classical | phase | ancilla | exact mean T | min T | max T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Q1273 parent | 64 | 1273 | 12,892,399 | 1,490 | 1,087 | 0 | 914203.818061558 | 914188.659796099 | 914215.946919326 |
| Q1272 candidate | 64 | 1272 | 12,908,488 | 1,457 | 1,107 | 0 | 914726.718348293 | 914705.705119681 | 914743.088763298 |

- candidate/parent classical ratio: `0.977852348993`;
- candidate/parent phase ratio: `1.018399264029`;
- candidate/parent combined ratio: `0.994955374466`;
- frozen ceiling for each ratio: `1.10`;
- per-nonce classical lower/equal/higher: `32/4/28`;
- per-nonce phase lower/equal/higher: `28/8/28`;
- parent total Toffoli numerator/shots:
  `527985616268 / 577536`;
- candidate total Toffoli numerator/shots:
  `528287610008 / 577536`;
- structural or shot-count violations: `0`;
- compact 64-pair ledger SHA-256:
  `ed88d7881d28cc052a14a1fe574132382a8665b36ad3e4fdb70b814d8c76e36f`;
- raw 128-row receipt SHA-256:
  `90a8d5c33fa62413befd337667bbe272f8bc7fe9e6e4f397df0192b2955efe9d`;
- 128-log manifest SHA-256:
  `671f85777ab23261e909ee2c2d656650ebdf812ed10e855344948900e1379330`;
- complete 128-operation manifest SHA-256:
  `6e1963431b41539cf131384f68e50de84a1b171ce0d707e2e25fed4786e460fa`.

The highest candidate row rounds to T914743, 4,362 below its Q1272 ceiling;
its row score is 1,163,553,096, leaving 5,548,524 points below the frozen live
anchor.  The highest parent row rounds to T914216, 4,167 below its Q1273
ceiling.

## Protected b523 context, exact reuse only

The existing protected b523 raw receipt is present and reproduces its required
SHA-256
`10ecb3139f4280bdf61b44a4416fc6ce301119f259f1e2a343ed283b7862b947`.
Its 64 protected rows all pass Q1278, 12,876,472 operations, and ancilla zero;
their exact extracted-row SHA-256 is
`a9f06faefa2768a93c03c65db5223342015ac8e93124db15b1452121e30a3416`.
Totals are 1,069 classical and 848 phase.  The Q1272/protected ratios are
1.362956033676 classical, 1.305424528302 phase, and 1.337506520605 combined.
This is context only: the frozen density gate compares the selector eviction
to its immediate Q1273 parent, isolating the architectural change.

## Next gate

Import only the source-bound Q1272 predictor from
`research/b523-q1272-selector-model-port@b3f71f7`, then predeclare complete
classical-mask equality on this H64 plus a disjoint holdout before executing
the predictor on either corpus.  Raw masks stay outside Git; durable evidence
contains only hashes and counts.  No range, CUDA, provider, hunt, submission,
or incumbent action is authorized until CPU exactness closes.
