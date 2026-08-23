# Q1276 exact-model qualification

Updated: 2026-08-23T03:40:02Z

## Verdict

`HOLD_ZERO_PENDING`

The CPU and CUDA models are bound to the byte-exact candidate. CPU equals the
unchanged full evaluator on the inherited nonce plus three ordinary nonces;
CPU also equals CUDA comb8 and comb16 on every frozen fixture. Low-count
fixtures 0 through 3 remain open. No hunt, submission, new spend, or range
scan has occurred in this lane.

## Live anchor

The benchmark was reopened before qualification. The live best remained
score `1,170,580,266`, Q1278/T915947, submission `792ac70`, source `bdf4845`.

Candidate source:

- commit `0b6ac181c46bd24ad6a5f8cd3d36b69bc040d73f`;
- tree `2fd5a034037d00cc9130f0733e48d2f4a89cc9b0`;
- parent/source anchor `bdf4845afa4f911192e20b5260b9efbd67655cf9`;
- only default changes: replay peak 1278 to 1276 and square ladder 248 to
  246;
- R1/R2 356/625, divide/multiply 698/696, g1000 width schedule, and fixed
  nonce 135608492183 are unchanged.

## Byte-exact reproduction

A clean environment release build emitted the same candidate byte-for-byte as
the source lane:

- operations: 12,929,346;
- compressed bytes: 51,271,953;
- SHA-256: `d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422`;
- MD5: `db4645d14ff62f009a3571f49aa69211`;
- `pingpong_div.rs` SHA-256:
  `ef9dd2d570c5826f0739509c45a082927985f68109c4dcbc53c36d9add2bb6d6`;
- `product_register.rs` SHA-256:
  `d2ee51194594123d982be3f135fbc087d24bf1cd645d8346c986f8d5dce3724d`;
- unchanged evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`.

The locally rebuilt binaries were not retained in Git. Their receipt hashes
were build-circuit `1cf961d8...` and eval-circuit `822d9cb7...`; executable
hashes can vary with build provenance, while the emitted artifact was exact.

## Model binding

The shared CPU/CUDA model is derived from the previously qualified g1000 port
at ops commit `7c0bddd10047de680650d236499f365d3b8445ef`. The round counts and g1000
schedule are unchanged. The host loader now hard-rejects every operation count
except 12,929,346, and the CUDA receipt will additionally assert the candidate
state digest before any range evaluation.

Committed model source hashes:

- `pp_host.h`: `257236aa61cafb8ba056271b7bd80d4144fb334bd31b11ae6b86405701c1c751`;
- `pp_model.h`: `4d3d748a3350851e263f9f3f180e6405b1240514dcff7a672b773751bbcf330e`;
- `ppcpu.cpp`: `8bbfad7fa8fa3efe0fa92805cf5ec7f41732edebceaa81ff2e8a7c9f05b9e6eb`;
- `ppgpu.cu`: `8fe6247eeb680ffad96423947909afc88321913bc039233dd85e18733b6a8fb3`.

`--max-faults N` retains exact complete counts up to N. It early-exits only
after the shared count exceeds N; the default remains the strict zero filter.

## CPU versus unchanged full evaluator

All rows used all 9,024 shots. CPU classical count and first classical failure
were exact on every row. Ancilla was zero throughout.

| nonce | CPU cls/first | full cls/phase/anc | full first | equality |
|---:|---:|---:|---:|---|
| 135608492183 | 15 / 32 | 15 / 5 / 0 | 32 | exact |
| 0 | 18 / 521 | 18 / 11 / 0 | 521 | exact |
| 7 | 20 / 594 | 20 / 11 / 0 | 594 | exact |
| 2500069332 | 17 / 266 | 17 / 10 / 0 | 266 | exact |

The full evaluator was unchanged and its tracked `results.tsv` stayed clean.
Generated patched artifacts and logs remain outside Git.

## CUDA parity

One bounded, isolated parity stage completed without a range scan. The
incumbent process and its immutable inputs were identical before and after;
the candidate CUDA process exited normally.

- state digest: `5a0a4564563a201a`;
- CUDA binary SHA-256:
  `672a47004f1f0a4a3ebc0d0a3e4a41e2dd903b1e1493bf493757fefed355cf2d`;
- Linux CPU binary SHA-256:
  `73f09fb8f5d84bdd595c730e0be34a8a8abb5d78184c8f431987708b4d2cc61b`;
- wrong-stream operation-count guard: exit 2 as required;
- all four rows: CPU = CUDA comb8 = CUDA comb16, including total count,
  first failure, and the five fault-cause counts.

Cause splits were respectively `3/0/11/1/0`, `9/1/8/0/0`,
`10/0/10/0/0`, and `9/0/7/1/0` in fixture-table order.

The dedicated-host stage path independently requires zero GPU applications
before and after rebuilding and repeating these equalities. Calibration accepts
exactly one host proof: a validated borrow receipt xor a dedicated-host receipt.

## Remaining gates

1. Stage the same exact source and artifact on a dedicated idle GPU and freeze
   binary, digest, and parity receipts.
2. Evaluate the predeclared zero calibration interval only. Confirm every
   retained row with the CPU model and unchanged full evaluator.
3. Only after an exact zero edge, evaluate the separate low-3 interval and
   freeze at least one exact full-evaluator fixture for counts 1, 2, and 3.

Until all three close with no false negatives, the stream is not eligible for
fanout or hunting. Final campaign acceptance still requires a full 9,024-shot
`0/0/0` result.
