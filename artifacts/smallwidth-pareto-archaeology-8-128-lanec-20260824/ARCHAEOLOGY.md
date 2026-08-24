# Small-width Pareto archaeology (lane C)

## Verdict

`ADMIT`, but only as a local mechanism candidate: the exact
`topW_with_window_entry_carry` repair has a measured affine resource law and,
when a correct entry carry is already live, costs exactly one more peak qubit
and zero more emitted Toffolis than `approximate_no_cin`. It does **not** earn a
full-circuit, 256-bit, score, or submission claim. The next gate must compute or
host that entry carry in the promoted route, clean it reversibly, and run the
trusted full evaluator.

The cleanest sampled witness is `n=96, W=24`:

| Repair | Peak Q | Emitted T | Q*T | Validation |
|---|---:|---:|---:|---|
| `approximate_no_cin` | 216 | 23 | 4,968 | sampled pass, 64 lanes; theoretical fault `2^-25` |
| `topW_with_window_entry_carry` | 217 | 23 | 4,991 | sampled pass, 64 lanes |
| `exact_whole_chunk_with_chunk_cin` | 289 | 95 | 27,455 | sampled pass, 64 lanes |

Thus the exact top-window microkernel saves 72 Q and 72 T against the measured
whole-chunk repair, but only under the explicit live-entry-carry precondition.

## Binding

- Worktree: `/Users/odin/Documents/coding with codin/ecdsafail-smallwidth-pareto-repro-codex`
- Branch: `research/codex-smallwidth-pareto-repro-20260824`
- Harness commit: `d76c426f7ad568355ecdb29be946a2a455226ecb`
- Harness tree: `9e749e1829b85b5fb6b80e3faf30b22d1452f83c`
- Embedded promoted-source commit: `67524171baaf568dc3dc606f38515745f70804ff`
- Embedded promoted-source tree: `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- Script SHA-256: `9f5913dfb64ec9f58f12e3d9444c04ac0232d9de18790bd489bd52875581138b`
- Release binary SHA-256: `ed1c1de36b87d81cb4cc7ff8b6683c44561899b1669cf8857c72938f4c940f2a`
- Toolchain: `rustc 1.93.0 (254b59607 2026-01-19)`, `cargo 1.93.0 (083ac5135 2025-12-15)`
- Host: Apple M4 Max, arm64; local CPU only.

The measured primitive dependencies are byte-identical between the embedded
promoted commit and the harness commit:

| File | SHA-256 at both commits |
|---|---|
| `src/point_add/arith/adder.rs` | `4e8502d0bb590381e51d94345ac9337502e71c4e6f5bfe36f1597b15a03f4e5f` |
| `src/point_add/arith/compare.rs` | `0d1cf305c68263cd078ec96c10b2b00135bef21492f81ff4e3d7d45d33e5191e` |
| `src/circuit.rs` | `ac2255f6bcb6895c9da2dfe21c3a051a0ef8fc4e0af9598634fec0035dbf35c6` |
| `src/sim.rs` | `f0c72f2a280cd68acee1dbf8282098f72d6b3bf4311e0abf96d122fe002256d7` |

## Exact execution commands

The required default reproduction was run first, with possible inherited
overrides explicitly removed:

```sh
/usr/bin/time -l env \
  -u SMALLWIDTH_WIDTHS \
  -u SMALLWIDTH_MAX_BLOCKS \
  -u SMALLWIDTH_MAX_WINDOW \
  -u SMALLWIDTH_VALIDATE \
  ./scripts/run-smallwidth-pareto.sh \
  artifacts/smallwidth-pareto-repro-lanec-20260824
```

The exhaustive-small-grid / capped-larger-grid archaeology was then run as:

```sh
/usr/bin/time -l env \
  SMALLWIDTH_WIDTHS=8,16,32,64,96,128 \
  SMALLWIDTH_MAX_BLOCKS=32 \
  SMALLWIDTH_MAX_WINDOW=32 \
  SMALLWIDTH_VALIDATE=1 \
  ./scripts/run-smallwidth-pareto.sh \
  artifacts/smallwidth-pareto-archaeology-8-128-lanec-20260824
```

Integrity and source-binding checks included:

```sh
shasum -a 256 -c artifacts/smallwidth-pareto-repro-lanec-20260824/SHA256SUMS
shasum -a 256 -c artifacts/smallwidth-pareto-archaeology-8-128-lanec-20260824/SHA256SUMS
diff -q artifacts/smallwidth-pareto/results.jsonl artifacts/smallwidth-pareto-repro-lanec-20260824/results.jsonl
git diff 67524171baaf568dc3dc606f38515745f70804ff..HEAD -- \
  src/point_add/arith/adder.rs src/point_add/arith/compare.rs src/circuit.rs src/sim.rs
