# Frozen q775 one-gate defense artifact

Status: `HOLD / SOURCE-PROVEN / NONCE-UNQUALIFIED`  
Exact parent source: `67524171baaf568dc3dc606f38515745f70804ff`  
Branch: `research/q775-defense-6752417`  
Live closure refresh: source `6752417`, score `1154731130`.

## Frozen change

The ping-pong stream removes only operation 15,461:

`CCX(q513, q775 -> q776)`

The production guard fails closed unless all of these source-bound facts hold:

1. operation 14,686 is unconditional `R q775` at condition depth zero;
2. no operation in 14,687..15,460 computationally writes q775;
3. operation 15,461 is the exact unconditional CCX above at condition depth zero.

Because `R q775` demolishes q775 into `|0>`, the CCX is the identity. The
standalone verifier independently decompresses clean-parent and candidate
streams and proves the candidate is byte-for-byte the parent with exactly this
one record deleted, including the unchanged 96-operation nonce tail.

Verifier command:

```sh
.lane/verify_q775_witness.py /path/to/parent/ops.bin /path/to/candidate/ops.bin
```

Expected receipt:

```text
PASS baseline=12593858 candidate=12593857 reset=14686 cut=15461 q775_no_write=true deletion_only=true
```

## Identity binding

- parent operation count: `12,593,858`
- parent ops SHA-256:
  `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e`
- candidate operation count: `12,593,857`
- candidate ops SHA-256:
  `107b19628d6d709f2c9416948fd2721b2a84bc1874aff1913664b95fd89c2764`
- source-only diff SHA-256:
  `e6e6caf7d477ae076ee3ee117c1318323e77736364434cca3f20ebf1cb62cc07`
- patched `src/point_add/mod.rs` SHA-256:
  `5a0ddd6a33fa8e95b55f1606a1d6214f503c6dbcf3174054a21dcddc6c19a6f5`
- verifier SHA-256:
  `a8ca92bd23501db464110a380086e9e34794ab1bf26d8b44553592ad227c6dca`

## Current-nonce canonical evaluator receipt

The unchanged full evaluator completed all 9,024 shots:

- Q: `1267`
- average T: `911410.358`
- average Clifford: `10359311.247`
- emitted operations: `12,593,857`
- classical mismatches: `17`
- phase-garbage batches: `12`
- ancilla-garbage batches: `0`
- first classical mismatch: shot `632`

This is not a candidate. The changed operation-stream hash does not inherit the
promoted source's clean validation draw.

## Authority matrix

- provider authority: `false`
- nonce-grind authority: `false`
- protected-queue authority: `false`
- fleet-retarget authority: `false`
- submission authority: `false`
- public-note authority: `false`

No authority becomes true until all of the following close in a new controller
receipt: exact source-qualified prefilter parity, campaign authorization,
external lease gates, disjoint range ownership, and a full 9,024-shot candidate
receipt with classical/phase/ancilla `0/0/0` whose integer score strictly beats
fresh live SOTA.

Generated `ops.bin`, evaluator output, results rows, build logs, and score files
are evidence inputs only and must not be committed.
