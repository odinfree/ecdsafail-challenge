# Lane state — Q1272 hard-channel re-descent

Date: 2026-08-23 (Europe/Zurich)

## Decision

The first bounded Burn-the-House-Down re-descent found a useful composition but
did not promote it. Replay fold `54 -> 55` alone binds at Q1273. Contracting the
existing replay peak allowance does not remove that fold-local wire. Replacing
the multiply replay's materialized `plus_2f` selector by the exact XOR of its
already-live factors restores Q1272 and keeps full T below the hard ceiling.

The composed stream reduces replay faults sharply on the frozen H block, but
it introduces one exact final-result failure and exposed three false negatives
in the first scratch predictor. That breaches the predeclared no-new-result
gate and blocks any search use. The protected fold54/alias-off source defaults
remain unchanged. The exact selector alias and its selfcheck are retained as an
opt-in structural component for a later result-channel composition.

No nonce search, remote/provider action, spend, submission, or mutation of
another worktree occurred.

## Source and switches

- isolated branch: `research/q1272-hard-channel-redescent`
- exact starting source: `091abce0c0ac73f5e1965034fa976fa14c855594`
- default/reproduction stream: fold54, multiply selector alias off
- held E-001c stream:
  `SUB4_PP_REPLAY_FOLD_WINDOW=55 SUB4_PP_MUL_PLUS2F_ALIAS=1`
- exhaustive selector identity gate:
  `SUB4_PP_MUL_PLUS2F_ALIAS_SELFTEST=1`

The alias implements
`plus_2f = routed XOR minus_f`, with `minus_f = routed AND sign`, as two
existing CX factors. The fold consumes the selector only through linear CX
toggles. No selector qubit is allocated, measured, or freed on the alias path.

## Structural saddle ledger

All diagnostic runs used the predeclared `PP_PROFILE_SEED=hard-fold-55` so T
comparisons use the same 64-lane diagnostic seed.

| experiment | operations | ops SHA-256 | Q | diagnostic T | gate |
|---|---:|---|---:|---:|---|
| protected base, fold54 | 12,901,167 | `ecc3d9f0bb1dd4e68e6d337e39c4cdb66cfbfe83928a81fec28e22797fca4cfd` | 1272 | 914777.30 | `0/0/0` |
| E-001 fold55 | 12,923,378 | `f3915652770187b4200ac6bf424ee3034b54e859b06717bf912fef562f72ed00` | 1273 | 916106.31 | killed on Q |
| E-001b fold55 + peak1271 | 12,945,334 | `65d7cb17bb9ede12e28f2d1a354b003a79a7b47ebc1ebb80cca2a8b9b4741d90` | 1273 | 917028.50 | killed on Q |
| E-001c fold55 + selector alias | 12,939,336 | `d4ecab6dd80d044d0a28ae456a9106992d2b3aae070d80cfa0dde3d24400f920` | 1272 | 916117.12 | `0/0/0`; density gate held |

E-001c's diagnostic delta is +1339.82 T against the same-seed base. Its four
Q1272 co-binders are:

| phase | peak Q | diagnostic T |
|---|---:|---:|
| divide replay | 1272 | 263184.47 |
| product-register square | 1272 | 58720.72 |
| multiply replay | 1272 | 24273.28 |
| multiply walkback | 1272 | 308320.66 |

## Exact H64 result

The complete predeclared H block is the 64 nonces
`444000000000..444000000063`. Both streams ran all 64 through the unchanged
full 9024-shot simulator with early abort disabled: 577,536 shots per stream.

| stream | classical | lambda/classical | phase batches | lambda/phase | ancilla | exact average T |
|---|---:|---:|---:|---:|---:|---:|
| fold54 base | 1135 | 17.734375 | 839 | 13.109375 | 0 | 914793.939537968 |
| E-001c | 1054 | 16.468750 | 765 | 11.953125 | 0 | 916182.965865331 |
| delta | -81 | -1.265625 | -74 | -1.156250 | 0 | +1389.026327363 |

This is a 7.14% classical-count reduction and an 8.82% phase-batch reduction
on H. Rounded candidate T is 916183, below the hard ceiling 921139 by 4956.
At Q1272 the hypothetical clean score would be 1,165,384,776, 6,304,524 below
the pinned reference score 1,171,689,300. The stream is dirty, so this is only
an economic bound.

The same numeric nonces derive different SHA-bound shots on the two streams.
These are full ensemble measurements, not paired-shot causal estimates.

## Exact cause census and predictor boundary

The qualified fold54 model matched all 64 full-simulator classical counts and
classified its 1135 faults as:

```text
walk_div=509 replay_div=71 walk_mul=500 replay_mul=55 result=0
```

