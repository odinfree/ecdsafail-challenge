# b523 balanced-ladder experiment ledger

| id | exact route | artifact | fixed diagnostic | unchanged full / H64 | verdict |
|---|---|---|---|---|---|
| B0 | `b523ecf`, all candidate knobs unset | 12,876,472 ops, SHA `4cb1787b...`, Q1278 | byte reproduction | official T914789.886, `0/0/0` | protected anchor |
| C1 | `SUB4_PP_PEAK=1276`, ladder unset at 248 | 12,901,294 ops, SHA `395df60f...`, Q1278 | T915872.42, `0/0/0` | not run | square co-binder confirmed |
| S76 | `SUB4_PP_PEAK=1276 SUB4_SQUARE_LADDER=246` | 12,901,678 ops, SHA `d460c396...`, Q1276 | T915914.61, `0/0/0` | inherited T915834.428, `17/16/0`; H64 `1048/883/0` | `GO_MODEL`, hold hunt |

## Exact falsifiers

| assumption | cheapest exact test | result |
|---|---|---|
| Lowering replay peak alone realizes Q1276 | peak-only forced build | falsified: square independently pins Q1278 |
| The coordinated pair remains pinned by a third owner | forced pair build and profile | falsified: global Q1276, divide replay owns first peak |
| The lower-Q pair loses product economics | unchanged full-shot T and exact scorer | falsified: projected margin 497,436 below refreshed live |
| The repair exposure catastrophically worsens faults | complete paired H64 | falsified on corpus: combined count +0.73%, ancilla zero |
| The promoted nonce transfers | unchanged inherited full | falsified: `17/16/0` |
| Structural success authorizes scanning | require source-bound predictor qualification | held; no hunt or canary |

The historical source clue selected a bounded composition; the exact current
source measurements establish the verdict. No result here is submission-ready.
