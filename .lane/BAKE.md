# Byte-exact b523 Q1274 control bake

Date: 2026-08-23

## Verdict

`BAKE_PASS`; `PROTECTED_OPT_OUT_PASS`; `HOLD_DENSITY`; `HOLD_MODEL`;
`HOLD_PARITY`; `HOLD_SCAN`; `HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The only circuit changes are the replay-peak default `1278 -> 1274` and the
product-square ladder default `248 -> 244`.

## Default Q1274 identity

- operations: `12,935,433`;
- operations SHA-256:
  `61a57ce6e167b64663288ade584785b26562f61ff197f6ae0c11c85ea098ee8e`;
- Q: `1274`;
- average Toffoli: `917227.881`;
- inherited full 9,024-shot channels: `14/9/0`.

This is byte-identical to the frozen env-driven control target.

## Protected b523 opt-out

With `SUB4_PP_PEAK=1278 SUB4_SQUARE_LADDER=248`:

- operations: `12,876,472`;
- operations SHA-256:
  `4cb1787b181417c1e180ddf362fd7e44430ef2d422bb4184d73d7fe1924fdf7e`;
- Q: `1278`;
- average Toffoli: `914789.886`;
- inherited full 9,024-shot channels: `0/0/0`.

This reproduces protected `b523ecf` byte-for-byte.  No B1, round, fold, slope,
or other architecture setting changed.

## Local executable identities

- untrusted builder binary SHA-256:
  `c9dd06d538072e58fb665b1165c32b9829af6e2e8b10298f295ebd38f4ed2084`;
- trusted evaluator binary SHA-256:
  `6b94b8bbdf6ab82a7a35c9cbbec4ffc7e60452ab31e36dde8e37e49b5597ec33`.

Generated operation streams, binaries, evaluator logs, and result rows are not
committed.  The paired H64 density gate is next; the bake itself does not
authorize model promotion or search.
