# Q1271 doubled-out lifecycle structural checkpoint

Verdict: `STRUCTURAL_PASS / INHERITED_FULL_REPRODUCED / FROZEN-EIGHT PENDING`.

## Binding

- predeclaration: `d9c59bf2b1b26b9cac497037828902a20a0d7dbc`
- predeclaration tree: `2649e5a594a706819c183d0bcb8e138bc2eb88f2`
- frozen live source: `4eb93cb33bbf6a93229fe166b8d511c5e52ee253`
- control source SHA-256 (`pingpong_div.rs`):
  `a247d6c7f31fd382b3041e4cb2f21d13d7870551fe68344e22615a02e11c0d20`
- control source SHA-256 (`point_add/mod.rs`):
  `da681f674c2bd0be2c507eafcc7785e045530d920fa343a52593aecf65619ba9`
- candidate source SHA-256 (`pingpong_div.rs`):
  `0b95700c5c977e9128ce609840da5996928e873313195fcd44935b06ed7df15a`
- candidate source SHA-256 (`point_add/mod.rs`):
  `c4aa38c73e79e3d5860616b31e3f507c888667390c857b319bb912dae1fd538d`
- release build command:
  `cargo build --release --bin build_circuit --bin eval_circuit`
- candidate build binary SHA-256:
  `e22e9652c292023baa898b7792849cc3223dfedd63b86a6f45d58e20230c0797`
- unchanged evaluator binary SHA-256:
  `add5c87d9f6d53a0cac65d6a2d9dc1fc70a642a218aadb00a8508080b73ca4da`

## Default control

With `SUB4_PP_PEAK`, `SUB4_SQUARE_LADDER`, and the lifecycle flag absent,
unchanged `./benchmark.sh` reproduced:

- operations: `12,887,894`
- operation SHA-256:
  `d21eff47434a95fe6f1036a59ddda830cf261a269b1d5eb387bde7ae7b6346b2`
- Q: `1273`
- exact average T: `914242.763`
- full 9,024-shot channels: `0 / 0 / 0`

The control build/evaluator binaries were
`26fd9da82b4a2a04ae316a75753068bbd647a48e3bbbf2de8545ad3fa682b29d`
and
`7b4991159d22541fa8d12beefdc657e150f845d2e5d721bae043a593a9883227`.

## Default-off lifecycle and focused miter

`SUB4_PP_EVICT_DOUBLED_OUT=1` enables the only source-semantic change.  At
the loan boundary, `odd_correction = doubled_out XOR add_out`; the fold reads
neither `doubled_out` nor a replacement carrier.  Two CX clear it, its clean
slot is freed across the fold, and two CX rematerialize the same parity before
the existing inverse cleanup.  The default path emits the original stream.

The dedicated `SUB4_PP_DOUBLED_OUT_SELFTEST=1` miter passed:

- all eight `(sign, shifted-out bit, add carry)` branches;
- 64/64 direct inverse-cell value equality against the unchanged cell;
- 64/64 forward/production-inverse composition equality;
- four coupled 64-lane measurement masks (`0`, `all-1`, and two balanced
  masks), with exact relative phase equality;
- source/sign preservation and zero non-ABI qubits;
- unchanged emitted and executed Toffoli counts;
- exactly four extra CX plus the clean reset.

The first eight complete-branch witnesses are exact field-value checks.  The
remaining adversarial field-edge vectors retain the unchanged truncated-fold
debt: direct cell `6/56`, composed forward/inverse `9/56`.  Candidate and
control remain bit- and phase-identical on every such row.  This debt is
source-inherited and is not a lifecycle regression; production-domain gates
below are exact.

## Component gates

Environment for both gates:
`SUB4_PP_EVICT_DOUBLED_OUT=1 SUB4_PP_PEAK=1271 SUB4_SQUARE_LADDER=241`.

- full affine point-add selfcheck: PASS; Q `1271`; `957,797` emitted and
  `915,559.281` executed Toffoli; exact values, phase zero, ancillas zero.
- product-register square selfcheck: PASS; Q `1271`; `58,997` emitted and
  `58,738.531` executed Toffoli; exact values, phase zero, ancillas zero.

## Inherited default-nonce full reproduction

Command environment added
`SUB4_PINGPONG_TAIL_NONCE=65700024945645` to the component environment and
ran unchanged `./benchmark.sh` once:

- operations: `12,926,780`
- operation SHA-256:
  `93cfdf6d43a1199745fd8d25b029a078d6ceed50aefee5cec36bf9ce38fe8c2f`
- Q: `1271`
- exact average T: `915685.693` (rounded `915686`)
- classical / phase / ancilla: `13 / 11 / 0`
- first mismatch: classical shot `38`
- generated result-row SHA-256 before restoration:
  `4eb6605bf9350ee21f40445d3b7c1ed74b5d1585c517e01395aaf01292c5e612`

This exactly reproduces the inherited structural result and remains five
rounded Toffoli above the strict `915681` score-go ceiling.  Per the frozen
order, it opens the eight predeclared calibration rows but authorizes no
provider, range, hunt, submission, or public action.
