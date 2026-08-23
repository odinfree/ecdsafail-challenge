# Promoted Q1272 H64 classical qualification

Date: 2026-08-23

Verdict: `H64_CLASSICAL_PASS / 64_OF_64_COMPLETE_MASKS / CUDA_HOLD`.

The H64 corpus was frozen and pushed at commit
`bdbce2c` (tree `6b3a54b836604a8f0dbafa72515990bc99d3ebbc`) before
prediction or trusted evaluation. Its 64 nonces are the closed interval
`444000000000..444000000063`; corpus SHA-256 is
`17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9`.

The exact Rust predictor was run first and sealed before any evaluator row was
opened. Prediction SHA-256 is
`6147c21129876a2193cd5813944b95d09ae1f149802c53ca731824a11be54adc`;
prediction-seal SHA-256 is
`d45626bf32eb990c98c6e3dc3528c214359068597fa4e3c28663dcd983e78e28`.
The qualification harness used for this run has SHA-256
`c12cb6140ccc06058a7d12ff118210c3e7d75edbe1f8a059e19fef689f388a36`.

Four isolated local workers rebuilt the exact source-bound operation stream for
each nonce and ran the unchanged trusted evaluator over all 9,024 shots. The
result is exact equality of every 9,024-bit classical mask:

- rows: 64/64 pass;
- predicted/trusted classical faults: 1,144/1,144;
- qubits: Q1272 on every row;
- tested shots: 9,024 on every row;
- ancilla-garbage batches: zero on every row;
- diagnostic raw phase-garbage batches: 797 aggregate;
- normalized summary SHA-256:
  `88cf50daa6a90f3bbf5404fb9df01924a39e7688d8ce596ad62bff9b58f38821`;
- raw-artifact manifest SHA-256:
  `cdd76c942c410c938338ae6851c6e3d39b987a0b7d38ae8ed426cc55d541f2f1`;
- completion receipt SHA-256:
  `b2d21e86ae6bd8b68a4700980442bce8a24ec52796ca5f428b770ae28453a5b1`.

Raw operation streams, evaluator logs, binaries, and generated artifacts remain
outside Git under
`/Users/olifreuler/ecdsa-ops/q1272-promoted-predictor-73422709-h64`.
This gate qualifies the exact Rust classical model on H64 only. It makes no
CUDA, conditional-phase, scan-range, provider, hunt, or submission claim.
