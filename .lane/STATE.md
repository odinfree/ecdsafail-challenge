# Lane state

- branch: `research/q1272-promoted-selector-rebase`
- base: `4eb93cb33bbf6a93229fe166b8d511c5e52ee253`
- decision: `STRUCTURAL_PORT_SEALED / MEASUREMENT_PENDING`
- structural commit: pending this commit
- semantic edit: exact hash-bound transplant of donor `14608572` selector
  lifecycle plus focused miter only
- target `pingpong_div.rs` / `mod.rs` SHA-256:
  `6e7cce578663d8419c032190a9caa405ca0d84e0512104b766b9c68540f01994` /
  `0c9e9a920d9078f2390028009895f03d495096fdac9d2b596c7913c064e03e63`
- focused miter: PASS 64/64, phase 0, ancilla 0, all eight arms,
  identical Toffoli, `+4 CX +1 R`, peak `573 -> 572`
- square component: PASS, Q1272
- ping-pong component: PASS, Q1272
- Q1272 rounded-T ceiling: `914961`
- next gate: forced candidate rebuild and unchanged full 9,024-shot measurement;
  kill if Q differs from 1272 or rounded T exceeds 914961
- provider/range/hunt/submission: forbidden
