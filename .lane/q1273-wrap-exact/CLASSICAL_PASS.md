# Q1273 wrapped-register classical qualification

Verdict: `GO_CPU_CLASSICAL / CUDA_HANDOFF_READY`.

The terminal-canonicalized finite-width transducer is exact on every frozen
complete classical shot mask.  This closes the two blinded overflow witnesses
without an ideal-output fallback or a corpus-specific exception.

## Frozen identity

- structural source: `093d85d64de87aa5006a94868172f642daacf136`;
- operation count / SHA-256: `12,933,805` /
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- Q / shots / inherited full channels: `1273 / 9,024 / 12/12/0`;
- predictor checkpoint digest: `2148e09f4c4293b2`;
- model / host / CPU source SHA-256:
  `da56cb95e2c423e67e8d400b423117cc54d007505aa7281e7725bcadd2ea19ab` /
  `bc2df2182beb8ebcc103a3fc498a8ca65911bf52439566dbfa1284e88407f98a` /
  `cc93e3ea51ddcb94857452e5aa3c9cfb39327a89711f703193e494daa2585d97`;
- qualified CPU binary SHA-256:
  `7f9a49d25f0c487d7f35ea09beff3749d2a64050b46089fbf078dadaabb4da00`.

## Exact-mask gates

The hardened binary was run twice on all 113 frozen fixtures.  Both raw
outputs were byte-identical per fixture, and every complete shot-index mask
equaled the unchanged evaluator oracle:

| corpus | rows | classical faults | exact |
| --- | ---: | ---: | ---: |
| inherited | 1 | 12 | 1/1 |
| H64 | 64 | 870 | 64/64 |
| D16 | 16 | 232 | 16/16 |
| blinded D32 | 32 | 480 | 32/32 |
| total | 113 | 1,594 | 113/113 |

- final summary SHA-256:
  `51d9802bee64c6865b294b1e3ac7f40d6717ce258677ea7b9bbfa4a5841a413d`;
- final immutable manifest SHA-256:
  `fa458ea4af5766df3660380943e3fc83e502d379f2cd9945c3e4c38e2f22d93c`;
- final artifacts:
  `/Users/olifreuler/ecdsa-ops/q1273-wrap-exact-ea6a02f/final-masks/`.

The structural transducer miter passed 4,096 deterministic fixtures.  The
loader/state packet passed all nine fail-closed negatives: wrong count,
same-count/wrong-SHA, wrong checkpoint state, bad magic, missing stream,
malformed nonce, malformed shot index, and disabled scan mode.  SHAKE256 known
answers also passed.

## Handoff boundary

The classical CPU model is qualified for an isolated CUDA transport/parity
port.  The nearest transport shell is the Q1274 repair-r100 `ppgpu.cu` with
SHA-256
`585d67a57edc5e953bb3c12792810e58e1a5fb8517788759e737cd214c194c26`.
It is only a transport reference: CUDA parity is not claimed here and no GPU,
provider, range, hunt, or submission was used.
