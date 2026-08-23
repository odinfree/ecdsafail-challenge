# Q1270 routed source-bound phase geometry

Date: 2026-08-23. Verdict:
`PASS_SOURCE_TRACE / PASS_CHECKPOINT / TRUSTED ORACLE NEXT / MODEL UNOPENED`.

The exact Q1270 stream was rebuilt with temporary caller tracking on R and Hmr
emission. The instrumentation changed only Rust caller metadata, not emitted
operations. It was removed immediately after trace generation, and the circuit
source, operation artifact, and tracked result ledger returned to their sealed
hashes.

The first diagnostic invocation omitted the required `TRACE_OP_SITES=1` guard
and failed closed before writing a trace. Its 13-byte empty zstd frame was
overwritten. The accepted invocation set the guard, satisfied the exact
operation/site-length assertion, and is the only trace used below.

## Trace binding

- trace-harness commit: `279f425`;
- trace-builder source / binary SHA-256:
  `358d34cdb5e8b3d520551de1978eafbafc095bd649bd6c3fb96e834a948b3d74` /
  `e23b0df47efa3c672e3cb7a7d99501a14fef85f4bbc2f9154616257127981c6a`;
- exact operation count / SHA-256:
  `12,953,636` /
  `ec4fadc0b5cd1c26ee5d81001b7a72692678b61a94c4091032dd93b8b62eb63a`;
- traced source-site rows: `12,953,540`;
- exact untraced nonce-tail rows: `96`;
- R/Hmr ordinals: `1,947,720`;
- raw operation-site trace SHA-256:
  `766a9b06009560333d3d2790001dfdda18e419123a9c3234732ee045373af36b`;
- compressed trace bytes / SHA-256:
  `20,433,808` /
  `069ae8682265a831a69bb7861e210fc58e62b7e76422bc66d0ed2f3a81ad4173`.

The 602 MiB raw stream was compressed in flight because the volume had less
than 1 GiB free. The fail-closed extractor independently decompressed it,
verified every contiguous row and ordinal, and reproduced the raw digest.

Post-trace identities:

- `src/point_add/mod.rs`:
  `3fbe6baa8bb4638217f7416b858f4ddd57906fdaaecc500d860f1ca96f1ed60f`;
- `src/point_add/pingpong_div.rs`:
  `9b1e5e8540a01584e1238c27328481ba67db3b167aa199db4113e846f1eb6295`;
- `ops.bin`:
  `ec4fadc0b5cd1c26ee5d81001b7a72692678b61a94c4091032dd93b8b62eb63a`;
- `results.tsv`:
  `eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

## Conditional-phase sites

The current source contains `4,658` qualified conditional-phase predicates:

- `3,267` replay chunk carries at `pingpong_div.rs:1585`;
- `694` divide replay flags at `pingpong_div.rs:1854`;
- `694` multiply replay flags at `pingpong_div.rs:2031`;
- `3` arithmetic-shell carries at
  `trailmix_ludicrous/arith.rs:1501`.

The routed-control checkpoint and its inherited selector/doubled-out/target0
loans add only CX/reset lifecycle operations and no new R/Hmr family. The
lower replay and square geometry changes the chunk-family population, which is
why every ordinal was derived anew instead of transferred from Q1271/Q1272.

## Fiat-Shamir checkpoint

The source-bound checkpoint builder contains no predictor. It absorbs the
exact nonce-independent 12,953,540-operation prefix, stores the 96-record tail
template, and writes the `PPFSCKP1` format.

- checkpoint-builder source / binary SHA-256:
  `ca381383a0bc000d91b25e4c50df94e69f931beb689c561da427685fd72dc46d` /
  `eb90df24eef4cbb05fa1ff6a861b6f3a33e2ab86e715f763d1edf9a0475584b7`;
- checkpoint bytes / SHA-256:
  `5,064` /
  `75deeae0d80122a3ce30a7337b34128af5dc964bc26ba0b77c2d6599abdb937f`;
- encoded operation count / residual / tail records:
  `12,953,636 / 70 / 96`;
- selfcheck: first 4,096 XOF bytes for inherited nonce `65700024945645`
  matched the trusted full-stream SHAKE256 byte for byte.

## Frozen schedule artifacts

- compressed-trace extractor SHA-256:
  `ffc168d817e98508067abaac228cfb5f5c7a97d2efeca737071427c05358acd6`;
- schedule generator SHA-256:
  `b4a2f6be2d1dc36200167a6cb4a2854b1c16f70ea93bf3bf84fffcbdf707dd2c`;
- phase metadata / ledger SHA-256:
  `fba2270e4c4fed53db5625612c72b930dc821bb8c54c4ed43df5855f845bca0b`;
- generated schedule-header SHA-256:
  `17720a6855002f12f0b90ce8598139bfa4f5d2ec0e1ed72d6579177da9a43d35`;
- external artifact root:
  `/Users/olifreuler/ecdsa-ops/q1270-routed-combined-ec4fadc0/trace/`.

The compressed raw trace, checkpoint, phase ledger, generated header,
operation stream, and binaries remain outside Git.

## Next gate

Construct an output-only two-pass trusted oracle from the current unchanged
evaluator, then seal the inherited and all 64 H64 complete classical/raw-phase/
clean-phase masks. No donor predictor source, binary, table, checkpoint,
schedule, or output may be imported before that trusted-mask commit is pushed.
