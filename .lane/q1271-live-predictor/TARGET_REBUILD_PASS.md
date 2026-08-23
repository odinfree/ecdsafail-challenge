# Q1271 target rebuild receipt

Verdict: `PASS_BYTE_EXACT / TRUSTED_FULL_REPRODUCED / MODEL_UNRUN`.

After the predeclaration was pushed, the exact structural source was built
under a minimal environment containing only the three frozen Q1271 controls
and calibration nonce `65700024945647`.

## Identities

- predeclaration commit: `aab0f49fa09f46b04b6a04f230380ba6affb3472`;
- structural source / tree:
  `b69c17e16e0b9140d14f15c7d87314352ecaf7be` /
  `8749e54dd9c3d801cd79edb5ff22b43c87fac0b9`;
- build command:
  `cargo build --release --locked --offline --bin build_circuit --bin eval_circuit`;
- rebuilt `build_circuit` SHA-256:
  `9e41896f19deecaf3f84ee0c9a7a5cb95ef4aaa3b572c857eaf0b5e0b1b1c985`;
- rebuilt unchanged `eval_circuit` SHA-256:
  `e2a1a9d860effe681ec206688d93d0b28653fe1cc812913ac8515ffcd2e7cfc3`.

## Exact artifact

- operation magic: `QECCOPSZ`;
- declared/emitted operations: `12,926,780 / 12,926,780`;
- compressed bytes: `50,733,211`;
- uncompressed bytes: `723,899,696`;
- operation SHA-256:
  `a13de41544a81672b07674acabecec0bb054201b8d1634ed79745bbc4be2f23e`.

This is byte-identical to the terminal frozen-eight winning stream.

## Unchanged full evaluator

The unchanged evaluator consumed the rebuilt artifact once and reproduced:

- Q / shots: `1271 / 9024`;
- exact average T / rounded T: `915675.850 / 915676`;
- emitted-operation receipt: `12,926,780`;
- classical / phase / ancilla: `13 / 17 / 0`;
- phase mask first reported by the evaluator:
  `0x0000000000000004`;
- appended result-ledger SHA-256 before byte-exact restoration:
  `5d90344dcb197c5ce3e8dd353bdd4c120b5b6da7e04d45c94d3c834473153a46`;
- restored tracked result-ledger SHA-256:
  `eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

The expected nonzero evaluator exit is the frozen dirty-channel result, not an
abort.  The artifact remains external/ignored.  No predictor output was
generated before this receipt.

## Next gate

Derive a source-bound operation trace, phase-site schedule, and two-pass
trusted oracle from this exact source.  Seal inherited-eight and H64 trusted
masks before importing or running the predictor.