The first fold55 patch predicted only 1051 faults and missed one full-simulator
fault in each of nonces `444000000009`, `444000000010`, and `444000000025`.
The gap was not the selector identity. Fold55 exposed an irreversible
pre-truncation width POP during reverse walkback; the inherited wrapped-output
rescue propagated replay and shell values but did not model the lost walkback
bit. A scratch-only fail-closed correction matched all 64 exact counts and
classified E-001c as:

```text
walk_div=502 replay_div=32 walk_mul=486 replay_mul=33 result=1
```

Replay therefore fell from 126 to 65 faults, a 48.41% reduction. However, the
new result fault is real: nonce `444000000032`, shot 7997 is present in the
unchanged simulator's exact mismatch set. That fails the predeclared gate.

The scratch correction is evidence, not a production predictor. Its fixed
`pp_model.h` SHA-256 is
`5b5bddc05cd92ffff4102fb90fd1dc3ec18daf78bfc59423c0371ae8f1d34ddc`.
No scan may use E-001c until a stream-bound model passes the full independent
qualification suite; this lane starts no such qualification.

## Exact P16 and inherited gates

The predeclared P block is `444000000000..444000000015`, all sixteen complete
9024-shot simulations per stream.

| stream | classical | phase batches | ancilla | exact aggregate T |
|---|---:|---:|---:|---:|
| fold54 base | 254 | 189 | 0 | 914793.968653036 |
| E-001c | 258 | 179 | 0 | 916180.733252992 |

The smaller P block is statistically flat on classical output and lower by ten
phase batches. H is the powered decision block.

The unchanged evaluator on E-001c's inherited nonce `251000962439` reported
`14/14/0` and exact average T 916180.201. It is not a candidate. Focused gates
on the held stream passed:

- selector Boolean miter: 8/8 states;
- product-register square: 58,980 emitted / 58,721.141 executed T, Q1272;
- full pingpong affine-add selftest: 957,402 emitted / 916,093.578 executed T,
  Q1272;
- both focused processes exited 0; `git diff --check` passed.

## Artifact receipts

Generated evidence remains outside Git.

| receipt | SHA-256 |
|---|---|
| base H64 full TSV | `7897379ef24d73e04310c72f12cfd0f4b1cb5f6147f80d8c1b86ab4722b6fbad` |
| E-001c H64 full TSV | `d08f40bc4a88a2038ff9f37def52b3288fe87f232f2d274c92bea1a20780b80f` |
| base P16 full TSV | `87382f73feb8a7cfb11393845e6f5237800367eaef1a69b6f3b1fc5b17069c80` |
| E-001c P16 full TSV | `0d3958364c0759e41287830806cc910fd259dd53d3a1c48453c94c197ddb0082` |
| candidate profile | `8d4c0661e74c0d0d81f5cff574aefeda20f88995e3d2975b0639abf1fd7b21e9` |

The final rebuilt candidate profile reproduces the same operations, SHA, Q,
T, and `0/0/0`. Temporary evaluators, predictor sources/binaries, ops streams,
logs, and generated result rows are not committed.

## Reproduction and next falsifier

Default source rebuilt the protected 12,901,167-op SHA `ecc3d9f0...`. The full
promoted-route override vector, with fold54 and alias off, rebuilt SHA
`d9737f5154cf1159d1115f5057dcc8019b42984507f4e0cbeacd80edaee0b124`.

The single next structural action is to isolate E-001c's exact result fault at
nonce `444000000032`, shot 7997 across square versus final coordinate shell.
Only if that attribution names a bounded repair should E-004 widen the square
low window or a terminal/result cell. Any composition must retain Q1272,
rounded full T at or below 921139, exact base/live reproduction, and a fresh
no-new-result H gate. Do not grind the held stream.

## E-004 terminal update

The exact fixed-shot probe completed the declared isolation. On held SHA
`d4ecab6d...`, nonce `444000000032` shot 7997 and adjacent control 7996 were
both exact through add3x, product-register square, and multiply restore. The
control stayed exact through the complete circuit. Shot 7997 first diverged at
the final y-subtract by exactly `+2^53`; x, phase, and ancilla remained exact.
This rules out square, multiply, and rsub for the observed result event.

The only admitted repair, final-y `LSBS 53 -> 54`, emitted 12,939,341 ops at
SHA `d45a4a5ce7e02fe9ab708c05929d27bb0ce55885233e688e9fa093aac8b0c441`
and Q1272. On the original pinned input it moved the error to exactly `+2^54`
instead of clearing it, while the control stayed exact. R1 therefore failed its
first gate. It was removed without profiling T or running selftests, inherited
full, or H64; those stages were conditionally authorized only after the fixed
shot passed.