```

Both runs used the script's `cargo build --offline --release` path. No fetch,
push, provider, GPU, benchmark submission, or challenge submission occurred.

## Reproduction counts and hashes

The fresh default output is byte-for-byte identical to the checked-in output:

- resource rows: 1,650;
- event rows: 1,213;
- lift-assessment rows: 11;
- `results.jsonl`: `aea056dcd937a7bdb3513c2c335543c6fbf641e95ed7ab21e346ccd3b27cacde`;
- `discontinuities.jsonl`: `5e69ecb13d6607898caae16bbed2df1177a94fdc3fbd8f46c09c3c07c25580aa`;
- `lift-assessments.jsonl`: `09fa9718e109e66e63e89bf2aa64a30b949ff51a4c5c39908056b24d3232c286`;
- `SUMMARY.md`: `1682ad9b07b7dbf32c3a6260a5c45cc7a07ad0f6a7fd954f97d0b580d8cbfa21`.

The 8/16/32/64/96/128 archaeology output contains 1,164 resource rows, 748
event rows, and 15 lift-assessment rows. Its generated hashes are recorded in
the adjacent `SHA256SUMS`. The 1,038 overlapping 32/64/96/128 resource rows are
byte-identical between runs; their filtered-stream SHA-256 is
`1eceb3a46879168c5c5bf62c867e8ad92ee420f7c4637fbcb523e7668ab6144b`.

At `n=8` all legal knob values are present: 43 rows total (`topclean` 0..7,
`co_binder_topclean` 0..7, `windowed` 1..9, boundary windows 1..8). At `n=16`
the corresponding full grid has 83 rows (`topclean` and co-binder 0..15,
`windowed` 1..17, boundary windows 1..16).

Important qualification: this is exhaustive **parameter-grid** coverage, not
exhaustive input-state validation. Only 23/43 rows at n=8 and 25/83 rows at
n=16 carry `sampled-pass-64-lane`; the remaining rows are resource-only
`not-run` entries.

## Event and Pareto archaeology

The claimed 1,213 event rows reproduce exactly, but the name
`discontinuities.jsonl` overstates their composition:

- 1,105 are `pareto_adjacency` rows;
- 108 are detector-selected `adjacent_step` rows;
- the 108 selected rows collectively contain 47 plateau, 34 Q-step, 27
  T-step, and 15 owner-migration reason tags (tags can overlap).

Of the 1,105 Pareto adjacencies, five are zero-length `(delta_q, delta_t)=(0,0)`
edges. Each is the duplicate resource point shared by `topclean(k=0)` and
`windowed(blocks=1)` at one of 32/64/96/128/256 bits. After coordinate
deduplication there are 1,100 meaningful adjacent Pareto steps, all with exact
trade slope one Toffoli per qubit.

No sampled `windowed(blocks>1)` row adds a unique point to the global
single-exact-add frontier. `blocks=1` duplicates `topclean(k=0)`, and
`blocks=2` is already dominated at equal Q by a topclean point with two fewer
Toffolis for the even widths measured; every later block count is dominated by
`blocks=2` within the windowed family.

## Owner changes

Let `c=ceil(sqrt(n))`. The co-binder rival uses `clean_top=n-c`, producing:

```text
Q = max(3n + 2 - k, 2n + 2 + c)
T = 3n + k - c
```

The candidate owns the tied peak at `k=n-c`; the rival first owns it at
`k=n-c+1`. Observed transitions exactly match the law:

| n | owner transition |
|---:|---:|
| 8 | 5 -> 6 |
| 16 | 12 -> 13 |
| 32 | 26 -> 27 |
| 64 | 56 -> 57 |
| 96 | 86 -> 87 |
| 128 | 116 -> 117 |
| 256 | 240 -> 241 |

The documented 32-bit rows are Q 72 -> 72 and T 116 -> 117; the 64-bit rows
are Q 138 -> 138 and T 240 -> 241. The transitions are real resource/owner
changes, but all four named rows are labeled `validation=not-run` by the
current harness. The 47 default-run Q plateaus are exactly the post-threshold
co-binder transitions, `sum(c-1)` over the five default widths.

Each boundary series also changes owner at W 1 -> 2: at W=1 the repair ties
the persistent allocation, while W=2 makes the repair phase strictly larger.
Those ten boundary changes plus five co-binder changes account for all 15
default-run owner migrations. These are micro-harness owners, not promoted
full-circuit peak owners.

## Explicit resource laws

All non-window rows in the 8..128 archaeology grid and all 160 window rows in
the default grid were independently checked against these exact laws:

```text
lowq:
  Q = 2n + 2
  T = 2n

topclean, 0 <= k < n:
  Q = 3n + 2 - k
  T = n + k

boundary approximate, 1 <= W <= n:
  Q = 2n + W
  T = W - 1
  fault probability = 2^(-(W+1)) under the stated uniform-input model

boundary exact with retained entry carry:
  Q = 2n + W + 1
  T = W - 1

boundary exact whole chunk:
  Q = 3n + 1
  T = n - 1
```

For the windowed family, let `b` be block count and `E=n+1`:

```text
b = 1:
  Q = 3n + 2
  T = n

b = 2:
  Q = 2n + 4 + floor(E/2)
  T = n + floor(E/2)

b >= 3:
  Q = 3n + b + 2 - ceil(E/b)
  T = n + sum(floor(jE/b), j=1..b-1)
    = n(b+1)/2 + (gcd(E,b)-1)/2
```

`b=2` is the one large width drop. For `b>=3`, reverse prefix cleanup owns the
peak and Q thresholds occur exactly when `ceil(E/b)` changes. Cleanup T has
divisor discontinuities whenever `gcd(E,b)>1`. Within the sampled `b<=32`
range these occur at multiples sharing factors with 33 (n=32), 65 (n=64), and
129 (n=128); none occur for n=96 because 97 is prime. The full small grids
show the terminal cases directly: n=8,b=9 carries a +4 gcd correction and
n=16,b=17 a +8 correction.

## Lift-assessment counterexample

The 11 default lift rows reproduce, but their CV verdict is sample-set
sensitive and does not test validation status. Adding the requested n=8/16
full grids changes the result to 15 assessments and reclassifies the 0.25
boundary families from `transferable_linear_mechanism` (CV T/n 0.039) to
`constant_or_scale_specific` (CV T/n 0.199). The underlying law is nonetheless
exactly affine, `T=rn-1`; the changed label is a finite-size/CV artifact.

Likewise, 256-bit canonical topclean/co-binder rows enter default lift CVs even
though every 256-bit row is marked `resource-only-u256-result-limit`, and the
analyzer does not filter them. A lift verdict is therefore descriptive resource
evidence, not a correctness or promotion gate.
