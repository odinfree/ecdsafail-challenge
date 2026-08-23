# GO_Q1270: routed-control checkpoint

Date: 2026-08-23. Branch: `research/burn-q1270-target0-saddle`.

## Verdict

`GO_Q1270` for local structural validation. The default-off
`SUB4_PP_EVICT_SIGN_XOR_ADD=1` lifecycle removes the sole remaining
1,271-qubit owner in the descended geometry without adding a Toffoli. Every
profiled phase is at or below 1,270 qubits, and the supplied exact component
checks preserve values, relative phase, and scratch cleanup.

This is not a shipping or submission receipt. The lane did not run a nonce
search, cloud worker, external evaluator, or submission.

## Architecture

After `routed = doubled_out AND (sign XOR add_out)` is created, the XOR wire
has no consumer until `routed` is uncomputed. The candidate reverses its two
CX gates, releases the clean wire across the correction fold, and reconstructs
it from the still-live parents immediately before the original AND uncompute.

The feature is default off. With the flag absent, the source follows the
protected path byte for byte.

## Three-row ablation

| row | geometry | checkpoint | Q | diagnostic T | clean contract | conclusion |
|---|---|---:|---:|---:|---|---|
| protected composition | 1271 / 1272 / 241 | off | 1271 | 915100.86 | prior PASS | frozen ancestor |
| descended geometry control | 1270 / 1271 / 240 | off | 1271 | 916333.09 | `0/0/0` | `pp_mul_replay` alone binds |
| routed checkpoint | 1270 / 1271 / 240 | on | **1270** | **916295.41** | `0/0/0` | structural GO |

The three geometry values are `SUB4_PP_PEAK`,
`SUB4_PP_MUL_REPLAY_PEAK`, and `SUB4_SQUARE_LADDER`. The candidate profile
reported 12,953,540 operations before the 96-operation tail and 959,138 CCX
plus 28 CCZ. Rounded diagnostic T is 916,295; the Q/T product is
1,163,694,650, 136,689 below the frozen 1,163,831,339 reference. This is a
local diagnostic comparison, not an official score.

All candidate profile owners:

| owner | peak Q |
|---|---:|
| `pp_div_replay` | 1270 |
| `square_product_register` | 1270 |
| `pp_mul_replay` | 1270 |
| `pp_mul_walkback` | 1270 |
| `pp_div_walk` / `pp_div_walkback` / `pp_mul_walk` | 1056 |
| coordinate phases | 1026 |

The exact peak census at operation 927,240 in `pp_div_replay` summed eight
owner groups to 1,270 live wires. No profile phase allocated above 1,270.

## Exact validation receipts

1. Protected stream identity:
   - emitted operations: 12,919,161;
   - `ops.bin` SHA-256:
     `590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa`;
   - identical to the frozen `a220903` receipt.
2. Routed-control focused miter:
   - 64/64 lanes and 8/8 `(sign, add_out, doubled_out)` arms;
   - identical output values and relative phase;
   - scratch zero;
   - identical CCX/CCZ, HMR, and CZ counts;
   - exact `+4 CX +1 R`;
   - standalone peak 574 -> 573.
3. Inherited composition miters:
   - target0/sign alias: 64/64 lanes, 16/16 arms, phase equal, scratch zero,
     Toffoli equal, peak 575 -> 574 under the required doubled-output
     lifecycle;
   - selector eviction: 64/64 lanes, 8/8 arms, phase zero, scratch zero,
     Toffoli equal, peak 573 -> 572.
4. Full affine component selfcheck:
   - 959,166 emitted Toffoli;
   - 916,222.859 executed diagnostic Toffoli;
   - 1,270 peak qubits;
   - process exited successfully after all value, phase, and scratch asserts.
5. Product-square component selfcheck:
   - 59,014 emitted Toffoli;
   - 58,741.016 executed diagnostic Toffoli;
   - 1,270 peak qubits;
   - process exited successfully after value and cleanup asserts.
6. Complete 64-lane profile:
   - `classical_mismatch=0`;
   - `phase=0x0`;
   - `dirty_qubits=0`.

The bare target0/sign harness has an unrelated standalone peak binder and does
not demonstrate its one-wire loan unless the doubled-output lifecycle is also
enabled. That dependency predates this experiment; the required composed
harness passes as recorded above.

## Frozen artifact and source identities

- candidate emitted operations with the fixed inherited tail nonce:
  12,953,636;
- candidate `ops.bin` SHA-256:
  `ec4fadc0b5cd1c26ee5d81001b7a72692678b61a94c4091032dd93b8b62eb63a`;
- `src/point_add/pingpong_div.rs` SHA-256:
  `9b1e5e8540a01584e1238c27328481ba67db3b167aa199db4113e846f1eb6295`;
- `src/point_add/mod.rs` SHA-256:
  `3fbe6baa8bb4638217f7416b858f4ddd57906fdaaecc500d860f1ca96f1ed60f`;
- unchanged local evaluator SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`.

Generated `ops.bin`, build output, and transient logs are deliberately absent
from the commit.
