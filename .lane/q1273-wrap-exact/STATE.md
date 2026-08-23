# Q1273 wrapped-register repair state

- branch: `research/q1273-wrapped-register-exact`
- base: `41df51a37e0489b5e801faec9b3db588b2037c6a`
- decision: `GO_CPU_CLASSICAL / CUDA_HANDOFF_READY`
- scan/provider/hunt/submission: forbidden
- exact masks: inherited + H64 + D16 + blinded D32 = `113/113`, repeated
  byte-identically with `1,594/1,594` classical faults
- final summary SHA-256:
  `51d9802bee64c6865b294b1e3ac7f40d6717ce258677ea7b9bbfa4a5841a413d`
- final manifest SHA-256:
  `fa458ea4af5766df3660380943e3fc83e502d379f2cd9945c3e4c38e2f22d93c`
- combined phase gate: predeclared against `031083cc`; no phase source edit or
  result preceded `.lane/q1273-wrap-exact/COMBINED_PHASE_PREDECL.md`
- next gate: source-event-preserving conditional-phase composition, followed
  by exact 113-row classical and 17-row phase replay plus negatives
