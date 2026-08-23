# Promoted-source Q1272 predictor state

- decision: `INHERITED_CLASSICAL_PASS / H64_PASS / D32_FAIL / REPAIR_REQUIRED / HOLD_CUDA / HOLD_RANGE`
- target: `73422709` / tree `fe77bddf...` / ops `ea19759d...`
- evidence: `41dd0b45` / exact diagnostic `23/8/0`
- predictor source SHA-256: `2d016070a93a5966c5a163a6242b27ef8264176c76c72448ba50027b70465890`
- inherited classical index SHA-256: `c46041ff454200ba4d2ab3cffcefb2b118e4afd839f674431762b24da37f8848`
- inherited result: evaluator = predictor = 23, first shot 292, complete set equal
- shared CPU model: exact 23 fault masks; 18 first-width deficits / 5 hard
- shared checkpoint/tail digest: `e9b2d20ecd1169a8`
- causal fixture SHA-256: `ab647dc2345fade447d47547037962e399d66142e57519563769cfe3a93d8fcb`
- H64 result: 64/64 complete masks, 1,144/1,144 faults
- H64 summary SHA-256: `88cf50daa6a90f3bbf5404fb9df01924a39e7688d8ce596ad62bff9b58f38821`
- D32 result: 31/32 complete masks; nonce `66961008849867` undercounts
  26/27 with evaluator-only shot `8729`
- D32 reveal SHA-256: `e2754ae5090b52ff6318920b9385579690213f5712bdf5ce1bed696bedc54c83`
- scan mode: disabled and negative-tested
- phase: independently owned by the combined-phase lane; no phase claim here
- provider/range/hunt/submission: none
- next action: seal the D32 failure, isolate shot 8729's first missing event,
  predeclare the smallest causal repair, and rerun inherited + H64 + D32 before
  freezing a new disjoint holdout
