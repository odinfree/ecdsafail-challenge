# Promoted-source Q1272 predictor state

- decision: `INHERITED_CLASSICAL_PASS / SHARED_CPU_EXACT / H64_RUNNING / HOLD_CUDA / HOLD_RANGE`
- target: `73422709` / tree `fe77bddf...` / ops `ea19759d...`
- evidence: `41dd0b45` / exact diagnostic `23/8/0`
- predictor source SHA-256: `2d016070a93a5966c5a163a6242b27ef8264176c76c72448ba50027b70465890`
- inherited classical index SHA-256: `c46041ff454200ba4d2ab3cffcefb2b118e4afd839f674431762b24da37f8848`
- inherited result: evaluator = predictor = 23, first shot 292, complete set equal
- shared CPU model: exact 23 fault masks; 18 first-width deficits / 5 hard
- shared checkpoint/tail digest: `e9b2d20ecd1169a8`
- causal fixture SHA-256: `ab647dc2345fade447d47547037962e399d66142e57519563769cfe3a93d8fcb`
- scan mode: disabled and negative-tested
- phase: independently owned by the combined-phase lane; no phase claim here
- provider/range/hunt/submission: none
- next action: seal this inherited checkpoint, then qualify the exact shared
  CPU/CUDA model against the predeclared H64 and disjoint holdout fixtures
