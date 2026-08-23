# Q1274 compare19 source-exact predictor qualification

Status: **local source-exact qualification passed; fleet launch remains
closed.**  The inherited control and all five pre-registered fixtures matched
the trusted full evaluator exactly in classical count and failing-shot set,
with zero ancilla garbage.  This lane did not scan a nonce range, touch a
provider or host, or submit.

## Frozen target

- Circuit commit: `ad690caacb0cc7f718b4fdfe36955fec3da67639`
- Emitted operations: `12921014`
- Operation stream SHA-256:
  `28ed9f5d4e9eccf222aa12a28d6fbf311d6f1c76daa62984c63d42a3f8f63955`
- Inherited control nonce: `251000962439`
- Trusted full-evaluator control: `15/17/0`
- Predictor base: the proven compare19 C++ model in
  `/Users/olifreuler/ecdsa-ops/gpu-port-compare19-087cafa/src`.
- Allowed predictor change: only the hard expected operation count,
  `12926071 -> 12921014`, in a temporary local build.  The model arithmetic,
  schedule, round counts, corpus derivation, and fault predicate stay
  byte-for-byte unchanged.

## Pre-registered fresh fixtures

The fixtures were fixed before running the predictor or evaluator.  Derivation
input:

```text
q1274-compare19-fixture-v1:28ed9f5d4e9eccf222aa12a28d6fbf311d6f1c76daa62984c63d42a3f8f63955
```

Its SHA-256 is
`dca0d8f18c0910955050a5243502f4337b794c83f0b18a28e9710a77c054fea1`.
Each nonce is the next complete 48-bit digest chunk interpreted as an unsigned
integer:

| fixture | digest chunk | nonce |
|---|---|---:|
| fresh-0 | `dca0d8f18c09` | 242583392586761 |
| fresh-1 | `10955050a524` | 18233483633956 |
| fresh-2 | `3502f4337b79` | 58286803221369 |
| fresh-3 | `4c83f0b18a28` | 84129562593832 |
| fresh-4 | `e9710a77c054` | 256671716196436 |

## Pre-registered gates

1. Verify the target stream hash and `12921014` header count before every
   predictor/evaluator use.
2. Run the inherited control first.  Require predicted classical count `15`
   and exact equality between the predictor fault-shot set and the trusted
   full evaluator's classical mismatch set.
3. Run all five fresh fixtures through the predictor and the unchanged full
   9024-shot evaluator.  Require exact classical count and per-shot-set
   equality on every fixture and zero ancilla-garbage batches.
4. Prove the diagnostic predictor rejects both the prior compare19 stream
   (`12926071` ops) and the live Q1275 peak stream (`12953930` ops) with exit
   code `2` before deriving a corpus.
5. Record the target state digest plus model-source, predictor-binary,
   evaluator-source, evaluator-binary, and tail-patcher hashes.  Record
   whether divide-walk, divide-replay, multiply-walk, multiply-replay, and
   result/shell faults were exercised.
6. Keep Linux CPU/GPU 32-fixture parity and a deterministic `pred_cls=0`
   canary closed until separately proven.  This qualification cannot start a
   hunt by itself.

## Predictor identity and target state

The temporary arm64 predictor was compiled with Apple clang 17.0.0.  A direct
diff against the proven compare19 CPU source contains one changed token only:

```diff
-static const u64 PP_EXPECTED_OPS_PEAK1275 = 12926071ULL;
+static const u64 PP_EXPECTED_OPS_PEAK1275 = 12921014ULL;
```

The comment, model arithmetic, width schedule, round constants, host loader,
corpus derivation, and fault predicate were unchanged.  Source and binary
receipts:

| artifact | SHA-256 |
|---|---|
| proven `pp_model.h` and qualified copy | `d47f7c5229d5751d30df2fa7936b87fe0b303ae1ad3c6fb97e2fc4ef44ff223e` |
| proven `ppcpu.cpp` and qualified copy | `ad419d754ffa57871003411df0ed6bea0696949be256da5e38c905105477d886` |
| proven `pp_host.h` before count rebind | `5888f1afd2aee16802c41e64f892f7ed32498ac1a2c45808656bbd76b0702a13` |
| temporary `pp_host.h` after count rebind | `c368dba1ddeb03dd604e131fcfdf303fbfdfd6cf8e21346d83c493c7c10a7486` |
| temporary arm64 predictor | `aa897cd4c536baa576fe1a40df074dcc2dadd8c4834b28b3c29d032f470a6cb4` |

