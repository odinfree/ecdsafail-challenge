# Promoted Q1272 post-repair W64 trusted gate

Date: 2026-08-23

Verdict: `W64_RUST_CPP_TRUSTED_64_OF_64_PASS / LOCAL_CPP_GO`.

W64 was frozen and pushed at `da99ccb` after the wrapped-state C++ repair and
before either model prediction.  Corrected Rust ran first, repaired C++ ran
second, and both complete-mask outputs were sealed and pushed at `57c3df7`
before the unchanged trusted evaluator directory existed.  The trusted reveal
then processed all 64 nonces over all 9,024 shots.

## Frozen identities

- structural source:
  `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- exact operation count: `12,904,643`;
- exact operation SHA-256:
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- checkpoint/tail state digest: `e9b2d20ecd1169a8`;
- corrected Rust source SHA-256:
  `39371fca9e77d7aab3cfda7111bdbc03c11d8cfc03966cd15b2ea77d79836e38`;
- repaired shared C++ model SHA-256:
  `d417865bcc119686dc2d9a3d45ca8e801332cf824c8ed95aefb5e0195f1318b2`;
- C++ host SHA-256:
  `b635c95deb5bab2b89ea65de4dafdba22ea4184a647c82d4bb5680450f976435`;
- C++ driver SHA-256:
  `37550fe3d8d1f1130cdc03a746ed5b4ea6bdb619475eebcddaeb087342457352`;
- W64 corpus SHA-256:
  `db43f935ec97561cdab7f1e0c86d11ea439f9b75f0da815a7a92b999bc5575a0`.

## Trusted reveal

- complete classical masks equal: Rust = C++ = trusted evaluator on `64/64`;
- predicted/trusted classical faults: `1,138/1,138`;
- qubits: `Q1272` on every row;
- tested shots: `9,024` on every row;
- ancilla-garbage batches: zero on every row;
- diagnostic raw phase-garbage batches: `856` aggregate;
- Rust/C++ complete-mask output SHA-256:
  `0e395369f6b6e8d560e3693316f5dc59d93e0e009d5b7b559e712f62720b276d`;
- trusted summary SHA-256:
  `80eb7ad77b4bd922b6faa3f016f8d3d294fa51dd1fe88a4eb1da6e44780c713e`;
- raw-artifact manifest SHA-256:
  `213221a677f0c92e6673763b842c1f1c84d736388146306fbf40589df6471e48`;
- completion receipt SHA-256:
  `185011dacf1e25bdb7fe42dc9462e44e765c5d8a96cddd9835a3292966d63734`.

A fresh local C++ rebuild repeated W64 twice.  Both complete-mask files were
byte-identical to each other and to the sealed Rust/C++ output above.  Both
stderr files were also byte-identical, SHA-256
`8561cb0ddfe86d00cee016e7a95d8c8701b439326da6996026a5f53cab575cc3`.

This closes the genuinely new post-repair holdout.  It is a local classical
model qualification only.  Conditional phase, CUDA, provider compute, scan
ranges, hunting, and submission are outside this gate.
