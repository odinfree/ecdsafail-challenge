# Mission Command SC675-HF1 — Q1100-class exact history cut

Issued: 2026-08-24T10:13:08+0200 CEST
Activity: source-bound structural research, local implementation, and validation
Submit: CLOSED

## Commander's intent

Purpose: replace autoresearcher cadence with one falsifiable attempt to remove a
leading live-state term from the promoted ping-pong point-add circuit.

Key task: determine whether a block of ping-pong sign history can be represented
by a smaller code conditioned on the block endpoint and the coefficient-replay
state, then price an exact reversible decoder against the live score frontier.

End state: either a source-bound two-width `ADMIT` that justifies one Rust
prototype, or a decisive `HARD_NACK` with a collision, entropy floor, unstable
scaling law, or Q x T miss. Only a clean official score below the refreshed live
best settles the campaign.

## Authoritative binding

- Repository/worktree: `/Users/odin/Documents/coding with codin/ecdsafail-structural-history-fiber`
- Branch: `research/codex-structural-history-fiber-20260824`
- Commit: `67524171baaf568dc3dc606f38515745f70804ff`
- Tree: `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- Official source: `https://github.com/Layr-Labs/ecdsafail-challenge.git`, `refs/heads/main`
- Live frontier at binding: Q1267, T911390, score 1,154,731,130
- Local exact-source profiler: Q1267, 64-lane T911454.45, 0 classical,
  phase `0x0`, 0 dirty qubits. The 64-lane value is diagnostic, not the
  authoritative 9,024-shot score.
- Frozen defense stream `744136752171711a3a8da6c11ba3a855a330aefa`
  remains `HOLD`: its one-deletion proof passes, but Q1267/T911410.358 with
  evaluator 17/12/0 is not a candidate.
- Provider, nonce-grind, fleet, queue, public-note, and submission gates remain
  closed during this phase.
- The user-approved provider budget is at most USD 500 aggregate across Vast
  and RunPod per Europe/Zurich calendar day, with no rollover. It is dormant
  until source, prefilter, CPU/GPU parity, range ownership, stop-action, and
  campaign gates all pass. Vast instances 48436357 and 48491958 are protected.

## Exact peak ledger

The exact promoted source binds first at op 913421 in `pp_div_replay`:

```text
phase=pp_div_replay peak_q=1267 op_idx=913421
live=333 ordinary sign bits + 2 fused sign bits
live=256 coefficient + 256 numerator/caller
live=146 caller x + 146 walk/value state
live=126 replay carry ladder + 2 boundary carries
candidate=conditioned block history code with decode before reverse walk
proof_obligation=exact value, phase, ancilla, ABI, and lower global peak
```

The multiply-side co-binder occurs at op 8322690 in `pp_mul_walkback`:

```text
phase=pp_mul_walkback peak_q=1267 op_idx=8322690
live=636 ordinary sign bits + 2 fused sign bits
live=256 coefficient + 256 numerator/caller
live=40 regrown walk/value bits + 14 reacquired terminal passengers
live=58 replay carry ladder + 2 boundary carries + 3 scalar controls
candidate=same conditioned code, decoded in reverse block order
proof_obligation=one representation must lower both co-binders
```

Current score thresholds, using strict integer score below 1,154,731,130:

| Q | Maximum average T |
|---:|---:|
| 1,266 | 912,109 |
| 1,200 | 962,275 |
| 1,153 | 1,001,501 |
| 1,152 | 1,002,370 |
| 1,100 | 1,049,755 |
| 1,024 | 1,127,667 |
| 1,000 | 1,154,731 |

The selected design must model Q at or below 1,100. Q1152 is an intermediate
milestone, not the mission end state.

## Structural alternatives

### A. Conditioned block-history code — selected

For a block of `b` walk rounds, treat the raw sign word as a fiber over the
block endpoint `(u, v)` and the coefficient state `(x, y)`. Store only the
index within that exact reachable fiber. During the reverse traversal, decode
the block word from `(endpoint, coefficient_state, code)`, reverse replay and
walk, and return the code and decoder ancillas to zero.

