# B1=24 Linux/CUDA parity

Updated: 2026-08-23T05:29:00Z

## Verdict

`HOLD_REMOTE_PARITY`

This packet binds the exact B1=24 predictor source before any borrowed-host
result. It authorizes only an isolated Linux CPU/CUDA comparison on the 32
predeclared nonces in `[81327465284,81327465316)`. It does not authorize a
range scan, nonce hunt, confirmer mutation, or fleet retarget.

## Circuit identity

- semantic source commit: `8a3c06e57f169d842fdb33722415dc66236a0b02`;
- semantic source tree: `b49fd5ef8bf42be563f9defa2f2a3282b27aa834`;
- parity predeclaration commit: `6f6da438735098008977143edd87585b79e86a4c`;
- base: promoted `b523ecf`;
- sole circuit edit: `value_width` `BREAK_1=30 -> 24`;
- operations: 12,822,408;
- operation SHA-256:
  `af28dbc49471651c3e856c62c1fd97cb429469cde4b66fe7fe082a0d23fe1ad7`;
- `pingpong_div.rs` SHA-256:
  `92ffe2f17886334e9db863e81683ef31911c46b759b7b7acac65017591e6c66d`;
- unchanged evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`.

The locally compiled source-bound CPU model reproduced operation count
12,822,408 and the four already-qualified counts `17,24,17,21` on nonces
81327465284 through 81327465287.

## Predictor source identity

- Rust CPU/checkpoint source SHA-256:
  `23ab339c466a41dbba4da65f2d4ab8bd70f8d504708a8e9135f12e48cead4658`;
- CUDA source SHA-256:
  `49989f9f5801005ac5ca478f24cddbda7c7ce99ee9287c876864435243014571`;
- upstream build script SHA-256:
  `cf7284dd7a5c29db04bdd1d42504cca7c69d6e1f2d2e618aacc61544e198f7ef`;
- port receipt SHA-256:
  `bb6fdba58f9ee1c5417f28436e5c5f2ecd300c962782f3952dee62108c23157b`.

The Rust source binds `VALIDATED_OPS=12_822_408`; the CUDA source independently
rejects any checkpoint whose embedded operation count differs from
`EXPECTED_OPS_B1_24=12_822_408`. The remote gate must also compare the generated
operation artifact's full SHA-256, checkpoint header and digest, Linux/CUDA
binary hashes, and every one of the 32 exact counts.

## Borrowed-host guard

Before and after parity, the stage must prove the protected Q1276 operation,
CPU, CUDA, fingerprint, parity, borrow, and drain receipt hashes unchanged.
It must preserve the exact incumbent confirmer PID/start/cwd with pending and
active counts both zero, preserve the clean Q1276 full-confirm source clone,
and observe zero GPU applications. Any discrepancy stops without a terminal
receipt.
