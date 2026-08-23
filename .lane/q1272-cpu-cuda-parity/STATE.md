# Q1272 repaired-model CPU to CUDA parity state

- status: `PACKET_READY / OFFLINE_VERIFIED / HOLD_CUDA_EXECUTION`;
- base: `32943c9589097312e78692122c72566f834355ef`;
- repaired source: `6cdcbedcb201bad289dd1381ae60429f0691d6fd`;
- fixed corpus: `FIXED8.nonces`, SHA-256
  `6830df61133fdd99ade11e4c2aa3b450f14dfe9331a7b64ae61817346e0a960c`;
- implementation commit: `1390a1464dd0a05d6d8b89edfc43df14bb7c9620`;
- CUDA source SHA-256:
  `23791a4aa69d3f88303bf64f8437a001f7f736721452490bc26b700ce908b072`;
- interface: fixed eight nonces only; no nonce/range override and no submit;
- packet manifest SHA-256:
  `5a016d0591024c71f20d5480084c0df1454bb8fb3bd4a947d5877e05565f9904`;
- archive SHA-256:
  `0d984dec387940836e45145cc2960a36edbc4cdbc813b91acaf71ca1d3f04705`;
- expected classical / phase transcript SHA-256:
  `b37aebb01c90a89490d2f5c545ec9f7dd6b77d9952699b7d31757f17ddf9ea91` /
  `a33b9abd86414551e1280d250c2a2e121a5e230f8d9a4a0066280937daa906f4`;
- offline negatives: 4/4 pass; clean archive extraction verifies;
- local CPU reconstruction: 8/8 exact, 150 classical rows and 32 clean-phase
  rows across 72,192 shots;
- CUDA compile/execution: not performed; local host has no `nvcc` or GPU;
- evidence: `PACKET_READY.md`;
- next gate: explicit future one-GPU execution of the immutable packet only.
  No provider, range, hunt, deployment, submission, or promotion authority is
  inferred.
