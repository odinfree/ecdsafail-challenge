# Lane state

- branch: `research/q1272-live-phase-screen`
- base: `41dd0b4508527081b8d24255adf0579389f02453`
- target source: `73422709ed70ba9725b3cb592770bcf197df4cdb`
- target ops: `12,904,643` /
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`
- decision: `PASS_D32 32/32 / CPU COMBINED EXACT / NEGATIVES NEXT`
- exact ops: reproduced `12,904,643` / `ea19759d...`
- predictor checkpoint: `e9b2d20ecd1169a8`
- regenerated phase geometry: `3,964` sites / `1,938,616` R/Hmr words,
  families `2573/694/694/3`
- inherited trusted/model complete sets: classical `23/23`, conditional phase
  `1/1` at shot `3290`, ancilla `0`
- H64 trusted/model complete sets: exact `64/64`; aggregate
  classical/raw-phase/conditional-phase `1144/844/293`; ancilla `0`; compact
  results SHA-256 `0b05b359...`
- D32 trusted/model complete sets: exact `32/32`; aggregate
  classical/raw-phase/conditional-phase `550/407/138`; ancilla `0`; compact
  results SHA-256 `462cc7c4...`; deterministic repeats SHA-256 `0569a821...`
- post-reveal source edits: none
- next gate: fixed fail-closed input/state/command negative matrix against the
  unchanged model, then exact-source CUDA handoff if it passes
- provider/range/hunt/fleet/submission/public-note: forbidden
