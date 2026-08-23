# Deterministic pred0 canary rule

This rule was committed before the bounded local predictor run.

- Parent fixture seed: `6744ead7c2070dc187433e2c766858dcb036c4ab50cc15f3bc4f98e3d5db7e3c`
- Derivation input: `compare19-pred0-canary-v1:6744ead7c2070dc187433e2c766858dcb036c4ab50cc15f3bc4f98e3d5db7e3c`
- Derivation SHA-256: `f52d550228b2a57c6824e935c796c9a44367a7a2941998139e6f00f6fc0d6c47`
- Start nonce: first 48-bit digest chunk interpreted unsigned, `269575048538290`
- End nonce, exclusive: `269575048800434`
- Maximum count: `262144`
- Order: strictly ascending
- Selected canary: the first `pred_cls=0` nonce emitted inside that interval

If the exact predictor completes the bound without a survivor, or the measured local rate makes completion impractical, no alternate range may be substituted. The packet records the terminal coverage or exact measured rate and leaves the pred0 gate open.
