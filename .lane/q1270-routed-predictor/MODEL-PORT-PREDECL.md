# Q1270 native combined-model predeclaration

Date: 2026-08-23. Decision: `PREDECLARED / EMPTY IMPLEMENTATION / FRESH HOLDOUT LATER`.

## One falsifiable family

The sole family is `q1270_native_recurrence_v1`: a new finite-width classical
replay and conditional-phase composition built from empty target files and
derived only from Q1270 source `90770b1` plus this lane's already sealed Q1270
trace, checkpoint, schedule, and trusted masks.

The read-only replacement checklist is
`.lane/q1271-target0-predictor/Q1270_DONOR_DELTA.md` from commit
`f054ed03004979ac2b958b5e749b598a4641b998`, tree
`423507a8b98fbd1033ec7b5b4672b8716e8fec98`, file SHA-256
`b1f9c1ad3119a716a5bc638fa068ba23944abbcfc93affe5b294e6a7d1d0ff0a`.
It is a checklist, not an input artifact. No terminal donor source file,
operation stream, checkpoint, trace, schedule, constant table, model output,
fixture, mask, corpus, receipt, binary, extractor, generator, or runner may be
copied into this lane. The implementation files begin empty; every constant and
transition must cite and reproduce the exact Q1270 source or generated target
identity.

The implementation is killed if any required behavior cannot be derived from
Q1270 source without a donor artifact, if any complete mask differs, or if a
post-holdout edit would be required.

## Frozen target identities

- circuit source / tree:
  `90770b10664fc89065b1d05ac792370efed4c629` /
  `944593de97d412f8b4c7242f7d0aff98002c0d04`;
- full evaluator receipt:
  `953acb44fbcbb32ab097a52be31ae365db41bd92`;
- pushed inherited+H64 evidence commit / tree:
  `5d9e8ce6b4381c6c4d0fb3e2d48db6baf9a06b6e` /
  `51938efa0067a0a5cd6b8e2ed52b5d0928e813d9`;
- operations: `12,953,636`, SHA-256
  `ec4fadc0b5cd1c26ee5d81001b7a72692678b61a94c4091032dd93b8b62eb63a`;
- Q / bits / traced body / nonce tail:
  `1270 / 961,070 / 12,953,540 / 96`;
- compressed trace SHA-256:
  `069ae8682265a831a69bb7861e210fc58e62b7e76422bc66d0ed2f3a81ad4173`;
- raw trace SHA-256:
  `766a9b06009560333d3d2790001dfdda18e419123a9c3234732ee045373af36b`;
- checkpoint: `PPFSCKP1`, 5,064 bytes, SHA-256
  `75deeae0d80122a3ce30a7337b34128af5dc964bc26ba0b77c2d6599abdb937f`;
- R/Hmr words: `1,947,720`;
- conditional-phase families: `3267/694/694/3`, source lines
  `1585/1854/2031/1501`, total `4,658`;
- phase metadata / generated schedule SHA-256:
  `fba2270e4c4fed53db5625612c72b930dc821bb8c54c4ed43df5855f845bca0b` /
  `17720a6855002f12f0b90ce8598139bfa4f5d2ec0e1ed72d6579177da9a43d35`;
- trusted oracle source / deterministic binary SHA-256:
  `4059969b3cca026a637e7fc735acc8c214d23a5172344d25463dff0ecf128b60` /
  `de84cf864bd80b7acf934259fa5435e4103d9b387167456091d85ca34ce9acfd`;
- inherited row / H64 results / H64 manifest SHA-256:
  `a2515e8989d873b721c59e9c58354f6b61d9754d0fb3291dd046ff9b6cc8f004` /
  `da0ca6fed7a3e45433a1d997a0d6f0116d92748731256666731a4cdaa34e3a6e` /
  `07e4a19246681192735dcf4a68ca2c4095eb7caa7e746ce0336a0891436ba20a`.

The target circuit controls are exactly selector eviction, doubled-out
eviction, target0/sign alias, sign-XOR/add-out routed checkpoint, divide peak
1270, multiply peak 1271, square ladder 240, and the selected nonce. No other
`SUB4_*` control exists.

## Required Q1270-native derivations

Before a model output, source audit and executable probes must independently
derive and seal:

1. exact divide and multiply round counts and endpoint/round-zero behavior;
2. the 700-entry sampled width table, its Q1270 round mapping, monotonicity,
   active widths, repair-disabled state, and fold widths;
3. separate divide/multiply replay peaks `1270/1271`, chunk boundaries,
   compare width/order, and square ladder `240`;
4. routed, doubled-out, target0, sign, and add-out value lifecycles, proving the
   sign-XOR route is value-neutral to the classical recurrence;
5. a new host-state digest from the exact `PPFSCKP1` representation, never
   inferred from a donor digest;
6. a byte-exact 4,096-byte inherited Fiat-Shamir checkpoint selfcheck;
7. exactly 4,658 target-schedule phase emissions on every classically clean
   shot and target source bindings only.

The three new implementation surfaces are `src/q1270_pp_model.h`,
`src/q1270_pp_host.h`, and `src/q1270_ppcpu.cpp`. Their first committed content
must be target-native. A source-bound derivation receipt must name every
constant, originating Q1270 function/line, probe output, and hash. Generated
operations, trace, checkpoint, schedule, masks, binaries, and logs remain
outside Git.

## Qualification order and kill gates

1. Commit and push this predeclaration before creating any model file.
2. Re-run the Q1270 extractor/generator and checkpoint selfchecks; require all
   frozen hashes byte-for-byte.
3. Implement the recurrence, host, and phase composition from the target
   derivation. Build twice from independent paths and require byte-identical
   binaries plus fixed SHAKE256 empty/`abc` vectors.
4. Require exact inherited equality for all 141 classical words and all 141
   clean-phase words, exact geometry, and ancilla zero. Any differing bit kills
   the family.
5. Without an edit, require exact ordered equality on the same complete masks
   for all 64 H64 rows, zero FN/FP, exact identities, and ancilla zero. Any
   mismatch kills the family; count-only agreement is not evidence.
6. Commit and push the model/H64 seal before creating a fresh holdout.
7. Only then generate and freeze a new private independent `F16` corpus outside
   Git, mode 0600, disjoint from inherited, H64, the unopened D32, and all prior
   Q1271/Q1272 corpora. Seal its list/seed hashes without printing values.
8. Open F16 first to the frozen model and seal all predicted complete masks.
   Only afterward reveal F16 once to the unchanged trusted oracle and compare
   complete masks. No post-reveal edit is permitted.

The existing private D32 remains unopened throughout this family. This lane
has no provider, CUDA, scan, range, hunt, fleet, submission, public-note, or
external-action authority.