This is not a local sign trick. For odd source and odd post-target, both
predecessors

```text
pre_target(sign=0) = 2*post_target - source
pre_target(sign=1) = 2*post_target + source
```

satisfy the source bit-1 sign rule. The coefficient recurrence also admits
both modular predecessors. Therefore post-walk or post-replay state alone is
locally two-to-one; global reachability or a retained code is mandatory.

The first experiment measures the exact reachable fibers for `n=5` and `n=6`
with moduli 29 and 61. It must report raw history bits, maximum fiber size,
minimum resident code bits, collisions, and an explicit round trip for every
input pair.

### B. Preserve-input shadow walk — parked cost reference

Preserving a 256-bit denominator and regenerating history with another walk can
replace raw tape with a checkpoint, but prior source notes price ordinary
Bennett/hierarchical checkpointing at roughly +30 percent T. The Q1100 strict
allowance is only +138,365 T over the authoritative T911390 baseline, about
15.2 percent. This route stays parked unless the selected fiber experiment
produces a decoder materially cheaper than a full shadow traversal.

### C. Radix/jump or tape-free local recovery — rejected

Radix-4/double-plus-minus was previously an information wash with a wider cell.
Local recovery is ruled out by the two-predecessor witness above. Neither route
may be relabeled as new structural progress without a new exact overturn
artifact tied to this source.

## Phase order

- Ball owner: this controller, hypothesis `SC675-HF1-A` only.
- Supporting roles: none during discovery; independent rebuilding begins only
  after a source-bound Rust candidate exists.
- Bound: one exact Python enumerator, two widths (`n=5`, `n=6`), block lengths
  1 through the configured convergence depth, one deterministic JSON receipt,
  and no circuit edit in this phase.
- Allowed resources: local CPU and the isolated worktree only.
- Required result: `ADMIT` or `HARD_NACK`, exact command, source hash, receipt
  SHA256, and a clean worktree scope proof.
- First falsifier: a reachable endpoint fiber whose required code width scales
  too close to the raw block width to model Q <= 1,100.

## Decision rights

Owner may make reversible local research edits inside `src/point_add/memory/`,
run local builds and simulations, commit verified research artifacts, and
select block sizes from enumerated evidence.

Owner may not purchase compute, launch or stop provider instances, grind
nonces, claim a candidate from a reduced-width result, push an unverified
milestone, publish, or submit.

Escalation is required on a live source change, ownership collision, daily
spend ambiguity, prefilter admission, a Q1100-class count-only Rust shape, or
any action that crosses an external-state gate.

## Forced resolution

Phase-one `ADMIT` to decoder synthesis requires all of the following:

1. exhaustive round-trip correctness at both widths;
2. no unreported endpoint/history collisions;
3. projected resident history plus decoder workspace at both exact peak
   equations is at most 469 bits on the multiply binder, yielding modeled
   Q <= 1,100;
4. scaling improves or stays stable from `n=5` to `n=6`; and
5. every enumerated history round-trips through the deterministic fiber index.

That verdict admits only a second, separately bounded decoder-synthesis phase.
Decoder synthesis must then show a cost model no larger than 138,365
additional average executed Toffoli for the whole point-add at Q1100 and state
one exact Rust prototype interface with value/phase/ancilla tests before any
circuit edit is admitted.

`HARD_NACK` follows from an exhaustive collision that violates the claimed
decoder interface, a lower bound above the resident-bit cap, a decoder lower
bound above the T allowance, or adverse two-width scaling with an explicit
witness.

Timeout, implementation difficulty, a stale public receipt, or missing cloud
capacity are not `HARD_NACK` evidence.

## Phase-one closeout

- Verdict: `ADMIT` to decoder synthesis only.
- Evidence: `src/point_add/memory/14-structural-history-fiber-verdict.json`
- Evidence SHA256: `fe2ea4b37efccd20b7786b9a08952d0ebc68cac9c396fe6174004be108733ba3`
- Width 5: modulus 29, 12 rounds, 812/812 exhaustive inputs converged,
  maximum final fiber 10, minimum code 4 bits for 12 raw signs.
