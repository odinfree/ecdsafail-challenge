# Q1272 repaired-model CPU to CUDA parity state

- status: `PREDECLARED / NO CUDA RESULT / FIXED8 SEALED`;
- base: `32943c9589097312e78692122c72566f834355ef`;
- repaired source: `6cdcbedcb201bad289dd1381ae60429f0691d6fd`;
- fixed corpus: `FIXED8.nonces`, SHA-256
  `6830df61133fdd99ade11e4c2aa3b450f14dfe9331a7b64ae61817346e0a960c`;
- interface: fixed eight nonces only; no nonce/range override and no submit;
- next gate: commit this predeclaration, implement the local packet, then
  verify manifest and negative behavior without CUDA or network access.
