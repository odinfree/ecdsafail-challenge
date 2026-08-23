# Q1271 source-bound phase geometry

Verdict: `PASS_SOURCE_TRACE / TRUSTED ORACLE NEXT / MODEL UNRUN`.

The exact Q1271 stream was rebuilt once with diagnostic caller tracking on R
and Hmr emission.  The instrumentation changed only Rust caller metadata, not
the operation stream.  It was removed immediately after trace generation, and
both target source files and the operation artifact returned to their sealed
hashes before extraction.

## Trace binding

- trace-harness commit: `1e6599f`;
- trace builder source / binary SHA-256:
  `575ad811842400a59b15abc12c50555f171321a8aaa91e6a54474c2c206cd7ef` /
  `d3127963682e2ae2378208ca8ab91a852e17c94ca574ce20bf25eb2641e74cfa`;
- operation count / SHA-256:
  `12,926,780` /
  `a13de41544a81672b07674acabecec0bb054201b8d1634ed79745bbc4be2f23e`;
- traced source-site rows: `12,926,684`;
- exact untraced nonce-tail rows: `96`;
- R/Hmr ordinals: `1,942,543`;
- operation-site trace SHA-256:
  `2b5001394244fa510ad1c947c7416e389ae22ef25f854676a47c73c45ecd4c7e`.

Post-trace source/artifact SHA-256:

- `point_add/mod.rs`:
  `c4aa38c73e79e3d5860616b31e3f507c888667390c857b319bb912dae1fd538d`;
- `pingpong_div.rs`:
  `0b95700c5c977e9128ce609840da5996928e873313195fcd44935b06ed7df15a`;
- `ops.bin`:
  `a13de41544a81672b07674acabecec0bb054201b8d1634ed79745bbc4be2f23e`.

## Conditional-phase sites

The current source contains 4,314 qualified phase predicates:

- `2,923` replay chunk carries at `pingpong_div.rs:1547`;
- `694` divide replay flags at `pingpong_div.rs:1783`;
- `694` multiply replay flags at `pingpong_div.rs:1927`;
- `3` arithmetic-shell carries at
  `trailmix_ludicrous/arith.rs:1501`.

The doubled-out loan/rematerialization adds four CX operations but no R/Hmr
site and therefore no new conditional-phase family.  The lower replay/square
geometry changes the chunk-family population and is captured by the newly
derived ordinals.

## Frozen generated artifacts

- extractor source SHA-256:
  `c368b7769941fcf9b203d557ba28889faa5f6e7484291b8d6a7780420bbf4651`;
- generator source SHA-256:
  `c853bf66050146bfc14708b18ced4209d207e64b83db60d8e06f7c996733f9f1`;
- phase metadata / ledger SHA-256:
  `2a2b1d5beb5560a4108e78c5cac03b878d684ef6a144bf10a1d1ae4581ae600c`;
- generated schedule-header SHA-256:
  `b3e073c55aaee18138ca8ffc6c751fcab2b59f8b8fd4c8d39cb211a60e35c23c`;
- external artifact root:
  `/Users/olifreuler/ecdsa-ops/q1271-live-combined-a13de415/`.

The 601 MiB raw trace, phase ledger, generated header, artifact, and binaries
remain outside Git.

## Next gate

Compile the two-pass trusted oracle against the current core simulator and
freeze all inherited-eight and H64 complete masks before any predictor output.
