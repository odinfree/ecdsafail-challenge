# Lane state

## E002 fixed-nonce width repair

- branch: `research/q1272-fixed-nonce-width-repair`
- base: evidence `41dd0b4508527081b8d24255adf0579389f02453`, structural
  `73422709ed70ba9725b3cb592770bcf197df4cdb`
- status: `TERMINAL KILL / 18 SOFT + 5 HARD / SOURCE UNCHANGED`
- target: the exact inherited 23 classical failures at nonce `65700024945645`
- sole family: sparse causal `+1` adjustments to sampled `WIDTH_SCHEDULE`
  indices
- hard-fault gate: fired on shots `292, 3094, 4897, 6692, 7956`
- score gate: Q1272 and rounded T at most `914961` (`+177` over inherited
  rounded T914784)
- exact predictor gate: PASS complete inherited set `23/23`, canonical set SHA
  `c46041ff454200ba4d2ab3cffcefb2b118e4afd839f674431762b24da37f8848`
- causal gate: 18 first post-add excess-one width deficits plus five non-width
  hard failures; independent diagnostic stdout SHA
  `b35613a083650e3d9c21c7993a778c338e67dd55c1fad0a95dad1a718ba3c1fd`
- minimum-set verdict: infeasible in the sole sparse `+1` family
- circuit source edit / chained cover / candidate price / full evaluator: none;
  stopped at the predeclared hard-fault gate
- next action: none in this family
- provider/range/hunt/submission/public note: forbidden

## E001 inherited selector saddle

- branch: `research/q1272-promoted-selector-rebase`
- base: `4eb93cb33bbf6a93229fe166b8d511c5e52ee253`
- decision: `SCORE_GO / VALIDATION_DIRTY / NO HUNT`
- structural commit / tree:
  `73422709ed70ba9725b3cb592770bcf197df4cdb` /
  `fe77bddfb49b426312b1cca3d009b150cd06fd89`
- semantic edit: exact hash-bound transplant of donor `14608572` selector
  lifecycle plus focused miter only
- target `pingpong_div.rs` / `mod.rs` SHA-256:
  `6e7cce578663d8419c032190a9caa405ca0d84e0512104b766b9c68540f01994` /
  `0c9e9a920d9078f2390028009895f03d495096fdac9d2b596c7913c064e03e63`
- focused miter: PASS 64/64, phase 0, ancilla 0, all eight arms,
  identical Toffoli, `+4 CX +1 R`, peak `573 -> 572`
- square component: PASS, Q1272
- ping-pong component: PASS, Q1272
- candidate artifact: 12,904,643 ops, SHA-256
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`
- unchanged full 9,024-shot evaluation: Q1272, T914783.521 (rounded
  914784), classical/phase/ancilla `23/8/0`
- projected rounded score: `1,163,605,248`, a strict improvement of
  `226,091` over the measured live score `1,163,831,339`
- Q1272 rounded-T ceiling: `914961`
- next gate: fresh source-bound classical and conditional-phase predictor
  qualification before any search; this lane does not hunt
- provider/range/hunt/submission: forbidden