- Width 6: modulus 61, 17 rounds, 3660/3660 exhaustive inputs converged,
  maximum final fiber 21, minimum code 5 bits for 17 raw signs.
- Scaling: code/raw improved from 0.333333 to 0.294118.
- Production information projection: one retained 256-bit denominator word.
  The reduced-width code grows as `width - 1` (4 bits at width 5, 5 bits at
  width 6), so scaling by the raw-sign ratio would be invalid. The corrected
  256-bit code is below the Q1100 history cap 469 and Q1000 cap 369.
- Qualification: information-theoretic and reduced-width only. No reversible
  decoder cost, production Q, executed T, op stream, nonce, or correctness
  claim follows from this result.
- Actions not taken: no circuit edit, provider action, nonce grind, fleet or
  queue dispatch, push, public note, submission, or protected-instance change.
- Next authorized action: apply the current-source materialization and
  recomputation bounds before any decoder implementation.

## Decoder static closeout

- Verdict: `HARD_NACK` for the selected endpoint-fiber/retained-denominator
  decoder family on Q1100 and Q1000.
- Evidence: `src/point_add/memory/15-structural-history-decoder-static-verdict.json`.
- Evidence SHA256: `6a3caf77906d930eea579ef9ae0655a86b3d2280cb845370bb745756e8fc151b`.
- Exact current-source geometry: the first unimplemented production sign at
  round 8 has `value_width(8)=258`. A materializing decoder needs 516 walk-state
  qubits + 512 replay-pair qubits + the 256-bit retained code = Q1284 before a
  sign, carry, extraction scratch, or the other co-binders.
- Exact current-source ordinary recomputation floor: deterministic generic walk
  CCX sums are 93,935 Divide and 93,925 Multiply after granting rounds 0..7
  free. One extra reverse+forward pass on both traversals costs at least
  `2 * (93,935 + 93,925) = 375,720 T`, before decoder, replay, square, or
  cleanup. This exceeds the Q1100 headroom 138,365 and Q1000 headroom 243,341.
- Direct retained-word extraction has adjacent exact evidence only through sign
  7; literal ANF terms through sign 14 grow
  `2,2,5,11,25,57,115,244,481,1001,2013,4041,8177,16433`. That is not a
  Boolean-circuit lower bound, but it supplies no full-depth decoder and cannot
  overturn either exact bound above.
- Prior artifacts reconciled: `fb07d5e` (retained transducer static kill),
  `43bcb37` (checkpoint Q/T bound), `0e20bdd` (only 6/1390 production fused
  calls covered), `2b0bd4c` (reachable local-sign collisions), and `65381d3`
  (ordinary full-history recomputation +38.1 percent on its bound ancestor).
- Actions not taken: no production circuit edit, full evaluator, provider,
  nonce, queue, push, public note, or submission.
- Changed-premise reopen: an exact in-place code update with a bounded-width
  reverse discriminator that never materializes `(u,v)` and is not a literal
  denominator ANF. The reduced-width fiber receipt does not exhibit one.
- Next authorized structural action: move off the closed sign axis and bind one
  replay-ABI/lifetime owner that lowers all current co-binders.

### Phase three settlement — sign-local one-word replay `HARD_NACK`

- Plan: `src/point_add/memory/16-oneword-replay-plan.md`.
- Evidence: `src/point_add/memory/17-oneword-replay-verdict.json` and
  `src/point_add/memory/repro/pp_oneword_replay.py`.
- Exact branch-matrix result: an even replay cell preserves only the untouched
  `x` projective coordinate across both sign branches; an odd cell preserves
  only `y`. The coordinates do not compose across a two-round pair.
- Reachable-tape enumeration saturates all nonzero field classes: 28/28 at
  width 5, 60/60 at width 6, and 126/126 at width 7. Terminal sign
  normalisation recovers the exact inverse for every legal denominator.
- Consequently a sign-local linear one-word replay needs a full-width
  discriminator: projected production storage is 256 data + 256 discriminator
  = 512 qubits before scratch, equal to the live replay pair.