Clean source again reproduces protected default SHA `ecc3d9f0...`, promoted
fixture SHA `d9737f51...`, and held SHA `d4ecab6d...`. No generated probe,
binary, ops stream, log, or result row is retained in Git. E-001c remains a
held structural component, not a predictor or hunt stream. A future turn must
predeclare a real boundary-carry representation; further window shifting is a
measured anti-lever.

## E-006 boundary-borrow terminal update

E-006 represented the missing state explicitly rather than shifting its
boundary: one borrow qubit crossed low53 into an exact controlled decrement of
the high203 suffix and was then erased from a corrected low copy. Its static
price bound was final-phase Q1186 and incremental T930.

The only implementation fixed both original E-004 inputs exactly. Candidate
SHA `760e6d76504a8f444c0945af3903f6f4be0ccc6beaced9b061a108f35f1c78b2`
had 12,942,597 ops and Q1272. Same-seed diagnostic T was 916996.73 with
classical/phase/dirty `0/0/0`; final-y peak stayed Q1026. The actual diagnostic
price was +879.61 T.

The focused 64-lane reversible miter then failed with phase mask `0x2c` on
lanes 2, 3, and 5. It aborted before full value/ancilla assertions, so no wider
correctness claim survives. The candidate and all temporary harness code were
removed immediately; inherited full and H64 did not run. The explicit borrow
repairs the observed value fault but this micro-composition is phase-dirty on
frozen corner cases and remains killed. Any later phase-clean construction
requires a new predeclaration rather than an amendment to E-006.

## E-007 post-low predicate terminal update

E-007 used the phase-clean alternative from independently pushed commit
`ff1387d`: compute the missing borrow directly from the post-low result as
`anc && (z_low >= 0x1ffffefffffc2f)`, decrement the complete 203-bit high
suffix, then recompute the unchanged predicate to erase the one borrow qubit.
No E-006 capture/restore erasure code was reused.

The fixed 7996/7997 gate and all 13 adversarial primitive lanes passed exact
value, phase, and ancilla checks. Candidate SHA `4618d4af...9f37` has
12,943,345 operations, Q1272, same-seed diagnostic T918043.41 with `0/0/0`,
and final-y Q1026. Exact inherited full T is 918104.700; the unchanged full
evaluator reported `11/12/0`, improving held aggregate `14/14/0`.

The predeclared numeric mismatch-set subset gate failed because the candidate's
11 SHA-bound mismatch indices and the held stream's 14 indices were disjoint.
The changed operation SHA also changes the Fiat-Shamir inputs, so this does not
attribute causal regressions to the repair. It does trigger the frozen stop:
H64, hunting, providers, spending, and submission did not run. The exact
phase-clean repair is retained behind
`TLM_FINAL_Y_SUB_BOUNDARY_CARRY=1` as a held structural component only.

Post-clean reproduction again matched default `ecc3d9f0...4cfd`, promoted
`d9737f51...b124`, candidate `4618d4af...9f37`, and held
`d4ecab6d...f920`. Temporary evaluator instrumentation and generated rows were
removed.

## E-008 causal H64 terminal update

Correction commit `8ddebcf` froze an independent-ensemble three-sigma
non-inferiority rule before any candidate or unchanged full-evaluator H64
measurement. Inherited E-007 reproduced Q1272/T918104.700, `11/12/0`, first
2582 and passed its frozen gate.

Both 64-nonce blocks then completed unchanged 9024-shot evaluation. Held was
`1054/765/0`; E-007 was `1053/776/0`. Candidate lambda is 16.453125 classical
and 12.125 phase, every nonce has ancilla zero, and both streams have zero clean
nonces. Candidate first-failure q10/q50 is 27/353 versus held 50/329. E-007
passes the 1192/883 non-inferiority ceilings but is not strictly superior
because phase is 11 higher and q10 is earlier.

Exact candidate H64 T is `530243544084/577536`, or 918113.406062999, at
Q1272. A temporary trusted-evaluator print hook compared every complete
classical set with the source-bound classifier from `c3dea71c`: 64/64 sets and
1053/1053 faults matched. Causes are `531/30/467/24/1` for
walk-div/replay-div/walk-mul/replay-mul/result, with no unclassified masks or
new vocabulary. The one result event is nonce `444000000042`, shot 3036.

Terminal verdict is `PASS_NONINFERIOR; NOT_STRICT_SUPERIOR; HELD_DIRTY`.
No scan, hunt, provider, remote, spend, or submission action ran. Trusted
evaluator source and tracked results were restored to SHA-256 `b35314bc...90b`
and `eea84022...810`; generated artifacts remain outside Git. The next single
structural action is fixed-shot E-009 localization of candidate shot 3036
across the final coordinate shell.

## E-009 square-boundary terminal update

