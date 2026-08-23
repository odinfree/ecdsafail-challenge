# Q1272 selector-eviction classical model port result

Updated: 2026-08-23

## Decision

`PORT_READY / KNOWN_NONCE_EXACT / WRONG_STREAM_FAIL_CLOSED / HOLD_H64`

The qualified Q1274 Rust predictor was ported to exact structural commit
`14608572e84daf89397768c43ac0d812c714c3bd`.  Only two model identities were
changed: the hard-coded value-width `BREAK_1` now matches the source value 24,
and the operation-count guard now requires the exact Q1272 selector stream.
The selector lifecycle edit is classically exact, so it needs no model-side
exception.

This lane deliberately consumed no H64 row and no disjoint holdout.  It has no
range, hunt, provider, CUDA, phase-certification, or submission authority.

## Source and artifact binding

Exact candidate environment:

```text
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
SUB4_PP_FOLD_SELECTOR_EVICT=1
```

Clean source identities:

```text
pingpong_div.rs                 de5e347383a9bab4d76a2776b3bcee4bebda4fecb65beb3dd1ad4c1cbf4c1095
product_register.rs             872f9a18929cc576dcdbfd05735bc3243b756488ce6acc70ce705f46e2b302ee
point_add/mod.rs                 3106691965fbd0002fc0dc427e07f28f30654be49b748beb08d93b30c21db490
unchanged eval_circuit.rs        b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b
ported pingpong_filter.rs        e5ef16cf344ac90d8f77489b18601a66f35396c875d813925b1beb02d9533c53
release pingpong_filter binary   a9c2a49aaf867e5e0337df0d7502c9e5804f2292059dbd249259525e4b62bc71
```

An independent `build_circuit` run under that environment reproduced:

```text
emitted operations  12,908,488
ops.bin SHA-256     678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0
```

The generated operation artifact was removed after hashing.

## Frozen known-nonce check

The predeclared first check used only inherited nonce `81327465284`, whose
unchanged full evaluator result was already sealed as classical/phase/ancilla
`18/13/0`.  The ported model built the exact 12,908,488-op stream and returned:

```text
81327465284 18
```

Thus the known classical count agrees exactly.  This one exposed nonce is a
port smoke test, not model qualification.  Complete mismatch-set equality on
the frozen H64 and disjoint sets remains mandatory.

Local timing for the smoke test was 3.63 seconds to build and absorb the
stream once, then 0.002 seconds XOF, 0.102 seconds elliptic-curve draw, and
0.494 seconds classical model for the nonce.  These timings are diagnostic
only and do not authorize range economics.

## Negative control

The same command with selector eviction omitted built the protected
12,904,991-op stream.  The predictor refused it before screening:

```text
pingpong_filter: refusing stream with 12904991 ops; exact Q1272 selector model requires 12908488
exit=2
```

This proves the first wrong-stream guard fails closed.  Further source and
Linux/CUDA identity guards remain part of the sibling qualification gate.

## Next gate

Wait for the independently frozen paired H64 density verdict.  If it passes,
the sibling lane may import this implementation, compare all 9,024 classical
shot bits per nonce on H64, reveal its predeclared disjoint holdout, and then
run Linux CPU/CUDA full-mask parity.  No canary begins before those gates and
the phase/confirmation path are green.
