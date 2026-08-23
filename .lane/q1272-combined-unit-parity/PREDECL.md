# Q1272 combined local unit-parity predeclaration

Date: 2026-08-23

Status: `PREDECLARED / NO COMBINED MODEL OUTPUT / F32 SEALED`.

This lane builds a bounded local unit-test checker for one reversible-arithmetic
program.  It combines the already-qualified classical C++ classifier with the
already-qualified conditional-phase trace, then checks both complete output
masks against frozen local evaluator fixtures.  It does not authorize CUDA,
ranges, searching, providers, submissions, or external connections.

## Immutable inputs

- branch base / qualified classical commit:
  `f308df4f1ab054b204dec050bc8b9f452e7c49ee`, tree
  `3b4febba67aa3fc349576498582bf11416ba66c9`;
- conditional-phase donor commit:
  `83ad631e1a99db3db1c3886b4d61ff9ded94b0f5`, tree
  `e96c542e73c8b265eadfe3c4bbcb71df1096a024`;
- structural source: `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- operation count / SHA-256: `12,904,643` /
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- checkpoint/tail state digest: `e9b2d20ecd1169a8`;
- qualified classical model / host / driver SHA-256:
  `d417865bcc119686dc2d9a3d45ca8e801332cf824c8ed95aefb5e0195f1318b2`,
  `b635c95deb5bab2b89ea65de4dafdba22ea4184a647c82d4bb5680450f976435`,
  `37550fe3d8d1f1130cdc03a746ed5b4ea6bdb619475eebcddaeb087342457352`;
- phase donor model / host / driver SHA-256:
  `0d4c9a812892b9dac598cb59a8345c443b9e21663ac29743578f4e651b39b92a`,
  `aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2`,
  `dd05545d33911e7e0ab44b0e373f03a759ae8ee4b990f20f2cc40ca6ee2063af`;
- unchanged local mirror source / binary SHA-256:
  `26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98` /
  `90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402`;
- frozen operation-site trace SHA-256:
  `f2f0f99d096027299460d9a82c16d3714c9684564d10f13f6dcbbac2b3e92833`;
- generated phase metadata / header SHA-256:
  `59c177b5b43bf27eba1ee6758a7c1cea07f0eef5aa9b0c2a27dfe05301c6657d` /
  `de37d6004427082c345004d1225d0f877abfe9597ac969df228b77eb915fe42f`.

## Frozen corpora

- inherited singleton: `65700024945645`;
- H64 SHA-256:
  `17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9`;
- D32 SHA-256:
  `45838602350ecabd4c95d900602d440692e57bffd2581160e1f151ccdb4cc79c`;
- V64 SHA-256:
  `9db8b3a0fc0f277f8cea77cac181cc6133a667c96d5e73a97397a7116a6ec1bd`;
- fresh F32 SHA-256:
  `8d93cbf5e871f1ec8cab5768835c5c60a78a94fbc71611a96248a4248dc450ec`.

F32 is the ascending set produced before any combined-model or evaluator
output by taking the low 48 bits of
`SHA256("q1272-combined-unit-parity-fresh-f32-v1\\n" || u32be(i) ||
u32be(counter))`, for `i=0..31`, incrementing `counter` only on collision.
It contains 32 unique canonical decimal values below 2^48 and is disjoint from
the inherited singleton, H64, D32, V64, and the prior W64.

## Integration and fail-closed contract

The qualified classical files at the branch base remain an independent
comparator and are not replaced.  The exact phase donor history is imported as
the combined implementation.  A wrapper will:

1. verify every source, operation, phase schedule, evaluator, and corpus hash;
2. build the classical comparator and combined checker locally;
3. require both binaries to reconstruct state digest `e9b2d20ecd1169a8`;
4. require byte-complete classical output-mask equality between the branch-base
   comparator, combined implementation, and unchanged local evaluator;
5. require byte-complete conditional-phase output-mask equality between the
   combined implementation and unchanged local evaluator, using only
   `raw_phase & ~classical`;
6. require evaluator geometry Q1272 / 9,024 shots / ancilla 0 on every row;
7. reject duplicate, malformed, out-of-range, overlapping, drifted, missing,
   or unexpected corpus inputs and reject any unavailable oracle row rather
   than skipping it;
8. rerun deterministic controls after all corpora.

Complete means every one of the inherited, H64, D32, V64, and F32 rows is
exact in both claimed channels.  Count-only agreement, subset agreement,
silent skips, phase claims on classically dirty shots, or any post-reveal model
edit is terminal `KILL`.  Exact equality plus the negative and deterministic
controls is terminal `GO`, still local-only.

Generated operation streams, binaries, raw masks, logs, attribution tables,
and evaluator outputs remain outside Git.
