# E007 Q1272 predictor preparation

This packet is bound to circuit source
`ea93a131e2bc488bff6fa12010d1f3606c7771b0` and its inherited-nonce
operation stream:

- operations: `12,943,345`;
- SHA-256: `4618d4af86c23c06cc72fef26f8a8e5986c7a9de5f804891541a8ce6eb189f37`;
- prefix/tail state digest: `963a662d2e392804`;
- divide/multiply rounds: `696/696`;
- width index: `floor(round * 703 / 695)` for both traversals;
- replay fold: low 55 bits;
- final-y correction: post-low53 threshold plus full high203 decrement.

The shared CPU/CUDA model source is not authorized for scanning. Local CPU
calibration matches the unchanged full evaluator's classical total and first
failure on all four frozen nonces. The inherited nonce also matches the exact
complete 11-shot mismatch set. CUDA comb8/comb16 parity is still open.

Before any GPU fixture run, require the full operation SHA above, the model
source hashes recorded in `../PREFILTER-PREP.md`, and the loader's count and
state-digest checks. Then require byte-identical `breakdown` output from CPU,
CUDA comb8, and CUDA comb16 for every row of `fixtures.tsv`. No model output is
a circuit result; every retained nonce still needs unchanged full 9,024-shot
evaluation with classical, phase, and ancilla all zero.

`build.sh` writes binaries beside this file, so run it only in a disposable
copy or remove the binaries afterward. Set `PPGPU_CUDA_ARCH=120` on Blackwell;
the only other admitted architecture is 89.
