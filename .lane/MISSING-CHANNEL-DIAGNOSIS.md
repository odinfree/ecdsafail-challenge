# Q1274 square-register missing-channel diagnosis

Date: 2026-08-23

## Verdict

`DIAGNOSIS_PASS`; one general source-semantic correction is authorized.

Both frozen evaluator-only shots agree with the exact-field predictor through
the divide restore and `tlm_coord_add3x`.  Their first unequal phase is
`square_product_register`.  The circuit differs from the predictor by exactly
one dropped carry at bit 56, with opposite signs on the two inputs.  This is
the existing product-register square geometry, not a nonce or fixture rule.

## Frozen stream and harness evidence

- candidate operation count: `12,935,433` for both streams;
- nonce `444000000008` operation SHA-256:
  `33eff9694e42d9519007f51f2bc049fc89b77f118a136f1927534900fd111375`;
- nonce `444000000031` operation SHA-256:
  `32c816dcb1d5f6f1e2204f15b1b956dd0f0b5fe0ad6160d10b2849b4296e5315`;
- those hashes equal the corresponding frozen candidate rows in the paired
  H64 receipt;
- temporary instrumented `pp_profile.rs` SHA-256:
  `db6026a9e323621b6260db8c14fcd0df59548f877dde157b0549412821a42fd8`;
- temporary builder SHA-256:
  `2d35563cec14fbe58e3c9f8105c1605176a565ac0409b27ebb88f5a5899ebde1`;
- nonce `008` trace SHA-256:
  `f2d586973382371fc2a8bd67725a40c10a63a69c6ced3f710afe469e8e30e6b0`;
- nonce `031` trace SHA-256:
  `53b186f9c69dd369de9377f0ef795de6f4af95406f3e05c46ec3742b9ee8ad34`;
- predictor traces SHA-256:
  `05d7b240adbcd5e4ca08e27168951dca5b1797e9199542f9868bfcdb072df662`
  (`008`) and
  `b4eaf33fa265e3233a412c171993f5bcfc6accee4b581e8ac07abe97497d1b63`
  (`031`).

The temporary instrumentation injected the already-frozen shot input only
into simulator lane zero and emitted the two coordinate registers after each
existing phase boundary.  It did not alter the operation stream, seed, RNG
consumption, or channel accounting.  Each injected run finished with exactly
one classical mismatch, phase zero, and dirty-qubit count zero.  The
instrumentation was removed byte-for-byte before this evidence commit.

## First-divergence table

| nonce/shot | last equal phase | predictor after square | source after square | source minus predictor |
| --- | --- | --- | --- | --- |
| `444000000008/6885` | `tlm_coord_add3x` | `3927bb0c2509e9b88775f63d2e1a0d73e7f66a929853fa84f42f7d2a0c834497` | `3927bb0c2509e9b88775f63d2e1a0d73e7f66a929853fa84f32f7d2a0c834497` | `-2^56` |
| `444000000031/3691` | `tlm_coord_add3x` | `c5e45d3156468c023c4de9820944421c8a2cea241bd4bffc4af53a42b031293e` | `c5e45d3156468c023c4de9820944421c8a2cea241bd4bffc4bf53a42b031293e` | `+2^56` |

The compared source phase boundaries were `6608`, `13216`, `13466`,
`843206`, `4731778`, `5996596`, `5997758`, `6039225`, `6960082`,
`6960332`, `8227435`, `8662117`, `12915828`, `12916758`, `12923366`,
and `12935337`; the point-add shell is followed by the unchanged 96-op nonce
tail.

## Single authorized correction

Replace only the predictor's exact-field `out -= lambda^2` step with a direct,
parameterized value model of
`trailmix_ludicrous::square::product_register::square_sub`:

- split the 256-bit operand into two 128-bit halves;
- reproduce the five product-register accumulation steps;
- reproduce `mod_add_top` with its low-56 `add_f_window` carry drop;
- reproduce the `apply_f` NAF shifts `(0,+), (4,+), (6,-), (10,+), (32,+)`;
- reproduce each `w + 24` guarded window and drop its top carry.

No other point-add, ping-pong, seed, or fault-accounting rule may change.
The original H64 must close at 64/64 exact complete shot sets before the
precommitted disjoint32 is opened.  Any predictor-only shot blocks scanning.