- This is not a lower bound for arbitrary nonlinear in-place division. Reopen
  only with an explicit reversible transform and independent end-to-end Q/T
  pricing; invoking the original division as the decoder is circular.
- No production circuit, provider, nonce, queue, push, public-note, or
  submission action was taken.

### Phase four settlement — source-present full streaming `HARD_NACK`

- Evidence:
  `src/point_add/memory/19-full-streaming-co-residence-verdict.md`.
- Removing both batch regions through `R1=0/R2=terminal` leaves divide signs
  resident for the later reverse walk. The first exact binder is Q1309:
  coefficient/numerator 512 + walk limbs 478 + early walk ladder 235 + tape
  82 + two scalar wires.
- The fixed 64-lane stream is clean but costs T999247.98, yielding a diagnostic
  product 1,308,015,632. It is wider and more expensive than the live circuit,
  so no trusted evaluator or external-state action is admitted.
- Changed-premise reopen requires a sign-erasing recurrence, a smaller replay
  ABI, an exact narrow early walk cell, or removal of the affine multiply phase;
  another interleave coordinate does not qualify.

### Phase five settlement — dirty-history arithmetic `HARD_NACK`

- Evidence:
  `src/point_add/memory/20-dirty-history-arithmetic-verdict.md`.
- The exact vented prototype borrowed raw history as dirty carry workspace and
  restored value, phase, and ancillas in the full 64-lane composition.
- Its best bounded form measured Q1234/T1871482.19, versus a live-score ceiling
  of T935762 at that width.  The lower-width unrestricted form measured
  Q1233/T2271655.83.
- Once clean ladders disappear, terminal replay still owns 694 raw history plus
  the 512-qubit coefficient/numerator pair.  Carry borrowing cannot reach
  Q1203 without changing one of those semantic terms.
- The prototype is preserved at commit `3a00a61` and reverted at `255b9dd`; the
  source head contains no activated dirty-history implementation.

### Phase six settlement — stationary terminal suffix `HARD_NACK`

- Evidence:
  `src/point_add/memory/21-stationary-suffix-codec-verdict.md`.
- A fixed cutoff at round 631 aliases 64 later logical signs to one physical
  terminal-run sign, but the exact fixed-64 selfcheck reports 27 classical
  mismatches. The `(+-1, +-1)` orbit is stationary; entry into it is not
  universally complete by round 631.
- The default planner absorbs the nominal history saving into replay ladders,
  leaving Q1267. Forcing both planner caps to 1209 makes the exact split
  geometry worse at Q1289/T64 957078.58 and does not repair correctness.
- Prototype `ffa9e377d4b48a23d216cd071a5b3c6009bc2324` was exactly reverted by
  `33197ff07b58eecc9d89e2b7dd5d4b237c25b1a8`; the production source is restored.
- Reopen only for an exact variable-boundary suffix code, a proof of an earlier
  admitted-domain convergence bound, or a recurrence with a cheaper reversible
  convergence certificate.
- No 9,024-shot evaluation, provider, nonce, fleet, queue, push, public note,
  protected-instance, or submission action was taken.

## Anti-rot ban list

The following do not advance structural cadence:

- reduced-width correctness without cross-width scaling;
- a lower raw tape count with unchanged global peak;
- count-only Q without executed-T pricing;
- local or synthetic score without the official 9,024-shot harness;
- a nonce survivor, GPU filter, or one-deletion proof labeled as correctness;
- tuning rounds, widths, windows, ladders, or nonce values under the structural
  label;
- accumulating findings without closing the predeclared falsifier; or
- a self-authored candidate validating itself at the independent gate.

## Campaign settlement

The broader goal is complete only after a clean isolated rebuild, exact op and
source hashes, independent CPU/reference/GPU parity as applicable, unchanged
official 9,024-shot validation with 0/0/0, refreshed strict score superiority,
and a recorded official promotion. Until then every artifact is diagnostic,
`submit=CLOSED`, and the route ledger remains active.
