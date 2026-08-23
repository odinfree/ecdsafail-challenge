# Q1274 three-stream H64 tiebreak — terminal result

Date: 2026-08-23. Live benchmark was reopened at source `b523ecf`,
score `1,169,101,620 = Q1278 * T914790`.

Every stream used the frozen nonces `444000000000..444000000063`, the
unchanged 9,024-shot evaluator, and a fresh build per nonce. There were no
missing rows, structural mismatches, or nonzero ancilla rows.

| stream | Q | operations | classical | phase | combined | ancilla | protected verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| protected `b523ecf` | 1278 | 12,876,472 | 1,069 | 848 | 1,917 | 0 | reference |
| Q1274 control | 1274 | 12,935,433 | 1,032 | 872 | 1,904 | 0 | PASS |
| Q1274 + B1=24 | 1274 | 12,879,923 | 1,504 | 1,083 | 2,587 | 0 | FAIL |

The frozen protected ceilings were classical <=1,207, phase <=971, combined
<=2,102, with ancilla exactly zero. Control passes all four. B1=24 fails all
three density ceilings.

Against control, B1=24 adds 472 classical faults and 683 combined faults. The
predeclared materiality allowances are floor(3*sqrt(2*1032)) = 136 classical
and floor(3*sqrt(2*1904)) = 185 combined. It therefore also fails the
score-optimal-vs-control condition by a wide margin.

Selection: carry Q1274 control forward for source-bound predictor
qualification. Reject B1=24 from hunting despite its lower Toffoli count.

The paired no-write harness captured exact full classical shot masks but did
not persist per-row Toffoli values. The protected serial reproduction did
reproduce mean T `914783.503250`. Density adjudication does not use T. The
control score projection remains bound to its earlier unchanged full row:
Q1274/T917227.881, rounded product `1,168,548,472`, 553,148 below the reopened
frontier. A future clean nonce must receive its own unchanged full T result.

Evidence identities:

- protected serial ledger (header included):
  `c569756de2fd4ca7aacd7f900fb0624bb9a0ec4ec957f7979e2a884368c95837`;
- paired protected/control raw rows:
  `10ecb3139f4280bdf61b44a4416fc6ce301119f259f1e2a343ed283b7862b947`;
- B1=24 raw rows:
  `24fefabffbea03c88237fb2358859afd152226185bdd38b7b1ab44bb25796fcf`;
- tracked `results.tsv` restored exactly:
  `eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

`.lane/H64-AUDIT.tsv` is the compact per-nonce count audit. Raw shot masks,
operation files, evaluator logs, binaries, and generated result rows remain
outside Git. No range, predictor deployment, provider action, hunt,
submission, or public note was performed.
