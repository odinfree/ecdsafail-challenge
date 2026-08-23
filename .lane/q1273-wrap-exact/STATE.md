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
- next gate: source-bound scan-disabled CUDA transport and CPU/CUDA/trusted
  fixture parity; scanning remains forbidden
- parallel bounded gate: fixed H64 combined-density characterization is
  predeclared; nonce extension and hunting remain forbidden
