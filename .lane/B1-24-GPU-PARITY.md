# B1=24 Linux/CUDA parity

Updated: 2026-08-23T05:47:00Z

## Verdict

`PASS_COUNT_PARITY_HOLD_MASK_PARITY`

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

Before and after parity, the stage proved the protected Q1276 operation,
CPU, CUDA, fingerprint, parity, borrow, and drain receipt hashes unchanged.
It must preserve the exact incumbent confirmer PID/start/cwd with pending and
active counts both zero, preserve the clean Q1276 full-confirm source clone,
and observe zero GPU applications. Any discrepancy stops without a terminal
receipt.

## Count-parity result

The isolated RTX 4090 gate completed without a range launch. Linux CPU and
CUDA produced byte-identical rows on all 32 predeclared nonces. The CUDA
self-test passed, an intentionally wrong `--ops` value was rejected with exit
code 4, no GPU application remained, and the protected Q1276 manifest was
byte-identical before and after.

- terminal receipt SHA-256:
  `24de81effc820a65033c79879e75d8ebc1586587a8ab6cece8f0796eae86efb3`;
- CPU/CUDA fixture SHA-256:
  `6411fd885aab5ddd19f673217c4c2cb5a51a7230b70bf91d143b71f1c2d1c920`;
- checkpoint SHA-256:
  `7080f69f4aabd7be663713d57c553d1e80913a2fc1d5b4958e7ab5c4b46a8dcc`;
- Linux `build_circuit` SHA-256:
  `6b41660048f26c86a37dbd96cf2f18299fc3377d7e0fe9e405a478544161c7d5`;
- Linux CPU predictor SHA-256:
  `5cb53f0a7694d3f9e6a1b60bf3e0167d19926ef12a6405c72ccc4b1ce933340e`;
- CUDA predictor SHA-256:
  `7bb7b2f2b4460e8372016d1d8cbb48c9015306c9ae31d289c853ac04e43f785a`;
- protected manifest SHA-256:
  `b8a5a89b4c528b588eb8482884f3556639f7d7bdca1ddd5748aa7ed736a6b5cb`.

The exact counts, in nonce order 81327465284 through 81327465315, are:

```text
17 24 17 21 34 30 18 26 26 26 16 27 23 36 34 24
17 36 26 16 21 24 26 19 32 27 19 18 31 27 23 18
```

Count equality is necessary but does not prove that CPU and CUDA identify the
same failing shots. The next gate therefore freezes these same 32 fixtures and
requires byte-identical complete 9,024-bit classical fault masks, plus
wrong-stream rejection, before this lane can become hunt-capable.
