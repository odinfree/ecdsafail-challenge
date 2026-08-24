# J2-D5 CPU predictor parity diagnosis

Date: 2026-08-24
Lane owner: D5 diagnostic owner
Scope: one named nonce, local CPU, diagnosis only
Verdict: **COMPLETE**

## Decision

The predeclared falsifier did not fire. The predictor failure can be localized
without acquiring a new trusted fixture, and there is a finite, source-literal
repair specification that does not fit the named nonce.

The archived assessment's premise is false: nonce `1001537523329` is not clean
for the promoted `6752417` circuit. The archived CPU predictor reports 18
classical-fault shots. Exact Rust evaluation reports 21 classical mismatches,
9 phase-garbage batches, and 0 ancilla-garbage batches. Seventeen predicted
shots are true positives. The actual parity errors are one false positive,
shot 8471, and four false negatives, shots 574, 992, 1184, and 6437.

This is a diagnosis, not a repaired or qualified predictor. No predictor or
production source was changed. No nonce range was scanned. No GPU, provider,
network fetch, push, submission, or external-state action was used.

## Exact binding

### Predictor under diagnosis

- Commit: `68ce67aee5f00bbbef3f050d84f03ace483b269c`
- Tree: `1a504466f6e627447ae255cb68044e350a6ea24d`
- Parent: `67524171baaf568dc3dc606f38515745f70804ff`
- `ASSESSMENT.md` SHA-256:
  `35348731b6181a919d03d843de71cb2fc343ab8ba02ac86a1c0de73f7b37b6a6`
- `build.sh` SHA-256:
  `7598ef077ab15573f2f1ed0d216a84ed0788f3c59a33ae7ae00a30051a867094`
- `pp_model.h` SHA-256:
  `1c99a3fa3b9bcc63473ee068e82f80c24cd2add66a03ed28e7946717a373f5c0`
- `pp_host.h` SHA-256:
  `6cb74f949456ada20e577c29f635c01f915ec8fc9c89ffd67c261f6feed69dff`
- `ppcpu.cpp` SHA-256:
  `3081eab0b5e87bf48a0031527228466c955ad5b04fd5b80954cff00d067755e5`
- Local CPU binary SHA-256:
  `cc805d8be780ec084c2bd2fa3edd3567277dca7619a2d2a7b539eb77ca5746b6`

The exact diff from the bundled `da61-qualified` model to the
`6752417-assessment` model is only:

```diff
-#define PP_ROUNDS_MUL 696 // exact d919/da61 multiply depth
+#define PP_ROUNDS_MUL 697 // exact 6752417 multiply depth
```

The host guard changed only the expected op count/state digest and their label;
`ppcpu.cpp` is identical. Thus the assessment did not port the promoted
algorithm. It relabeled the old model, changed one wrong constant, and guarded
it against the new byte stream.

### Promoted source and literal evaluator

