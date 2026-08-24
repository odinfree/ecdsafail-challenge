# Ping-pong prefilter upstream binding

Verdict: the Q1266 search uses the same checkpointed SHAKE256 plus classical
ping-pong modelling method as
`somejohnbforya/pingpong-prefilter`, but it does not execute that repository's
shipped binary or accept its compiled-in circuit constants.

## Exact upstream artifact inspected

- repository: `https://github.com/somejohnbforya/pingpong-prefilter`
- branch / commit: `main` /
  `da0e5721f14f5d956aa703b38311f4087388a7b1`
- upstream's stated circuit binding: frontier commit `8d7051b`
- upstream's own hard warning: model constants drift, and a stale constant can
  silently produce a wrong screen

That shipped artifact is therefore not admissible for this search. The live
candidate is bound to official source commit
`67524171baaf568dc3dc606f38515745f70804ff`, Q1266, and a different operation
stream.

## Admitted local artifact

- candidate ops SHA-256:
  `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`
- source-literal CUDA SHA-256:
  `dfa7cc860e24a4785ae3ec4da5451e7afaa9685f6ae2d9fe77f23cb185f0fa6a`
- exact distributed runtime SHA-256:
  `4ff81a62f3be5333104df9bfd937a967d405656340d0e4656fb5d4d647c53956`
- runtime bytes: `2808400`
- state digest: `bc16e98fdac46783`
- comb mode: `comb_bits=8`

The local model was retargeted from the source-literal CPU implementation and
qualified on frozen and blind CPU/GPU fixtures. Every GPU survivor is then
checked by the exact 9,024-shot CPU postfilter. A classically clean GPU result
is only a proposal; it cannot open trusted evaluation, promotion, queue, or
submission gates by itself.

## Anti-rot rule

Any change to official source, candidate operations, Q, prefix state, model
constants, CUDA source, or runtime bytes invalidates this admission. Regenerate
the prefix, rebuild the model, repeat bidirectional CPU/GPU parity, freeze one
runtime byte-for-byte, and re-run the exhausted-canary bootstrap before any
new range scan.

`submit=CLOSED`, `no_submit_ack=yes`.
