# Promoted Q1272 V64 trusted adjudication

Date: 2026-08-23

Verdict: `RUST_64_OF_64_PASS / SHARED_CPP_FALSE_NEGATIVE / CPP_REPAIR_REQUIRED`.

Both model outputs were sealed before trusted reveal, as recorded at `7805169`.
The unchanged trusted evaluator then processed every V64 nonce over all 9,024
shots. The corrected Rust predictor is exact on all 64 complete masks:

- rows: 64/64 pass;
- predicted/trusted classical faults: 1,131/1,131;
- qubits: Q1272 on every row;
- tested shots: 9,024 on every row;
- ancilla-garbage batches: zero on every row;
- diagnostic raw phase-garbage batches: 819 aggregate;
- Rust prediction SHA-256:
  `c3f5bf182ab37716e9dfaa03174de35ce703099ceb2c845a2c9e720b840ad862`;
- trusted summary SHA-256:
  `8f398581aaedfaa629ce15db4322e99dd463eed662fdab8c23063776553e6fea`;
- raw-artifact manifest SHA-256:
  `b8d686d389cd70d14efd49173a0a60ebc1e75024110dde6d594baee467e86335`;
- completion receipt SHA-256:
  `16529409312bee8cb7648d813772bc2f0192d61a8793216762d520628f547012`.

The trusted row for nonce `90522024612912` contains 18 classical faults and
includes shot `2544`, proving the shared C++ prediction's 17-count mask is a
false negative. That row reports Q1272, 9,024 shots, 16 raw phase-garbage
batches, and zero ancilla-garbage batches. Its trusted classical index-list
SHA-256 is
`2d3cbac8e89709289b7c0f168ba34a59dc8377559f089eabea16e788f485ef9b`.

The corrected Rust model is therefore retained unchanged. The shared C++
finite-width transducer must be repaired against shot 2544, then rerun over
inherited + H64 + D32 + V64. A new disjoint post-C++-repair holdout is still
required before CUDA GO. V64 is revealed evidence and cannot fill that role.

Raw trusted artifacts remain outside Git under
`/Users/olifreuler/ecdsa-ops/q1272-promoted-predictor-73422709-v64`.
CUDA, provider compute, scan ranges, hunting, and submissions remain disabled.
