# Q1273 predictor disjoint-corpus hold

Verdict: `HOLD_MODEL / NO_CUDA_HANDOFF`.

The original Q1273 CPU model is exact on the inherited stream and frozen H64,
but it is not globally exact. An independently frozen D16 corpus exposed one
predictor-only classical shot. The miss is localized to a scheduled-width
overflow whose signed register wrap happens to recover the correct circuit
output. A known generic wrapped-output fallback fixes that shot but erases a
different evaluator-real fault in the same blinded corpus. It is therefore not
a safe correction and was not committed to the production model.

No provider, GPU, range, hunt, submission, or CUDA compilation occurred. The
uncommitted CUDA handoff copy was discarded after the counterexample arrived.

## Evidence ordering and identities

The inherited plus H64 gate was frozen and pushed first at
`2d16b17f5e6b83b376ae4041fd94a2c42ba1f158`:

- inherited complete classical set: exact `1/1`;
- H64 complete classical sets: exact `64/64`;
- H64 evaluator/predictor faults: `870/870`;
- H64 classical/phase/ancilla totals: `870/696/0`;
- H64 fixture-ledger SHA-256:
  `7918937a30d562a2dd26cf59374cdb702c11ce0f08d42789f9ef42da8264b5f4`.

The later disjoint oracle corpus was frozen independently on branch
`research/fable-q1273-phase-port` at commit
`4e06616d549bb8d60a4009ffa64e2f84168621cf`. Its committed inherited-plus-D16
ledger SHA-256 is
`e148f24d99ae45b3c6930a33d49173fd31b2c236593d98375956077b3feb4d1b`.
The oracle is bound to the same Q1273 target:

- source commit: `093d85d64de87aa5006a94868172f642daacf136`;
- operation count: `12,933,805`;
- operation SHA-256:
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- Q1273 / 9,024 shots / zero ancilla batches on every fixture;
- two-pass oracle source SHA-256:
  `26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98`;
- two-pass oracle binary SHA-256:
  `90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402`;
- oracle operation-site ledger SHA-256:
  `ddce38817e1fccbf26f1f1ec0d000df28a18b2945b4ffd0a38b3cacbb69de6d5`.

The unchanged original predictor remains bound by source hashes
`7a7e477082c240278c36eabfca227b8266d638ae5ab30e5ac6ea2a7dd34f42bb`
(`pp_host.h`),
`8e97b9b94d313e05bbe7fb844a53381b17c9c3fbd027a744feb41edaa993976d`
(`pp_model.h`), and
`0fde4f34365e352b272e138d450d9321fff9a1366d38fbd7213dda35b58fa4a8`
(`ppcpu.cpp`). Its local binary SHA-256 is
`93a9d9be4e542388457d802dd0a0832c527bfe3803efd8158a2d66e626ecd63c`.

## Minimal counterexample

For nonce `730140001442`, the unchanged oracle reports 19 classical faults,
12 phase-fault shots, four clean-lane phase faults, and zero ancilla batches.
The complete classical set SHA-256 is
`fd7744b179e46d282ed9b4a22a8feb33cc6ff9ccf26ca86e52c09275678c6347`;
the full oracle row artifact SHA-256 is
`233c7b5333bd197d1985a7dd6582f438111b90eb5dd6c601552012568d0a51fb`.

The original predictor reports the same 19 shots plus shot `6329`, for 20
total. Its complete index-set SHA-256 is
`acfa410b8f687b0a3da4a2d3d1c56eeb247d8300f7a49e4457b058fddf58cacf`;
its cause-mask ledger SHA-256 is
`b4ab770cc46b111edab12e4c60083354b2449c0720b0498f5c2e5253fdbecb85`.
There are no evaluator-only shots and exactly one predictor-only shot: `6329`.

