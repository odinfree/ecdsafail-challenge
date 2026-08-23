# Promoted Q1272 V64 pre-evaluator predictor disagreement

Date: 2026-08-23

Verdict: `V64_PREDICTOR_DISAGREEMENT / EVALUATOR_UNOPENED / HOLD_ALL`.

V64 was frozen and pushed at `805fcfd` before either prediction. The corrected
Rust prediction was sealed first, with SHA-256
`c3f5bf182ab37716e9dfaa03174de35ce703099ceb2c845a2c9e720b840ad862`.
The unchanged shared model was then compiled behind the source-bound batch
host at `a0d92e9` and run over the same corpus before creating any evaluator
directory. Its complete 64-row output has SHA-256
`96763fd5332145466d91c552a707d41e5e33760a2cb04990f88ac30a304dfecb`;
stderr SHA-256 is
`8561cb0ddfe86d00cee016e7a95d8c8701b439326da6996026a5f53cab575cc3`.

The complete masks differ on exactly one row:

- nonce: `90522024612912`;
- corrected Rust count: 18;
- shared C++ count: 17;
- Rust-only shot: `2544`;
- C++-only shots: none.

No trusted V64 evaluator row had been opened when this disagreement was found.
Under `V64_PREDECL.md`, the cross-model gate has failed permanently; V64 cannot
be relabeled as a fresh terminal holdout even if one predictor is repaired.
Its sealed predictions may now be revealed to the unchanged trusted evaluator
to adjudicate the row and provide causal evidence.

CUDA, provider compute, scan ranges, hunting, and submissions remain disabled.
