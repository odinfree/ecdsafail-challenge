# Q1271 doubled-out lifecycle frozen-eight result

Terminal verdict: `SCORE_GO / VALIDATION_DIRTY / NO CLEAN CANDIDATE / STOP`.

## Frozen execution binding

- source checkpoint: `b69c17e16e0b9140d14f15c7d87314352ecaf7be`
- source tree: `8749e54dd9c3d801cd79edb5ff22b43c87fac0b9`
- `pingpong_div.rs` SHA-256:
  `0b95700c5c977e9128ce609840da5996928e873313195fcd44935b06ed7df15a`
- `point_add/mod.rs` SHA-256:
  `c4aa38c73e79e3d5860616b31e3f507c888667390c857b319bb912dae1fd538d`
- trusted unchanged evaluator SHA-256:
  `7b4991159d22541fa8d12beefdc657e150f845d2e5d721bae043a593a9883227`
- build binary SHA-256 used by `benchmark.sh`:
  `462260d57469b4ce5e144c8ab22e02d775bbf21555be1be532d657cbc58bac6a`
- environment common to all rows:
  `SUB4_PP_EVICT_DOUBLED_OUT=1 SUB4_PP_PEAK=1271 SUB4_SQUARE_LADDER=241`
- evaluator: unchanged full `9,024` shots
- Q1271 strict rounded-T ceiling: `915681`
- frozen reference live score: `1,163,831,339`

No other `SUB4_*` variable was present.  The rows ran once each, in the
predeclared order, with only `SUB4_PINGPONG_TAIL_NONCE` changing.

## Complete rows

Every stream has Q `1271`, `12,926,780` operations, and zero dirty ancilla
batches.

| tail nonce | operation SHA-256 | exact T | rounded T | rounded score | cls / phase / anc | first mismatch |
|---:|---|---:|---:|---:|---:|---|
| 65700024945641 | `b2b1e5076ef6c8bca1df870482060c4bf31d3fa262e0a35a77654b9a8aa0cd1e` | 915690.782 | 915691 | 1,163,843,261 | 18 / 9 / 0 | classical shot 318 |
| 65700024945642 | `00aecf4df5314350fe7f8b42a81b16d1dfe7f6c3f87f877d64b7bffb548784e3` | 915690.020 | 915690 | 1,163,841,990 | 16 / 13 / 0 | classical shot 159 |
| 65700024945643 | `3b78640cc2aadd0092c35c6e88b9377f122e0f90afac378760fdd6d6b5dd2762` | 915696.244 | 915696 | 1,163,849,616 | 19 / 15 / 0 | phase mask `0x0000000000008000` |
| 65700024945644 | `c1685eb822e8c82d8a725c0e1c50301548583f4938b7f24d8c277e79bbde70ac` | 915692.326 | 915692 | 1,163,844,532 | 27 / 19 / 0 | classical shot 85 |
| 65700024945645 | `93cfdf6d43a1199745fd8d25b029a078d6ceed50aefee5cec36bf9ce38fe8c2f` | 915685.693 | 915686 | 1,163,836,906 | 13 / 11 / 0 | classical shot 38 |
| 65700024945646 | `4c3742bbf99aee67b98310474b644739e11fbe7ec108632db58c89a931c2787f` | 915689.499 | 915689 | 1,163,840,719 | 21 / 18 / 0 | classical shot 259 |
| **65700024945647** | **`a13de41544a81672b07674acabecec0bb054201b8d1634ed79745bbc4be2f23e`** | **915675.850** | **915676** | **1,163,824,196** | **13 / 17 / 0** | phase mask `0x0000000000000004` |
| 65700024945648 | `8454057f3ae2d1b4d98e375293cb9afe9f4f8c33464afeb2290f38acdd69e98a` | 915684.857 | 915685 | 1,163,835,635 | 15 / 16 / 0 | classical shot 63 |

## Exact classical first-mismatch witnesses

- `...641`, shot 318: got
  `(0xda0890ac3d0e15eea49057a267e7e57eb0e215f4f3a70809fcb0259449af4874,
  0xb7abc3745f8cbc69be74f2725c880da6a069566d631f4db7a05c2a64d919162d)`;
  expected
  `(0x2a46c9845793e0caa3e2e2432016f079179d088c3293e483c82272ed7cb306c2,
  0x1238554d15d34f27952827a8761dc4c35b8cef2e2938c5d31ed772a596ad5115)`.
- `...642`, shot 159: got
  `(0x5012689d19b75a7934739157073c85ac475be1bc27ecb124e96da9c3bdf28e57,
  0x56192e131598e12d1753ec963ef7973b3cd67491d872b14f301c595d6c2ebd3a)`;
  expected
  `(0x3fee89b2c4a2b6187d560d58acd968b1b1ded66d6e67643611152f5b1ca16283,
  0xcd2e2b14450afc56d66a48c73c93a3ecaaf9abe44a99dee36c89840b50975346)`.
- `...644`, shot 85: got
  `(0x9d560af85cd84d26a59e56527a5711e683897a8255abdfc41291d3fdf9445d22,
  0xe1bf8c74d4c5a574dd8fa717cc63661f5efa9f7c724ed072f238258f98b53f86)`;
  expected
  `(0x4db66934233ca6c664990cb1b1eaeb649c6b9800bae2ac0215d65bae772bb543,
  0x65af76f872531bf6c96eed366e46e59c8082cad5e150de6c5acb74c8d6749b43)`.
- `...645`, shot 38: got
  `(0x57e8df97cf573a00ec14705835b22f88f7a0a0245dd3e3377db0beafabb904e8,
  0xb96186bb0c9d3c6fd9263b09b57c6add25f74dbdea07c61c64aa7be6e453947e)`;
  expected
  `(0xb4aff83b4641a36ed9e2fe41bf2a8c2a020b66513afb0458c4f7426cfa479b80,
  0xa5adeaa5cbef22be90ca5521f49dbb96954085a4073d02f253222dc875d1cd48)`.
- `...646`, shot 259: got
  `(0xf758c84c36687fc1663255d08a709debd73c3010b7711e98525bccbde9efcf4f,
  0xe9b18a9c6db7bf0654647b2ed13619201057c6a87c92d9e78f1c9f1a8ed8db38)`;
  expected
  `(0x109cff6a59b8f92fa5528faabf2c29c3d0af2953b7d4376963b0eb73b5dc9c9d,
  0x7d0fa8e021287099a277c7682de80b03b54e2978179dcf81a0aecee672b5e8c6)`.
- `...648`, shot 63: got
  `(0x2347fa07be5905672d3b52d37582c10d9d72339c92d2fb8edb155a955876f06c,
  0x6cfcba129163e7276636d71fae3d1dc87196cf1c6eb0ec678e28557e4efcd0d4)`;
  expected
  `(0x194f148f979ab07657570691991e310704db9ad48fad6c354d8b43910a370cdf,
  0x215473fad63aa680987b39e997a15894faae18ab2b0358811364cc2bb06fef88)`.

The generated eight-row `results.tsv` had SHA-256
`5d70c57cb9303593bc9d50c4569a262149b138920899ad3298a1e6fc0f2f448b`
before restoration to the tracked ledger.

## Verdict

Nonce `65700024945647` is the sole frozen row below the declared T ceiling:
rounded T `915676`, five Toffoli of headroom, and a frozen-score improvement of
`7,143`.  Its `13/17/0` channels make it only `SCORE_GO / VALIDATION_DIRTY`.
None of the eight rows is clean, so there is no candidate and no live refresh.
The predeclared set is exhausted.  No provider, range, hunt, submission, or
public action was taken or is authorized by this packet.
