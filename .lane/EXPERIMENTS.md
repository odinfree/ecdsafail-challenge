# E-004 boundary audit experiments

| id | source/flags | result | disposition |
|---|---|---|---|
| A0 | commit `4e33a0c`, protected defaults | 12,901,167 ops, SHA `ecc3d9f0...` | reproduced |
| A1 | E-001c held flags | 12,939,336 ops, SHA `d4ecab6d...`, Q1272/T916117.12, `0/0/0` | reproduced |
| A2 | A1 + `TLM_FINAL_Y_SUB_BOUNDARY_CARRY=1` | 12,943,345 ops, SHA `4618d4af...`, Q1272/T918043.41, `0/0/0` | composition fits |
| A3 | `TLM_FINAL_Y_SUB_BOUNDARY_SELFTEST=1` | 13/13 exact, phase 0, ancilla 0, emitted T1984, Q307 | pass |
| A4 | A2 unchanged full 9024-shot evaluator | exact T918104.700, `11/12/0`, first mismatch 2582 | held; no hunt/submit |

Next falsifier: the pinned two-lane E-004 gate at nonce `444000000032`, shots
7997 and 7996, as specified in `E004-BOUNDARY-AUDIT.md`.
