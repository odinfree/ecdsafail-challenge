# Promoted Q1272 D32 classical reveal

Date: 2026-08-23

Verdict: `D32_CLASSICAL_FAIL / 31_OF_32_COMPLETE_MASKS / MODEL_REPAIR_REQUIRED`.

The D32 corpus was generated deterministically, frozen, committed, and pushed
at `ad6d34f` (tree `7063752804a69188ae8978339c13264e53f87794`)
before predictor or evaluator reveal. Corpus SHA-256 is
`45838602350ecabd4c95d900602d440692e57bffd2581160e1f151ccdb4cc79c`.
It is disjoint from H64 and the inherited diagnostic nonce.

The generalized source-bound harness was pushed at `673b393` (tree
`da63e984625404d47ab62054cad51d6d5b4dbdc9`) before use; harness SHA-256 is
`fa5934706265eca952cb3232c49e258ec9964fd71ac2b52a8aa134e7ea55609f`.
The prediction was sealed while the evaluator directory did not exist:

- prediction SHA-256:
  `a27293818356b76ceea9afd4bc307f5082364832e70725cb9117eb5cd8c98a9a`;
- prediction-seal SHA-256:
  `b5d945beba283d30eed1a48691370d5fe6c952d011c8bc9d469c1fbdc0b7f2cc`.

The trusted reveal completed all 32 local evaluations. Every row reported
Q1272, 9,024 shots, and zero ancilla-garbage batches. Thirty-one complete
classical masks were byte-exact. One row failed:

- nonce: `66961008849867`;
- predictor/trusted classical counts: 26/27;
- evaluator-only shot: `8729`;
- predictor-only shots: none;
- prediction index-list SHA-256:
  `b82d942106bbb3706a02f93bd0bbc0876f1db2d7f7c3b0806f8be95171eac9bb`;
- trusted index-list SHA-256:
  `a42304be3f660e6b970024eadef0720b1d0af09f52e343a279a49fd0568370cb`;
- exact operation-stream SHA-256:
  `37a3f16cdb9f5d22c7e380019e60c18aa3a820034db920c24e8e6555c91681ca`;
- trusted evaluator stdout SHA-256:
  `36fb56255197b6661371d59fe6dc551001a2845b01e69e780d7ad241fe619e9f`.

Across D32, the predictor reported 558 faults and the trusted evaluator 559.
The trusted raw diagnostic phase total was 383 and the ancilla total was zero.
The committed normalized 32-row reveal is `D32_REVEAL.tsv`, SHA-256
`e2754ae5090b52ff6318920b9385579690213f5712bdf5ce1bed696bedc54c83`.
Raw artifacts remain outside Git under
`/Users/olifreuler/ecdsa-ops/q1272-promoted-predictor-73422709-d32`.

D32 is now revealed and cannot be reused as a fresh holdout. The current model
is not qualified for CUDA or range scanning. The next admissible action is a
predeclared, minimal causal repair for shot 8729, followed by exact reruns of
the inherited nonce, H64, and D32 and then a new disjoint sealed holdout.
Provider compute, ranges, hunting, and submissions remain disabled.
