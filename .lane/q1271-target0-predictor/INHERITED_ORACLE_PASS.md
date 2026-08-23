# Q1271 target0/sign-alias inherited oracle seal

Verdict: `PASS_EXACT_TRUSTED_ORACLE / MODEL_UNRUN / H64_NEXT`.

This seal was produced after predeclaration and after the byte-exact target
rebuild. No predictor source existed and no predictor output was opened.

## Immutable stream and trace

- source/evidence commit / tree: `a22090374a957d29a3331d6c876ad12ff45fea31` /
  `018eb52de8ab3e6337864338683821c0cbb574a2c`;
- operations: `12,919,161`, SHA-256
  `590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa`;
- op-site rows: `12,919,065` body rows plus the known 96-X nonce tail;
- op-site TSV SHA-256:
  `56e084c152701707310c6822f7b914652a5d17d2352efd2255fd513492a0b4ce`;
- trace build source `build_circuit.rs` / `mod.rs` SHA-256:
  `3b3852e6ab887852f47af44e205196a43473b8e28fe62bc2c51d2213b37a8b9e` /
  `0f2cad91de35568c15a561449d4e0c2c53b84673afd329d6d5591b91096dd202`;
- complete trace instrumentation diff SHA-256:
  `9aa8dbe6b58094b3f009b8c6e37de7656353c9a84dab2f15871fded103de9c87`.

The detached trace build added only caller attribution to `R`/`Hmr` and an
output-only TSV dump. Its generated `ops.bin` reproduced the frozen target SHA
byte-for-byte. Therefore no instrumented semantic stream was admitted.

## Trusted two-pass oracle

- oracle source / binary SHA-256:
  `26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98` /
  `90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402`;
- nonce: `65700024945645`;
- geometry: Q `1271`, shots `9024`, ancilla failures `0`;
- unchanged full-channel totals: classical `11`, raw phase `10`, ancilla `0`;
- classical mask, complete sorted set:
  `{384,497,1093,1129,2209,2726,2798,2835,5494,6721,7427}`;
- conditional phase mask `raw_phase & ~classical`, complete sorted set:
  `{2854,5626,8398,8828}`.

The four conditional events are four distinct measured-uncompute divergence
sites, all attributed to the source-bound fused add carry at
`pingpong_div.rs:1577`; no bare-R or deterministic residual was present.

External artifacts remain outside Git at
`/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d/inherited`:

- attribution SHA-256:
  `b9137fbf0deae69e41d492e86de0ec76abb7bf4ec6f5dd98171b3db2675c34e4`;
- oracle stdout SHA-256:
  `e2d7e71267b9ea107ec01d93b452fb618e77ceef076ca6c7fa47986d70cf3847`;
- timing stderr SHA-256:
  `3bf793469c900856e5d9a749640f323d50c1f729d2b61d76d929780757b6e35a`.

Runtime was `30.49 s` wall on this host. This is evidence only; it is not a
provider, range, CUDA, or hunt result.

## Next gate

Run and seal the same trusted oracle on the already-frozen H64 before any
model output. D32 remains unopened to predictor output and is forbidden until
the combined model is exact on inherited plus all 64 H64 rows.
