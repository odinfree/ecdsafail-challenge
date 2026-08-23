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
- combined phase gate: `GO_CPU_COMBINED / CUDA_HANDOFF_READY`
- phase donor: `031083cc`; source schedule/fixtures preserved exactly
- combined exactness: classical `113/113` with `1,594` faults; conditional
  phase `17/17` with 87 clean-phase faults; negatives `17/17`
- combined manifest SHA-256:
  `c1088ca0e3bf0d9215f63b6823bf490d408ba46e2cf3271d35c40b449d5fe847`
- fixed H64 density: terminal `64/64`, joint lambda `18.359375`, predicted
  zero `0/64`; manifest `986d1c97376590450cca3c6856598ef045fff7cff67f563f2aa868ba3ea443f4`
- live displacement: promoted `4eb93cb`, Q1273/T914243; this Q1273 stream and
  its CUDA/hunt path are score-dead
- next gate: none in this lane; rebase structural work onto promoted source
