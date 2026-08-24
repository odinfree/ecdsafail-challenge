# Q1266 GPU parity terminal receipt

Decision: `HARD_NACK_GPU_PORT_COMB16_INTERMEDIATE_DRIFT`

The frozen GPU qualification contract failed. The current `ppgpu` binary and
all use of its comb16 path are closed for search.

## Binding and environment

- pre-reveal contract commit: `7ef751ce8cb47dbbe0bee67c8e1f364107f49786`
- CPU-truth reveal commit: `de4b650d3cdc96c0e808bf6b61cbfafa103e8a74`
- candidate ops SHA-256: `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- CUDA source SHA-256: `687d1df6cd5b853d55e38b3ae066045bdffe3d01e3508b10ffe6704145f9caaf`
- remote CPU binary SHA-256: `175fb72b8e5a9eafbf7393aab319d871b53530a04b3b45b5364604f85c81aba1`
- remote GPU binary SHA-256: `b413fc923a649b372c6786cf1d0f01d231908f46172b9ec73a679d3b6bc630ea`
- parity runner SHA-256: `4f38005123598949a259378fbfa6592cd27349578ba51d2c845c9214d0e719ce`
- evidence archive SHA-256: `d4f069f867b2626193ce89f785f40d31ad314fd0a313466cb0deebbb14fa7352`
- evidence archive bytes / local path: `6755` /
  `/tmp/q1266-gpu-parity-hard-nack-logs.tar.gz`
- device/toolchain: one RTX 4090, driver 580.159.03, CUDA compiler 13.0
- frozen build command: `g++ -O3 -std=c++17` plus
  `nvcc -O3 --std=c++17 -lineinfo -Xptxas=-v -gencode arch=compute_89,code=sm_89`
- build wall time: `147.59 s`

All transferred source, truth, and artifact hashes matched before compilation.
The first parity attempt stopped before evaluation because the minimal image
lacked `zstd`; installing that runtime dependency and rerunning did not change
source, binary, fixtures, or flags.

## What passed

- remote CPU truth selfcheck: exact
- GPU prefix operation count/state digest: `12596439` / `bc16e98fdac46783`
- block batch inversion: 4/4 configurations passed (comb8/comb16 crossed with
  128/256 threads)
- full fault-mask matrix: 28/28 fixture/configuration diff files empty; all 121
  frozen shot-index/mask lines matched under all four configurations
- comb8 probe set: squeezed bytes and all Jacobian fields matched on calibration
  and blind-0
- comb8 replay of already exhausted local canary: 4096 nonces, zero survivors,
  exact state digest, `15692.9 nonce/s`

These subordinate passes do not override the contract falsifier.

## Falsifier

The first comb16 Jacobian probe, on the inherited calibration nonce, disagreed
in all six fields:

| field | CPU / comb8 expected | comb16 observed |
| --- | --- | --- |
| jx | `0b2eee22782ed23bc7046d1e432b13a5579c2256a800944e41b22dd72ecc884c` | `579a0ceb61c6ba50b0514a0dbdc38b5dddaa8fb3c407a52d488c5e024e2a867f` |
| jy | `ce5db124846474a3b3c6143665dcea4beb6040b50d294635218527e1dfb80ac5` | `646e9551b3d57dce3550f787508a108cbe8f903bbf93c60cc3064d9de894d627` |
| jz | `cdca6d97f5d0be8e70df80da27e23ef81f45204b4d41a866d528c159e77a1ac0` | `ff6545920a457a175041ffd456612447912a163a461108c923a2630017203dbc` |
| kx | `d0dc0c743480726ff81de53ff5842766b2a34f905aa218297dda6c1dec564fa8` | `205851049279112325ca68d19b559638273e6f7aa01b6b141bff6429fe40b129` |
| ky | `99b77045fbf81067541a02debb26cefe508066ea5eeaaf0f089dd41e45b96fee` | `a1f2deab41a909f68b76094acf9990337990607ced94d1f9bfa8179ea6703bd3` |
| kz | `9e7edabe531c7d2b753b7e4cd288f1e7053b995c97b478d07b56ba7a65baa339` | `8ca585152c7177d4c3bcebd158d585032eb54b48d270abe0f59a8d2e2b149878` |

The fact that downstream fault masks happened to agree is not source-exact
parity. Aggregate or final-verdict agreement cannot launder an incorrect
intermediate state.

## Closeout

No new nonce range was run. The only GPU range was an exact replay of the
previously exhausted 4096-nonce canary. The comb16 canary replay was never
reached. No postfilter, trusted evaluator, bake, push, public note, queue, or
submission action occurred.

The uniquely labeled experiment-owned Vast canary was destroyed after evidence
harvest; a filtered provider query reported zero active instances under that
label. Runtime was under one hour, so rental exposure was below USD 0.2875;
exact provider billing was not claimed.

This binary is not salvageable by switching a command-line flag after reveal.
A future GPU attempt must remove the invalid optional architecture before its
own freeze, use new blind nonces and a fresh exact intermediate-state contract,
and earn a separate admission. `submit=CLOSED`, `no_submit_ack=yes`.