The target predictor state digest is `8d378405aee2b176`, using the same FNV-1a
definition as `ppgpu.cu`: checkpoint sponge, checkpoint byte count, protected
96-operation tail, and total operation count.  The temporary digest utility's
source and arm64 binary hashes were
`4c12780ffd081a9272847799c2e70778384b63326edbcd4f4faa7a6a34407a9d`
and `1c567160dd49eae545cf600514fe26439807a17f4448da3c66e78f5f925adf05`.

The ordinary trusted evaluator remained unmodified in the circuit worktree.
Its source SHA-256 is
`b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
the ordinary local release binary is
`1028675a9784aca35db33cc526c22457ba1f08bca1198a5596f8f6c58f0e21de`.
For set comparison, a temporary copy added only an environment-gated
`eprintln!("FAILSHOT {i}")` in the existing mismatch branch.  Its source and
binary hashes were
`b92fae87e6f8539133abc7d88ed0dbb1e6db08a29ca6e81c36de0f61cf766645`
and `b8b4efd599104567e5d644511ba021481c6f1698ebf15c8674d95dad0c5306b4`.
The temporary diagnostic reproduced the ordinary evaluator's inherited
summary byte-for-byte on stdout.  No evaluator decision or count changed.

The local tail patcher source SHA-256 is
`ffb1200e451a9a3b959b3287f25ad73c348598e9cef5b69824fad6f31bfe5853`;
the arm64 binary is
`651f2b01aca842431142be33271fc6d143da16a0ff4b7e2b965ad05e09d258e0`.
Patching the inherited nonce reproduced the frozen target stream byte for
byte before any fresh fixture was evaluated.

## Inherited control

The predictor reported:

```text
nonce 251000962439 pred_cls=15 walk_div=6 replay_div=2 walk_mul=7 replay_mul=0 result=0 shots=9024 first=525
```

The ordinary unchanged evaluator independently reproduced `15/17/0`.  The
temporary index diagnostic found exactly the same 15 classical failing shots
as the predictor:

```text
525 538 596 2028 2341 2431 3196 3760 5533 5582 6039 7134 7145 7329 7843
```

The predictor masks were `1,4,4,2,1,4,4,1,4,1,4,2,1,4,1`.  Both index files
hash to
`128091e1f9fcaa0969c1d91562771839151ca166d7ff9d754afae903d197a461`.

## Five-fixture full qualification

Every fixture ran through all 9024 shots.  `pred cls` equals `full cls` on
every row, the complete ordered failing-shot files are byte-identical, and
all six controls have zero ancilla-garbage batches.

| fixture | nonce | pred cls | full `cls/pha/anc` | cause counts `dw/dr/mw/mr/result` | index-set SHA-256 |
|---|---:|---:|---:|---:|---|
| fresh-0 | 242583392586761 | 17 | `17/19/0` | `5/1/8/3/0` | `eef6e1799953d9013e2c75d29685e3976f050d54653666e8d1af63ff757fcb62` |
| fresh-1 | 18233483633956 | 12 | `12/16/0` | `3/1/8/0/0` | `773a7b1d7d09a51ff6701be0c9babb103af11dde0c71824b845be9f5278e05a4` |
| fresh-2 | 58286803221369 | 14 | `14/19/0` | `3/0/10/1/0` | `b850304f4fd884a59b8db3fba8e668540a5d6ea6aedf6a1c97b2703f6a4b0882` |
| fresh-3 | 84129562593832 | 15 | `15/15/0` | `7/0/7/1/0` | `b470b31c0d8eafcc34fb06afbb365c654fbdb8504705159d69783f1b3a90df56` |
| fresh-4 | 256671716196436 | 10 | `10/13/0` | `3/1/5/1/0` | `0902436740c9ceff0c9384c7e71e089c5720c40b21562434a7645a0de43288ec` |

Exact ordered failing-shot sets:

```text
fresh-0: 773 908 925 1844 2102 2425 3478 3915 4424 4626 4743 4850 5728 6331 6532 7383 8271
fresh-1: 2908 3361 3389 4553 5073 5281 6146 7426 8028 8433 8572 9013
fresh-2: 660 1483 1502 2095 3734 3779 4886 5695 7303 7310 7436 7823 8349 8541
fresh-3: 722 1188 2034 2326 2558 2957 3378 3577 3759 3984 4391 4397 6273 6373 6778
fresh-4: 2418 2924 3219 3834 3943 4172 5543 7472 7823 8563
```

The compact five-row receipt hashed to
`d470db3495613078ca5eca2c7171886f8dc51cbeb8eac380ca32af90ada32996`.
Across the inherited control plus five fresh fixtures, the predictor classified
83 faults: 27 divide-walk, 5 divide-replay, 45 multiply-walk, 6
multiply-replay, and 0 result/shell.  Masks `1`, `2`, `4`, and `8` were all
exercised.  Mask `16` was not, so **not every modeled fault class is covered**
by this six-nonce set; result/shell coverage remains an explicit Linux parity
gate rather than being silently inferred.

## Wrong-stream rejection

The temporary predictor rejected both known neighboring streams before comb
construction or corpus derivation:

| rejected stream | operation count | SHA-256 | exit |
|---|---:|---|---:|
| prior Q1275 compare19 | 12926071 | `ae588d6227dddfe5bdb996ae55cd1137d2424fdb3c9ba87dcff30f8e45087ab2` | 2 |
| live Q1275 peak625 | 12953930 | `83b66b7ef8e5080924f96faa0970a625044eb9d1e58fa2f6a75d162a3bb850d8` | 2 |

This proves the requested count-bound wrong-stream cases.  It does not prove
same-count collision rejection.  A deployable build must enforce the frozen
`8d378405aee2b176` state digest, or an external exact SHA-256 check, in addition
to the operation count.

## Remaining readiness blockers

The model is locally source-exact for this stream, but no hunt may start until
both gates below close.

### Linux CPU/GPU 32-fixture parity

1. Freeze production Linux CPU and CUDA sources from the same qualified model;
   bind both to operation count `12921014` **and** state digest
   `8d378405aee2b176`.
2. Build and hash the Linux CPU binary plus GPU binaries for the intended
   architectures.  Require startup to print the target count/digest and exit
   `2` on both neighboring streams above.  Add a same-count corrupted-stream
   negative test so the digest guard is actually exercised.
3. Pre-register 32 deterministic nonces from the target operations hash.
   Compare the complete per-shot fault mask, not only `pred_cls`, between
   Linux CPU and GPU at both comb widths 8 and 16.  All 32 must match exactly.
4. Require the set to exercise masks `1`, `2`, `4`, `8`, and `16`.  If the
   deterministic 32 contain no mask `16`, document that coverage gap and add a
   separately pre-registered deterministic extension; do not hand-pick after
   seeing results.
5. Send at least the inherited control and five fresh fixtures above through
   the unchanged trusted Linux full evaluator.  Require the same counts and
   ordered classical sets recorded here, with ancilla zero.  Any disagreement
   quarantines the corresponding binary.

### Deterministic `pred_cls=0` canary

The canary rule is fixed but unexecuted.  Derivation input:

```text
q1274-compare19-pred0-canary-v1:dca0d8f18c0910955050a5243502f4337b794c83f0b18a28e9710a77c054fea1
```

Its SHA-256 is
`9273bc7d65abb3452deb78668eb8178ad89da82728334dc7080f605b3db3066c`.
The bounded ascending interval is
`[161025781228971,161025781491115)`, exactly 262144 nonces; the canary is the
first emitted `pred_cls=0`.  No alternate interval may be substituted if the
bound contains no survivor.

To close the gate, CPU and both GPU comb widths must select the same first
survivor.  The unchanged full 9024-shot evaluator must then report classical
zero, an empty classical failing-shot set, and ancilla zero.  Phase may be
nonzero for a predictor canary; only `0/0/0` would make it an island candidate.
The run was deliberately not started here.

## Verdict

The compare19 classical model is locally qualified for the exact
`ad690ca`/`28ed9f5...f63955` Q1274 stream.  The evidence authorizes building
the production Linux parity packet; it does not authorize a range scan,
provider deployment, or submission.
