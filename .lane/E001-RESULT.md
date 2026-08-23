# E001 terminal receipt

- source commit: `73422709ed70ba9725b3cb592770bcf197df4cdb`
- source tree: `fe77bddfb49b426312b1cca3d009b150cd06fd89`
- exact environment: `SUB4_PP_FOLD_SELECTOR_EVICT=1`,
  `SUB4_PP_PEAK=1272`, `SUB4_SQUARE_LADDER=242`; every other `SUB4_*` unset
- build binary SHA-256:
  `1330fa45385cffbacae379943e1c939d429b3774f8d9ed5cd5b9d0d3c4105544`
- unchanged evaluator SHA-256:
  `afd84890818db97a93aaf94905e700058d6c963289f5bbd057a35352d53065a7`
- operation count: `12,904,643`
- artifact SHA-256:
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`
- artifact compressed bytes: `50,846,670`
- qubits / bits / shots: `1272 / 957,916 / 9,024`
- average executed Toffoli: `914783.521`
- average executed Clifford: `10708681.049`
- rounded T / rounded score: `914784 / 1,163,605,248`
- live SOTA commit / score at predeclaration:
  `4eb93cb33bbf6a93229fe166b8d511c5e52ee253 / 1,163,831,339`
- strict score margin: `226,091`
- classical / phase / ancilla: `23 / 8 / 0`
- first mismatch: shot 292, classical
- evaluator-row SHA-256:
  `8723d525d7a4502c921c374d0e675bcca786d58c3b80b85f9de06ea29f036d86`
- independent evaluator-row SHA-256 values (same Q/T/op count, `23/8/0`, and
  first mismatch):
  `ec5574ae0dea4739b5189c80532b0a6a28622cbda7b8ecc1e58bc783b39ef1f6`,
  `b403c8982fab24b84af564f03fe382fdb279ac72dbac3ad579e8e8ace73f614e`

Decision: `SCORE_GO / VALIDATION_DIRTY / NO HUNT`.  The product gate passes;
the correctness gate does not.  Exact source-bound predictor qualification is
required before any search work, and no provider/range/hunt/submission action
is authorized here.