The exact tail42 stream reproduced 12,943,345 operations, SHA
`89d26f325df66ba0ebd9ec327895ccb537a918f0c7b0d34d9c8002a094f9d968`,
and Q1272. Condition depth was zero at every frozen phase cut. Adjacent control
3035 stayed exact with phase/dirty `0/0` throughout. Target 3036 was exact
through add3x, then first diverged after the product-register square by exactly
`+2^56` in x while y, phase, and dirty state remained exact/clean.

An independent integer replay matched the observed square output and isolates
the lost carry to the ninth and final `mod_add_top`: the C-half subtraction.
Its overflow-controlled `+f` crosses the low56 boundary; none of the first
eight top reductions does. Multiply and the final coordinate shell only
propagate this error. No source repair ran during localization. Temporary
instrumentation was removed and protected evaluator/results hashes reproduce.

The next bounded experiment, if admitted, is a separately predeclared one-site
C-half 56-to-57 window falsifier followed immediately by an adversarial
boundary miter. The pinned event has bit56 zero and should become exact, but a
general carry can recur at bit57; failure of that exactness gate kills the
width shift without another adaptive width.

## E-010 one-site width terminal update

The only admitted C-half LSBS56-to-57 implementation fixed original E-009
control 3035 and target 3036 exactly in the 64-lane product-square selfcheck.
That focused circuit stayed Q1272 and cost only `+3` emitted / `+1.671`
executed T. Value, phase, and ancilla all passed on that gate.

The frozen adversarial top-reduction miter then failed: the two cases at
`2^57-f` and `2^57-f+1` were each wrong by exactly `+2^57`, and the eight-lane
phase mask was `0x0a`. This repeats the E-004 anti-lever one boundary later.
E-010 was removed immediately; no composed artifact, full evaluation, or H64
ran. Default, E-007, and tail42 operation hashes reproduced exactly after
cleanup. Any next repair must explicitly preserve the carry across the
low56/high200 boundary and erase it coherently inside the remaining 992-T live
budget; another width shift is ruled out.

## E-011 explicit call-9 carry terminal update

E-011C1 reused the clean constant-add ladder apex to compute the exact carry
crossing bit 56 and controlled-increment the untouched high200 suffix. The
pinned E-009 control/target pair passed exact value, phase, and ancilla. The
focused square remained Q1272 and measured 59,583 emitted / 59,327.438
executed Toffoli versus the inherited 58,980 / 58,721.141: a `+603` /
`+606.297` price inside the 992-T live allowance.

The next frozen gate killed the implementation. All eight adversarial miter
values were exact, including both bit-57 boundary cases that killed E-010, and
all scratch was clean, but lane 4 (`z = 2^57-f`) retained phase mask `0x10`.
The miter peaked at Q515 and emitted 817 Toffolis. Per the declared stop rule,
square64, composition, full 9,024-shot evaluation, and H64 were not run.

The failed source and temporary harnesses were removed. Protected arithmetic,
product-square, evaluator, and tracked-results SHA-256 values reproduce as
`c6deb3c0...69e0`, `21e4ef93...a4c6`, `b35314bc...890b`, and
`eea84022...c810`. Default, E-007, and E-009 tail42 operation streams reproduce
12,901,167 / `ecc3d9f0...4cfd`, 12,943,345 / `4618d4af...9f37`, and
12,943,345 / `89d26f32...968` respectively.

Terminal verdict: `VALUE_EXACT; COST_PASS; PHASE_KILL; SOURCE_REMOVED`.
No hunt, scan, provider, remote, spend, submission, or downstream candidate
measurement ran. A successor requires a separately predeclared phase-clean
erasure, not another boundary shift or an adaptive patch inside E-011.

## E-012 phase-clean erasure terminal update

The E-011 durable packet omitted its simulator seed, and no harness survived.
E-012 froze `b"e011-call9-boundary-miter"` before output as an explicit
provenance repair. The fixed eight values remained exact and dirty-free at
Q515 / 817 emitted Toffolis; the repaired-seed phase mask was `0x30` rather
than the old unrepeatable `0x10`.

Stepped cleanup tracing killed the sole admitted complemented-AND hypothesis.
Every tagged high200 increment vent and clean low56 ladder HMR/CZ group had an
exact target/control-product identity and zero phase delta. Phase stayed zero
through the final low-ladder cleanup and appeared only in the downstream
`clear_overflow_phase` shell. No conditioned-`NEG` repair was implemented.

Per the frozen gate, square64, composition, and Q/T measurement did not run.
All instrumentation, candidate source, and harness code were removed;
protected hashes reproduce. Terminal verdict:
`HYPOTHESIS_FALSE; DOWNSTREAM_OVERFLOW_PHASE_LOCALIZED; SOURCE_REMOVED`.
No hunt, provider, spend, remote, or submission action ran.