- Promoted source commit: `67524171baaf568dc3dc606f38515745f70804ff`
- Promoted source tree: `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- `src/point_add/mod.rs` SHA-256:
  `596ed58d4d61fbb087ccf236c728efc09631632a96693d849a71c03bea866a06`
- `src/point_add/pingpong_div.rs` SHA-256:
  `953dd851629e4d15a4f56d5061e3c0d61ea83bebab8f7aca5243636d4f240c38`
- `git diff --exit-code 67524171 68ce67ae -- src/point_add` exits 0: the
  promoted point-add source is unchanged in the predictor commit.
- Exact `68ce` `tail_patch.rs` SHA-256:
  `c5a5ff7700f93f52081e34bffc7e3bcf89ff5d6d9dded8e1c8c5faefb5088f6c`
- Exact `68ce` `eval_circuit.rs` SHA-256:
  `4b07377df5ba3a8fb1b261fbb4791341f40effb976e5e474e50d8ffddca93f35`
- Local release `tail_patch` binary SHA-256:
  `b9f020d6f95a0067b2503eb34956b069665aea491fd1a0b744e79f078eba9a0e`
- Local release `eval_circuit` binary SHA-256:
  `76551b52cba5e7ba2e29980931a7071321985021e19cde6dcfa91a8217e065c5`

The diagnostic per-shot Rust simulator used the same promoted `circuit.rs`,
`sim.rs`, and curve implementation. Their copy hashes exactly equal the blobs
at `67524171`:

| File | SHA-256 |
|---|---|
| `Cargo.toml` | `3c80178b08d29a158abb29a7dcb8eefc67c66f60f2c3bd14483b65eeca0740dc` |
| `Cargo.lock` | `42ff16919e551891ad1b21821329b116d133194245a0e0734a33573dfe598e07` |
| `src/circuit.rs` | `ac2255f6bcb6895c9da2dfe21c3a051a0ef8fc4e0af9598634fec0035dbf35c6` |
| `src/sim.rs` | `f0c72f2a280cd68acee1dbf8282098f72d6b3bf4311e0abf96d122fe002256d7` |
| `src/weierstrass_elliptic_curve.rs` | `ecfca15ee3b831c243fbea559ff4b8937be47fe591a4f14786ec2b9bfb30bded` |

Diagnostic-only, ignored harness bindings:

- `target/d5-predictor-68ce-20260824/d5_trace.cpp` SHA-256:
  `9216f7a52f4eddad3fd933942000614f818efa62283c784ce0fb62f4b888c5dd`
- `target/d5-predictor-68ce-20260824/d5_trace` SHA-256:
  `8a213f7ee1dab21c5a700b9d4d8b6d2b16d1d30efb5951b63b651d596f4bdfd9`
- `target/d5-source-sim-harness/src/main.rs` SHA-256:
  `58f1e0ba4291753608973869979ed241bd6ec61283fd1ae62f9cf78458c89fe6`
- `target/d5-source-sim-harness/target/release/d5_source_sim_harness`
  SHA-256:
  `0dbeb982e802e5fe517b896ba279777f83653ff8be7f86724fc75c4920b104cc`

### Ops, nonce, checkpoint, and environment

- Baseline ops: 12,593,858 records, SHA-256
  `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e`
- Predictor prefix state digest: `867497b860476be7`
- Baked nonce: `1001537523329`
- Tail-patched ops: 12,593,858 records, SHA-256
  `f36adbd063fa0ccafb03cdf044ed2cbd47c7a00e4271d18ccb3e9a1cf6c90204`
- Exact evaluator layout: 1,267 qubits, 952,914 classical bits
- Host: Apple M4 Max, arm64, Darwin 25.5.0
- Compiler: Apple clang 21.0.0; `rustc 1.93.0`; `cargo 1.93.0`
- Relevant ambient environment at capture: no `SUB4_*`, `TLM_*`, `PPF_*`,
  `PP_PROFILE`, `ECDSA_*`, or `CONSTPROP_*`; only `RUST_LOG=warn` matched the
  diagnostic filter. Final reproduction commands below use `env -i` and an
  explicit `PATH`.

The predictor consumes the baseline stream prefix plus the nonce argument. The
Rust evaluator consumes the tail-patched stream. The derived inputs agree
exactly at shots 0, 449, 574, and 8471, which is a direct checkpoint/corpus
parity control rather than an assumption based on the two file hashes.

The assessment binds only the baseline hash, not the baked stream hash or an
evaluator binary/output receipt. Its statement that a full evaluator found zero
mismatches is therefore neither artifact-bound nor reproducible from the
commit.

## Reproduction

Working directory for all relative commands unless a subshell says otherwise:

```text
/Users/odin/Documents/coding with codin/ecdsafail-smallwidth-redteam-codex
```

CPU predictor build and guards:

```bash
c++ -O3 -std=c++17 \
  target/d5-predictor-68ce-20260824/predictor/6752417-assessment/src/ppcpu.cpp \
  -o target/d5-predictor-68ce-20260824/ppcpu

shasum -a 256 \
  target/d5-predictor-68ce-20260824/ppcpu \
  target/redteam-baseline-ops/ops.bin \
  target/d5-baked-nonce-1001537523329/ops.bin

env -i PATH="$PATH" \
  PPF_OPS="$PWD/target/redteam-baseline-ops/ops.bin" \
  target/d5-predictor-68ce-20260824/ppcpu statedigest

env -i PATH="$PATH" \
  PPF_OPS="$PWD/target/redteam-baseline-ops/ops.bin" \
  target/d5-predictor-68ce-20260824/ppcpu breakdown 1001537523329

env -i PATH="$PATH" \
  PPF_OPS="$PWD/target/redteam-baseline-ops/ops.bin" \
  target/d5-predictor-68ce-20260824/ppcpu faultshots 1001537523329
