# Promoted Q1272 shared CPU/CUDA classical-model checkpoint

Date: 2026-08-23

Verdict: `CPU_INHERITED_EXACT / CAUSAL_DIAGNOSTICS_SEALED / CUDA_UNRUN / H64_RUNNING / RANGE_DISABLED`.

## Exact binding

This source is bound to structural commit
`73422709ed70ba9725b3cb592770bcf197df4cdb`, operation count `12,904,643`,
operation SHA-256
`ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`,
and the exact three-variable environment recorded in
`INHERITED_CLASSICAL_PASS.md`. The loader derives and enforces checkpoint/tail
state digest `e9b2d20ecd1169a8` in addition to the exact operation count. The full
operation SHA remains an external packet gate.

The shared source was mechanically retargeted from the previously qualified
Q1272 rescale CPU/CUDA implementation, then independently compared with the
committed exact Rust model. Its source identities are:

- `pp_model.h`:
  `120979945f82318e9df77014fabea3d2f8a9dea3c433e1ff5636cb3cb654424b`;
- `pp_host.h`:
  `b635c95deb5bab2b89ea65de4dafdba22ea4184a647c82d4bb5680450f976435`;
- `ppcpu.cpp`:
  `8dbc8687f2bc5dcfae2861d9ab0e8e757785d7eb608d6d2b05296f04f0c1ae4d`;
- uncompiled CUDA handoff source `ppgpu.cu`:
  `c40e32d3bce59d8443b695777a452adf7dd80baeba4369d4edd1ed5c2b6fef30`.

The local arm64 CPU qualification binary SHA-256 is
`501ee20c42ab402189d524c4053cc50276a06b6248ff83f51f55925ee76818ed`.
No CUDA compiler, device, provider, or hunt range was used. Both CPU and CUDA
sources compile range mode out unless a later reviewed build explicitly sets
`PP_ENABLE_RANGE_SCAN`.

## Exact inherited gate

On nonce `65700024945645`, the shared CPU source returned the same 23 sorted
fault shots and masks as the exact Rust model and trusted evaluator. Its raw
`faultshots` SHA-256 is
`46c6192499165eb5c2d2cd91d5b3478aafa25fc653f371fcc54b2e71f68a8fb0`.
Two causal-diagnostic runs were byte-identical, SHA-256
`b35613a083650e3d9c21c7993a778c338e67dd55c1fad0a95dad1a718ba3c1fd`.
The committed normalized fixture
`INHERITED_CAUSAL_DIAGNOSTICS.tsv` has SHA-256
`ab647dc2345fade447d47547037962e399d66142e57519563769cfe3a93d8fcb`.

The 23 failures split into 18 first-width violations and five hard failures:

- soft walk deficits: 18, every one a post-add excess of exactly one bit;
- hard replay-multiply coefficient failures: shots 292, 3094, and 4897;
- hard replay-divide coefficient failure: shot 6692;
- hard multiply terminal failure: shot 7956.

The first-deficit sampled indices are `680, 583, 649, 556, 450, 690, 651,
600, 651, 145, 688, 608, 659, 666, 678, 641, 517, 145`, in shot order.
Repeated indices are intentional: 651 covers two shots and 145 covers two.
This is causal first-deficit attribution, not a claim that a single +1 at each
index clears the corresponding final fault; after repairing one boundary a
later boundary may become the next violation.

## Fail-closed gates

- SHAKE256 empty-string and `abc` KATs passed;
- exact target state digest reproduced `e9b2d20ecd1169a8`;
- range mode exited 2 with empty stdout;
- a valid same-count stream with a different nonce tail exited 2 with empty
  stdout (stderr SHA-256
  `9e6a04d189f70ab2850411f104f5ae6f60572f25ed74a8e8efd86861e5bad69a`);
- an older wrong-count stream exited 2 with empty stdout (stderr SHA-256
  `a2cb1f534578ca43dd027a540e5ba75d800cb425439ba3fa7f3c0b286fd155b1`);
- scan-disabled stderr SHA-256:
  `454b84aee200e8f60dcf721081b227877479f478ddf45812910e693955d78851`.

H64 complete-mask equality remains the next terminal CPU gate. The CUDA source
is a handoff artifact only until Linux compilation, negatives, and complete
CPU/CUDA/trusted fixture equality are sealed. Conditional phase remains owned
by the independent combined-phase lane.
