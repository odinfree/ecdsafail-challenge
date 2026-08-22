# Teddy Pender compact-history saddle on exact `6b5c82c`

Verdict: `KILL_BENNETT_RECONSTRUCTION`

Promotion status: `NO_CANDIDATE`; no hunt, provider work, submission, or
publication occurred.

## Protected contract

- Source: `6b5c82cbe723b33c296c8926876f14f1ac3307a8`.
- Protected metrics: Q1278 / exact average T918357.924 / rounded T918358 /
  score1173661524 / trusted `0/0/0`.
- Strict ceilings: Q1182 requires T<=992945; Q1148 requires T<=1022353.
- Existing paired prerequisite: commit `2d2eeb2` established that Teddy's
  four-round low-five candidate and its unchanged reference have identical
  midpoint, reverse, final logical, and ancilla results. It did not establish a
  full-depth decoder.

Teddy Pender supplied the architecture question and the method: protect the
leader, write the overturn, run the cheapest falsifier, compose every co-binder,
and grind only after the product clears. This result is a direct application of
that method.

## Exact checkpoint accounting

The divide branch of `pingpong_mod_mul_div_in_place` walks rounds `0..355`, then
explicitly shrinks both walk registers to `value_width(plan.r1)` before the
first batch replay. On exact source:

```text
plan.r1 = 356
value_width(356) = WIDTH_SCHEDULE[356] = 140
checkpoint = 2 * 140 = 280 wires
allowance = 1278 - 356 - 512 - 280 = 130 wires
peak = 356 + 512 + 280 + 130 = 1278
```

This is a source equation, not a sampled allocation estimate. The 280-wire
checkpoint named in the saddle is therefore present exactly where expected.

## Fixed-scratch recurrence falsifier

For every generic walk round, `signed_add_wrapping_sigma` and its split form
emit exactly `width-3` CCX gates. Their measurement uncompute uses CZ, so those
CCX gates execute deterministically. A Bennett-compatible fixed-scratch divide
decoder must move from the round-356 checkpoint back to the input boundary and
forward again to supply signs in replay order. Relative to the protected walk
and walkback, that adds one reverse and one forward pass.

The exact schedule sum is:

```text
sum(value_width(r), r=1..355) = 72,565
sum(value_width(r)-3, r=1..355) = 71,500
two extra passes = 143,000 deterministic CCX
```

This deliberately excludes round zero and any decoder/cleanup gates, making it
a favorable lower bound for this implementation class.

At Q1182:

```text
allowed delta over exact baseline ~= 992945 - 918357.924 = 74587.076 T
walk-pass floor = 143000 T
shortfall before square/decoder = 68412.924 T
```

At Q1148 after the measured sparse-square full-affine delta of +1012 T:

```text
favorable T floor = 918357.924 + 143000 + 1012 = 1062369.924
rounded T floor = 1062370
Q1148 score floor = 1148 * 1062370 = 1219600760
protected score = 1173661524
loss = 45939236
strict Q needed at that T = floor((1173661524-1)/1062370) = 1104
```

The exact sparse-square component is Q1148, so it cannot reach Q1104. The
existing recurrence reconstruction therefore cannot compose into a strict
beat even with zero decoder overhead beyond those passes and free round-zero
handling.

## Composition audit

| component | exact-live evidence | compatibility verdict |
|---|---|---|
| divide checkpoint | 280 wires at r1=356 | geometry survives |
| fixed-scratch existing-walk reconstruction | >=143,000 extra deterministic T | killed on product |
| Teddy sparse square | standalone Q1148; full-affine +1012 deterministic-64 T | width survives; its Q floor blocks the Q1104 requirement |
| symmetric multiply teardown | `917cde9`: replay allocation remains live through every binding add | allocation-release route killed; a new tape decoder remains unimplemented |
| global composition | all Q1278/Q1276 owners must fall | no complete path below Q1182, and favorable T already loses |

The multiply traversal consumes signs in reverse order, so a genuine backward
checkpoint decoder could align with its walkback without the divide side's
extra order-conversion pass. That observation keeps a new direct decoder open;
it does not rescue the divide economics above.

## Injectivity boundary

The 280-bit checkpoint has enough raw capacity to encode a 256-bit denominator,
so dimension counting does not kill injectivity at round 356. Conversely, the
transition is locally two-to-one, and later exact-live collision work found
reachable sign disagreements once the state narrows. A bounded QF_BV collision
query attempted to settle round 356 but returned `unknown`, even on its small
sanity instance. PIP rule: timeout/unknown is not a lower bound. The generator
and solver output were removed from shipping HEAD.

The only useful reopen is a stronger exact rank/unrank construction or proof,
not more sampling. It must beat the Q1148 post-square budget of roughly 102,983
extra executed T and then pass the paired slice gate.

## Gate-off reproduction and shipping audit

With every research gate absent, a clean invocation produced:

```text
emitted operations: 12950916
ops.bin SHA-256: 88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb
```

The temporary `ops.bin` was moved to Trash with its isolated directory. No
generated operation stream, score file, solver query, build target, evaluator,
or helper binary remains in this worktree. `git diff 6b5c82c -- src/` is empty.