```

Literal evaluator and exhaustive per-shot diagnostic:

```bash
(cd target/d5-baked-nonce-1001537523329 && \
  env -i PATH="$PATH" \
  ../d5-microgrind-source-68ce/target/release/eval_circuit \
  --note D5-final-verification)

env -i PATH="$PATH" \
  target/d5-source-sim-harness/target/release/d5_source_sim_harness \
  target/d5-baked-nonce-1001537523329/ops.bin all
```

The evaluator exits 1 as expected because the circuit is incorrect. It prints:

```text
loaded ops              : 12593858
qubits                   : 1267
tested shots             : 9024
classical mismatches     : 21
phase-garbage batches    : 9
ancilla-garbage batches  : 0
first mismatch           : shot 449
```

Per-shot causal traces:

```bash
for shot in 449 574 992 1184 6437 8471; do
  target/d5-predictor-68ce-20260824/d5_trace \
    target/redteam-baseline-ops/ops.bin 1001537523329 "$shot"
done

for shot in 0 449 574 8471; do
  target/d5-source-sim-harness/target/release/d5_source_sim_harness \
    target/d5-baked-nonce-1001537523329/ops.bin "$shot"
done
```

No ordinary `cargo test` result is used; this lane used dedicated binaries as
required by the handoff.

## Exact set comparison

Predictor output:

```text
pred_cls=18 walk_div=8 replay_div=0 walk_mul=9 replay_mul=1 result=0
first=449 shots=9024
```

| Set | Shot indices |
|---|---|
| Predicted 18 | `449, 860, 1174, 1249, 1352, 2274, 2352, 5392, 5453, 5624, 5981, 5993, 6834, 7057, 7099, 7224, 8471, 8772` |
| Actual value-fault 21 | `449, 574, 860, 992, 1174, 1184, 1249, 1352, 2274, 2352, 5392, 5453, 5624, 5981, 5993, 6437, 6834, 7057, 7099, 7224, 8772` |
| Intersection 17 | `449, 860, 1174, 1249, 1352, 2274, 2352, 5392, 5453, 5624, 5981, 5993, 6834, 7057, 7099, 7224, 8772` |
| False positive | `8471` |
| False negatives | `574, 992, 1184, 6437` |

The nine exact phase-garbage batches are:

| Batch | Shot range | Live phase mask | Dirty shots |
|---:|---:|---:|---:|
| 7 | 448-511 | `0x0000000000000002` | `449` |
| 18 | 1152-1215 | `0x0000000000400000` | `1174` |
| 19 | 1216-1279 | `0x0000000200000000` | `1249` |
| 26 | 1664-1727 | `0x0000000400000000` | `1698` |
| 77 | 4928-4991 | `0x8000000000000000` | `4991` |
| 92 | 5888-5951 | `0x0040000000000000` | `5942` |
| 93 | 5952-6015 | `0x0000020020000000` | `5981, 5993` |
| 106 | 6784-6847 | `0x0004000000000000` | `6834` |
| 110 | 7040-7103 | `0x0800000000020000` | `7057, 7099` |

All 141 batches are ancilla-clean after clearing the four ABI registers.

## Causal witnesses

### Shot 449: smallest prediction is a true source fault

Inputs:

```text
tx=4886ad02767db1ed7e727cf7cb632f26340874bbde39d5987aec9acc8223b421
ty=552ef662907f1bf4c3f4860597ee3942632b59a9feba6e18f8de08affb66d09f
ox=2930f2fbf27add9499647b125fe96ac1ae3e2309e31f03dfdac95ef18bc29c13
oy=7538d038c117a1b35dc3ac0c317b2cc041f9b6653d99c56dcb1776a6d0984456
```

Predictor and promoted-source surrogates match through coordinate subtraction,
divide replay/restore, add-3x, and square:

```text
x2     =1f55ba068402d458e50e01e56b79c46485ca51b1fb1ad1b8a0233bdaf661180e
y2     =dff62629cf677a416630d9f966730c822131a344c120a8ab2dc692082ace8878
y_div  =78d114c90ab2ba01df5b4cef1357356f6c6e40d1f8174dd7691bf4d4f9144d7e
a_mul  =48d0ac00722a372c96ccd28f4fe9868c0da40804784b06b3af60fb3f46cacdf9
```

The promoted multiply walk itself exceeds its scheduled width at post-add
round 116: target signed width 228 versus scheduled width 227. Thus source and
predictor both correctly enter their wrapped fault routes and both classify the
shot as `WALK_MUL`.

The first *internal parity divergence* is later, at multiply round 118, sampled
schedule index 119. The active source repair gives width 227; the predictor's
raw table gives 226. The sign bit remains 1 and `u` remains equal, but `v`
acquires opposite signed extension after truncation:

```text
source_width=227 predictor_width=226 source_sign=1 predictor_sign=1
source_v   =fffffffffffffffffffffffe1633fb8720b9f1457576fbf100b510e8b688f434f8d49bd77b290505
predictor_v=0000000000000000000000001633fb8720b9f1457576fbf100b510e8b688f434f8d49bd77b290505
```

That divergence changes the wrong wrapped result but not the verdict:

```text
promoted y_mul =1b11f8b4037a0beef56c2fd68660c8358b8780ee20aea26c31fc8a7599c92a93
promoted got_x =e06046fb8050a6680297a8830fffe435a09a1b056ad3fd2c2b6863b144f7ca49
promoted got_y =a5d9287b42626a3b97a883ca54e59b75498dca88e314dcfe66e513cdc930e26c
expected_x     =e06046fb8050a6680297a8830fffe435a09a1b056ad3fd2c2b6863b144f7ca49
expected_y     =baae28073800214b7b4e429e6e406613a890d3831fe9835b0b2ef0fc5455033b
```

Shot 449 is also phase-dirty (batch 7, mask bit 1) and ancilla-clean. It is a
true source fault, not a false positive. The assessment's claimed first
counterexample disappears only because its trusted label was wrong.

### Shot 8471: sole false positive, missing active `WIDTH_REPAIR`

The predictor returns mask 1 (`WALK_DIV`). The promoted source is value-correct
and ancilla-clean. The first raw table difference is round 18/sample 18, but it
is not load-bearing. The first load-bearing divergence is the divide post-add
at round 352, sampled index 356:

```text
field=v old_width=140 source_width=141 target_signed_width=141
source_post_add             =0000000000000000000000000000000000000000000009888dc3502abd5162e2777cbf5bb41e173e
predictor_post_add_truncated=fffffffffffffffffffffffffffffffffffffffffffff9888dc3502abd5162e2777cbf5bb41e173e
source_post_shift           =0000000000000000000000000000000000000000000004c446e1a8155ea8b1713bbe5fadda0f0b9f
predictor_post_shift        =fffffffffffffffffffffffffffffffffffffffffffffcc446e1a8155ea8b1713bbe5fadda0f0b9f
```

At the fast classifier seam the source continues while the predictor flags an
overflow. The latter two values are the predictor's wrapped-fallback state.
The repaired source reaches `u=-1,v=+1`, restores
`y_div=b736562f8eed27209321342ce1d01b6457ea1a7694a78cb7ddbadab85e877a93`,
and returns the reference result:

```text
x=c50f5532b1b4427413bf8755ab90952a017d53f91a9faca58de8169133b75cc3
y=56b374583bb443ab41ee64cb66e12a1e410b5489f3d8541ac5b1a53a4ae8f6d5
```

Source binding: index 356 is present in `WIDTH_REPAIR` at promoted
`src/point_add/pingpong_div.rs:585-592`; the repair is default-active at
`:594-602` and applied to the table at `:613-617`. The predictor's
`pp_value_width_t` at archived `pp_model.h:568-575` reads only the raw table.

### Shot 574: earliest false negative, wrong multiply depth

Predictor and source match through the multiply input:

```text
y_div=d63fb872cee3d57c4a7fcbec0e9b1df6229e93877e074d2b94c8299a0c22522b
a_mul=ddc42922faa341947cefc88bdad7f218b5c64246ceea9fb710f41f104cdc6934
```

The first divergence is the loop bound at round 694. The promoted source has
finished rounds 0-693 and stops with `u=3,v=-1`; `u` is not plus/minus one, so
the source flags `WALK_MUL`. The predictor incorrectly executes rounds
694-696 and reaches `u=1,v=1`, so it calls the traversal clean.

```text
source rounds=694:    u=+3  v=-1  u_pm1=0 v_pm1=1
predictor rounds=697: u=+1  v=+1  u_pm1=1 v_pm1=1
```

The literal Rust result is in fact wrong:

```text
got_x=4f84cf63e1f11b4f27d8a5c2cdcddb770d1ab41914cd0ac9e74969464a93bc24
got_y=de7ded8a3e40f2fae395902cd1bc89795693f95470ee4a57a69c84de58d40260
exp_x=e794807e6dbf142cf515b6f9ca40a160edd1e34802a0bc85097dd1b4319586d7
exp_y=de90a8254255058a25f4f7a984dea66b21ea0c7a64c3047a632a396fec9a2072
```

All four false negatives have the same root:

| Shot | Source terminal after 694 | Predictor terminal after 697 |
|---:|---|---|
| 574 | `u=+3, v=-1` | `u=+1, v=+1` |
| 992 | `u=+1, v=-3` | `u=+1, v=-1` |
| 1184 | `u=-1, v=-3` | `u=-1, v=-1` |
| 6437 | `u=-3, v=-1` | `u=-1, v=+1` |

Source binding: the executable default is
`set_default_env("SUB4_PP_ROUNDS_MUL", "694")` at promoted
`src/point_add/mod.rs:2468`; the predictor hard-codes 697 at archived
`pp_model.h:523`. Promoted `mod.rs:2579-2580` still says “M697” in a comment,
contradicting the executable default. That stale prose is a plausible direct
source of the assessment's wrong constant and must not govern a model port.

## Complete obvious-staleness audit

The two causal defects above are sufficient to localize the observed parity
errors. They are not the only stale assumptions. The following finite list is
source-derived; entries marked “not isolated” were not independently proven to
change this nonce's shot set and must not be described as causal from this
evidence alone.

| Mechanism | Archived predictor | Promoted source | Status |
|---|---|---|---|
| Traversal depths | DIV 696, MUL 697 (`pp_model.h:522-523`) | DIV 696, MUL 694 (`mod.rs:2464,2468`) | Causal for four false negatives |
| Width schedule | Raw rescaled table only (`pp_model.h:568-575`) | Same table plus default-active 100-index `WIDTH_REPAIR` (`pingpong_div.rs:585-617`) | Causal for false positive 8471 and shot-449 internal divergence |
| Divide frame | Always enters d919 signed frame (`pp_model.h:1001-1074`) | Build forces canonical frame with `SUB4_PP_SIGNED_FRAME=0` (`mod.rs:2483`) | Source-proven stale; not causal on the isolated witnesses |
| Fold window | One 54-bit `pp_fold54` for divide and multiply (`pp_model.h:894-975,1087-1100`) | Divide 54, multiply 53 (`mod.rs:2476-2477`; `pingpong_div.rs:166-173,2684-2687`) | Source-proven stale; not independently isolated on this nonce |
| Per-direction interleave | No literal direction-specific plan/HMR schedule | `R1=335`, `R1_MUL=315`, `R2=645`, `PEAK=WALK_PEAK=1267`, replay chunk 96, compare 22 (`mod.rs:2469-2475`; plan at `pingpong_div.rs:1805-1817`) | Required for op/HMR parity; value-only classifier may be invariant |
| Split walk terminal | Retained old carry-chain abstraction | Direct final high carry and shortened phase comparator (`pingpong_div.rs:1189-1291`) | Required for literal HMR parity; value causality not isolated |
| Unsplit walk terminal | Retained old final carry wire | Merged/direct terminal writes carry into top output (`pingpong_div.rs:1344-1414`) | Required for literal HMR parity; value causality not isolated |
| Fused fold terminal | Retained operand/final carry model | Direct terminal carry, no retained final wire (`pingpong_div.rs:2225-2318`) | Required for literal HMR parity; value causality not isolated |
| Shell source | da61 coordinate/square/final-shell port copied wholesale | Later promoted arith/comparator/product-register stream | Checkpoint values match at shots 449, 574, and 8471 through their first recurrence divergence; full source-literal re-port still required |
| Artifact guard | Op count plus state digest | Semantic behavior encoded only indirectly in ops bytes | Guard accepts a stale model; needs a model-config/source digest |
| Phase verdict | No exact HMR phase classifier | Exact evaluator finds 9 dirty batches | Cannot call a nonce clean without a phase gate |

The assessment correctly suspected merged/direct terminal changes, but it
stopped at that broad hypothesis. The first actual parity defects are earlier
and simpler: an omitted active table repair and a wrong executable round count.

## Finite source-literal repair specification

This is an implementable checklist, not an implementation or a claim that the
result will pass held-out qualification.

1. Generate a model manifest from exact commit/tree `67524171/8202910d`, not
   from comments. It must include hashes of `mod.rs`, `pingpong_div.rs`, the
   shell files, the baseline ops, and the generated predictor constants.
2. Set direction-specific depths to DIV 696 and MUL 694. Treat a source comment
   that says M697 as stale when it conflicts with the executed `set_default_env`.
3. Apply the exact rescale `round * 703 / 695`, then add one at every one of the
   100 `WIDTH_REPAIR` sampled indices when the source's default conditions hold.
   Stage the repaired table identically for CPU and CUDA; do not patch witness
   indices ad hoc.
4. Select canonical divide replay because `SUB4_PP_SIGNED_FRAME=0`. Retain the
   signed-frame code only behind a manifest-selected variant.
5. Split pseudo-Mersenne fold configuration by direction: 54 for divide, 53
   for multiply, with endpoint window 26. Port round 0, round 1, and fused
   multiply replay through the multiply-specific target.
6. Port the exact per-direction interleave/phase geometry: R1 335, R1_MUL 315,
   R2 645, peak/walk peak 1267, chunk 96, chunk compare 22, and flag compare 22.
7. Port the split, unsplit, and fused-fold direct terminal stages literally,
   including every HMR/CZ dependency and the shortened comparator phase
   polynomial. Do not infer phase equivalence from equal checkpoint values.
8. Keep the current coordinate/square/final-shell model only where a
   differential miter proves it equal to the promoted source. Otherwise port
   the promoted shell literally.
9. Emit separate value, phase, and ancilla verdicts. Until exact HMR phase is
   modeled, fail closed instead of labeling a nonce clean.
10. Make the runtime guard verify the semantic manifest/config digest in
    addition to op count, prefix state digest, and ops SHA-256. A correct ops
    hash does not prove that hard-coded model semantics match those bytes.

Nothing in this checklist depends on the values of shots 449, 574, or 8471.
Those shots are regressions; the repair choices come directly from the source.

## Frozen fixture plan

### Known fixtures

Freeze one manifest for nonce `1001537523329` containing:

- source commit/tree, both ops hashes, evaluator source/binary hashes, toolchain,
  nonce, ordered 9,024-shot inputs, and phase batch geometry;
- the exact 21 value-fault indices and nine phase masks above;
- shot 0 as a baseline control: predictor mask 0, exact final value equals the
  reference, `phase & 1 == 0`, no dirty ancilla;
- shot 449 as the true-positive wrapped-MUL/phase witness;
- shot 8471 as the `WIDTH_REPAIR` false-positive witness;
- shots 574/992/1184/6437 as the MUL-depth false-negative witnesses;
- checkpoint values at coordinate subtract, divide walk/replay/walkback/restore,
  add-3x, square, multiply walk/replay/walkback/restore, final y-sub, final
  reverse-sub, and nonce tail.

Acceptance on the known set requires exact equality of value-fault indices,
phase masks, ancilla verdicts, cause masks, and selected checkpoint states. A
mere total count match fails.

### Held-out fixtures

Before implementation, an independent evaluator owner should deterministically
derive and seal eight nonce values from a domain-separated SHAKE256 stream over
`J2-D5-heldout-v1 || source_commit || source_tree || baseline_ops_sha`. This is
fixture selection, not predictor-guided scanning. The owner should bake each
tail, record its ops hash, run all 9,024 exact shots, and commit a hash
commitment to the ordered truth manifests while withholding four manifests
from the implementer.

After the repair is frozen:

- reveal the four held-out manifests;
- require exact shot-index/cause-mask parity, exact phase-mask parity, and zero
  disagreement on ancilla cleanup for all 36,096 held-out shots;
- require intermediate parity on at least one clean and one faulting shot per
  held-out nonce;
- only then run CPU/CUDA predictor parity as a distinct gate.

No held-out nonce was generated or evaluated in D5, and no CUDA result is
claimed here.

## Next independent gate

Open one implementation owner on a new isolated branch to apply the finite
source-literal checklist. A separate verification owner should hold the sealed
fixtures and run the known/blind parity gate after the implementation commit is
frozen. Provider, scanning, push, and submission remain closed.