Shot `6329` is classified as mask 1, `PP_F_WALK_DIV`. Its denominator is
`de83caa0a4eb4e4932825c55e612d46165c8117a3859e4b339dcca7d8f2bf7ca`.
The mathematical walk first exceeds its scheduled register after round 602:

```text
fault=post round=602 schedule_round=607 width=44 target_width=45 u_width=43 v_width=45
```

The trace receipt SHA-256 is
`2741b7f128bfc877d052fe7c4bc97485a0fe7c0b5e00c5b5c40ca8309a55c926`.
The source-bound shot receipt SHA-256 is
`3cdcad04d2befe7cb3fe6ff5de740fd0a3fa613074b21b508250be85d9fd3f2c`.

The existing model treats every scheduled-width overflow as an immediate
classical fault. The circuit does not halt: `shrink_to` retains the scheduled
low bits, interprets the retained top bit as sign, and continues the remaining
walk, replay, and point-add shell. On this shot, that wrapped path returns the
correct affine output. This is the exact missing semantic channel.

## Why the available fallback is not shippable

A diagnostic-only port of the pre-existing Q1272 signed-truncation and
full-output fallback was tested without changing the committed model. The
diagnostic source and binary SHA-256 values are respectively
`4cd9d349096348e1b5bab87a59962618f0cc7d0131eea3bb0eb58e0fc8503b78`
and
`fa7817ae361ade38091307de78eaf36d9be81ab0f62329a674ff0da30f4061cf`.

It correctly changes nonce `730140001442` from 20 to 19 predicted faults and
shot `6329` from mask 1 to mask 0. It also preserves exact complete-set parity
on the inherited stream and all H64 streams (`65/65`); the H64 diagnostic
manifest SHA-256 is
`f983a7944416b4941835eadc354219363bb2c04f59d0236d4ea79a7c3fe746f3`.

It nevertheless fails the same D16 corpus on a different fixture. For nonce
`730070000721`, the unchanged evaluator and original model agree exactly on 21
classical faults, set SHA-256
`d9bfb2fc4f2b3cfdabede6d98df9ade6e9c25315b2a287b4a9e713854adb1e82`.
The oracle row artifact SHA-256 is
`2bc767c89b97cb294a218489f21f72924cd08d9902596bc965761d0fc5986d19`.
The generic fallback incorrectly removes evaluator-real shot `2493`, changing
it from original mask 4 (`PP_F_WALK_MUL`) to zero.

That true multiply overflow first appears before round 503:

```text
multiply fault=pre round=503 schedule_round=507 width=83 u_width=84 v_width=82
```

The trace receipt SHA-256 is
`8173874fef78781ed7e5e34da0c0b0dc0bb2c0e480c71a493d1f06735dfdaa64`.
The original model is `15/16` on D16 with the one false positive at shot 6329;
the generic fallback is also `15/16`, but with the one false negative at shot
2493. Their respective external D16 artifact-manifest SHA-256 values are
`bf8f73cd6570bcf1c6dc2eddcf227ba40f4f0fe5bc3b4877bc119e01a5bf9e41`
and
`f452acaaea475c0ab5b3f14ace572551b209807fcfbc411dba0af959204ad8c5`.

Thus neither `overflow => fault` nor `overflow => wrapped final-output check`
is exact for this source. The missing distinction lies inside the target's
wrapped walk/replay register semantics, including the lossy carry/fold state
that the Q1272 fallback does not preserve for this architecture.

## Terminal decision and next gate

`HOLD_MODEL`. Do not compile or qualify CUDA from this model, and do not use it
for a range, survivor filter, or density claim. The H64 PASS remains useful as
a regression corpus, not as deployment authority.

A successor lane must predeclare before editing, model the actual scheduled
signed truncation plus every lossy replay carry/fold state through the full
output, preserve both contrasting overflow shots above, and then pass inherited
plus H64 plus the now-public D16 as regressions. It must use a newly frozen,
disjoint holdout for qualification; none of the revealed fixtures can serve as
that holdout again.
