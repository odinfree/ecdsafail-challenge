# Promoted Q1272 W64 pre-evaluator prediction seal

Date: 2026-08-23

Verdict: `RUST_CPP_64_OF_64_EQUAL / EVALUATOR_UNOPENED`.

The holdout was frozen and pushed at `da99ccb` before either prediction. The
corrected Rust predictor ran first. The repaired shared C++ predictor ran
second. No trusted evaluator directory or row existed before both outputs were
sealed.

- corpus SHA-256:
  `db43f935ec97561cdab7f1e0c86d11ea439f9b75f0da815a7a92b999bc5575a0`;
- rows: 64;
- predicted classical faults: 1,138;
- Rust complete-mask output SHA-256:
  `0e395369f6b6e8d560e3693316f5dc59d93e0e009d5b7b559e712f62720b276d`;
- repaired C++ complete-mask output SHA-256:
  `0e395369f6b6e8d560e3693316f5dc59d93e0e009d5b7b559e712f62720b276d`;
- Rust seal SHA-256:
  `8f9e1a4b7664b01a3d470212165489c8e6a2598aa93f24ac7c2935ce81f077f0`;
- C++ seal SHA-256:
  `5747b09724ebc57fb8fd6037e6920df768ac3163c9700fc441ae920ff7742ace`;
- C++ stderr SHA-256:
  `8561cb0ddfe86d00cee016e7a95d8c8701b439326da6996026a5f53cab575cc3`.

Both outputs contain one row per sorted nonce, a self-consistent fault count,
and the complete 141-word mask covering all 9,024 shots. Byte equality proves
all 64 complete predicted masks agree; it does not yet consume or claim the
trusted result.

The immutable next action is trusted W64 reveal with the unchanged evaluator.
Any row mismatch permanently fails this gate. CUDA, provider compute, ranges,
hunting, and submission remain disabled.
