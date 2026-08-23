# Q1273 combined classical/phase CUDA parity handoff

Status: `PREDECLARED / HOLD_COMBINED_CPU / HOLD_CUDA / HOLD_RANGE`.

Date: 2026-08-23

No CUDA result, provider action, nonce range, survivor, or submission preceded
this document.  This lane is a bounded parity handoff.  It cannot scan.

## Frozen circuit and qualified classical base

- structural source commit:
  `093d85d64de87aa5006a94868172f642daacf136`;
- classical qualification commit:
  `7b339f5d1fce6af6f3b3f360cb856b95326bb5ff`;
- qubits / emitted operations: `1273 / 12,933,805`;
- operation-stream SHA-256:
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- checkpoint/tail state digest: `2148e09f4c4293b2`;
- qualified repaired model SHA-256:
  `da56cb95e2c423e67e8d400b423117cc54d007505aa7281e7725bcadd2ea19ab`;
- qualified host/model/CPU source SHA-256:
  `bc2df2182beb8ebcc103a3fc498a8ca65911bf52439566dbfa1284e88407f98a` /
  `da56cb95e2c423e67e8d400b423117cc54d007505aa7281e7725bcadd2ea19ab` /
  `cc93e3ea51ddcb94857452e5aa3c9cfb39327a89711f703193e494daa2585d97`;
- classical final summary / manifest SHA-256:
  `51d9802bee64c6865b294b1e3ac7f40d6717ce258677ea7b9bbfa4a5841a413d` /
  `fa458ea4af5766df3660380943e3fc83e502d379f2cd9945c3e4c38e2f22d93c`.

The pending combined CPU source may be consumed only from a terminal committed
`GO_CPU_COMBINED / CUDA_HANDOFF_READY` revision descended from `7b339f5`.  Its
commit and complete source hashes are deliberately not guessed here.  The old
phase branch at `031083cc` is fixture/schedule provenance only; its classical
model is not a CUDA donor.

## Frozen phase provenance

- phase schedule header SHA-256:
  `4249864aca9e2928a33865ea086b99ef8ecccc9eb596ba4c3e57468ba88d25e5`;
- phase schedule ledger SHA-256:
  `a4043530337b91e97d7a42dde2aff7e5a967a0b820ad1a9a120b3c366d7a5294`;
- phase fixture ledger SHA-256:
  `e148f24d99ae45b3c6930a33d49173fd31b2c236593d98375956077b3feb4d1b`;
- source events / R-Hmr words: `3,983 / 1,942,962`;
- conditional contract: `clean_phase_mask = raw_phase_mask & ~classical_mask`;
- survivor contract:
  `classical_mask == 0 && clean_phase_mask == 0`.

Raw phase on a classically dirty shot is never promoted as an independent
claim.

## One allowed CUDA family

The parity binary uses the committed combined model as its only semantic
source.  The allowed port is:

1. reuse the combined `pp_model.h` under `PP_HD` so host and device compile the
   same arithmetic and trace code;
2. use the combined `pp_host.h` to load and bind the exact compressed stream,
   operation count, operation SHA, checkpoint/tail state digest, and phase
   schedule identity before any corpus derivation;
3. derive one requested nonce's exact 9,024-shot corpus on the host, transfer
   those shot records to a device-only parity kernel, and emit complete
   classical and conditional-phase masks;
4. accept only explicit frozen nonces or a frozen nonce file.  There is no
   `from`, `to`, `range`, `screen`, early-exit, survivor-only, or approximate
   mode in this family;
5. preserve canonical shot ordering and output framing so complete masks can
   be compared byte-for-byte with both the qualified CPU and unchanged
   evaluator oracles.

The mechanical transport reference is Q1274 repair-r100 `ppgpu.cu`, SHA-256
`585d67a57edc5e953bb3c12792810e58e1a5fb8517788759e737cd214c194c26`.
Only its CUDA error handling, single-nonce harness layout, device transfer, and
host lifecycle are reusable.  No Q1274 or Q1272 predictor semantics transfer
by name or label.

## Frozen parity gates

The eventual packet must bind and replay all of the following without opening
a new corpus after the first CUDA result:

| corpus | rows | required equality |
| --- | ---: | --- |
| inherited | 1 | CPU = CUDA = unchanged evaluator, full classical and conditional-phase masks |
| H64 | 64 | CPU = CUDA = unchanged evaluator, full classical masks |
| D16 | 16 | CPU = CUDA = unchanged evaluator, full classical masks; also phase fixtures |
| blinded D32 | 32 | CPU = CUDA = unchanged evaluator, full classical masks |

Total classical gate: `113/113` complete masks and `1,594/1,594` fault shots.
Total phase gate: `17/17` complete conditional-phase masks.  The inherited
classical and phase rows are repeated after all other fixtures; both stdout and
stderr must be byte-identical.  CUDA source, CPU source, phase schedule,
fixtures, ops stream, checkpoint, build command, binaries, and all parity
outputs receive SHA-256 receipts before any activation decision.

## Fail-closed gates

Before parity can be sealed, empty result output and the declared non-zero exit
must be demonstrated for: bad magic, wrong operation count, same-count/wrong
operation SHA, wrong checkpoint/tail state digest, wrong phase schedule,
missing stream, malformed/non-canonical/overflowing nonce, malformed shot
index, unknown selector, disabled scan, forbidden range flags, and incomplete
screen-plus-mask requests.  Source and checkpoint bindings cannot be bypassed
with an `allow mismatch` option.

Any classical mask difference, conditional-phase mask difference, schedule or
trace-count drift, non-determinism, permissive loader path, or scan-capable
binary is terminal `HOLD`.  Local parity readiness does not authorize a GPU
host.  A CUDA parity pass authorizes only a separately predeclared bounded
pilot after an explicit root gate; every survivor still requires the unchanged
full 9,024-shot evaluator at classical/phase/ancilla `0/0/0`.
