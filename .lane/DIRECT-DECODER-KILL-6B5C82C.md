# Direct rank/unrank checkpoint decoder on exact `6b5c82c`

Verdict: `KILL_DIRECT_DECODER` — every constructive decoder class for the
280-wire round-356 checkpoint is closed. No candidate, no hunt, no provider
work, no submission.

Source: `6b5c82cbe723b33c296c8926876f14f1ac3307a8` (production `src/`
byte-identical to base throughout; nothing was ported).

Method: smallest strict falsifier first, on an exact classical model of the
divide walk, before any circuit work. The model was validated as a paired
reference/oracle (forward walk vs independent backward reconstruction) before
any falsifier was trusted.

## Protected contract (unchanged)

- Q1278 / exact average T918,357.924, rounded T918,358,
  score 1,173,661,524, trusted `0/0/0`.
- Strict ceilings: Q1182 requires T<=992,945 (delta 74,587; ~73,575 after the
  sparse-square +1,012); Q1148 requires T<=1,022,353 (delta 103,995; ~102,983
  after the sparse-square +1,012).
- One full sign-consuming pass over rounds 1..355 costs exactly
  `sum(value_width(r)-3, r=1..355) = 71,500` deterministic CCX.

## Exact classical model and its validation

The model reproduces the register semantics of `pingpong_div.rs` bit for bit:
round-0 fused odd-lift `w = (a + (a0 - 2*(1-a1))*p)/2`; generic round
`t := wrap_w(t + (-1)^sigma * s) >> 1` with `sigma = t[1]^s[1]`, target
alternating by round parity, widths from the shipped `WIDTH_SCHEDULE`,
two's-complement wrap at each round width, shrink/grow as sign-extension.

Validation (E1/E4, seed-fixed):

- 300/300 sampled denominators: backward reconstruction with the true signs
  reproduces every one of the 355 intermediate states exactly. The model is
  self-inverse, matching the circuit's walk/walk-back pairing.
- 300/300 checkpoints at r1=356 fit 140-bit signed registers (max magnitude
  133 bits) — the exact 280-wire checkpoint recorded in
  `TEDDY-COMPACT-HISTORY-6B5C82C.md`.
- 50/50 full 694-round walks terminate at `u, v in {+1, -1}`; width-violation
  events were rare (2 across ~34,650 rounds), consistent with a tuned
  small-tail schedule.

## Result 1: zero local sign information (lemma + exhaustive check)

Undoing generic round `r` from state `(s, t')` offers two candidates,
`t = 2t' - s` (sigma=0) and `t = 2t' + s` (sigma=1). They differ by `2s` with
`s` odd, so their bit-1 values differ, and the two self-consistency conditions
`sigma = t[1]^s[1]` therefore coincide: **both candidates are consistent or
neither is**. A reachable state has a real predecessor, so on the accepted
support both are always consistent.

Empirically (E2): 71,000/71,000 backward steps on true trajectories had both
candidates self-consistent, and the wrong candidate inside the round's width
envelope every single time. A backward decoder extracts exactly zero bits per
step from the sign rule.

## Result 2: no envelope signal in register semantics

The walk registers are w-bit wrapped. A backward candidate is produced by
`wrap_w(2t' ± s)` and therefore always fits its register; a width violation on
a wrong branch is locally unobservable — it silently wraps and remains
self-consistent. The width schedule cannot be used as a local pruning oracle
by any reversible in-register decoder.

## Result 3: refuting a wrong sign is an unpruned exponential search

E3 explored the full backward subtree of the wrong sign candidate (consistency
plus envelope pruning enabled) at rounds {5, 20, 50, 100, 150, 200, 250, 300,
340, 355}, 60 denominators each:

- Round 5: the subtree is a complete binary tree — exactly `2^5 - 1 = 31`
  nodes, zero interior pruning; it dies only by reaching the round-0 boundary.
- Rounds >= 20: every one of 60 subtrees exceeded a 20,000-node exploration
  cap without a single extinction, reaching depth `r` (the round-0 boundary)
  while still branching.

The only discriminator between the true and wrong sign at round `r` is the
global boundary condition (`u_0 = p` exactly, canonical odd-lifted `v_0`),
`r` rounds away. Deciding one sign by search costs on the order of `2^r`
round-width evaluations; a deterministic-Toffoli circuit must provision the
worst case for all 356 signs. This is not over budget — it is out of the
theory entirely.

## Composition closure

| decoder class | status |
|---|---|
| bounded local / lookahead backward decoder (any order) | killed by Results 1-3: zero local information, no envelope signal, exponential refutation |
| Bennett reverse+forward through the existing walk | already killed at the >=143,000 T two-pass floor (> 102,983 budget); Results 1-3 strengthen it — the reverse pass cannot even take a step without the signs it is supposed to produce |
| forward re-walk from recovered `v_0` | sign order fits the divide replay, and one pass is 71,500 T (< 102,983), but recovering `v_0` from the checkpoint requires inverting the sign-dependent linear system; the only known constructions are extended-gcd/lattice style on the 280-bit pair, on the order of the full 694-round walk (several 10^5 T) — over the 31,483 T slack by an order of magnitude, before reversibility overhead |
| multiply-side backward alignment | the ordering compatibility noted in the prior evidence is moot: the backward decoder it would consume cannot exist in bounded form (Results 1-3); the `917cde9` lifetime census independently keeps the 256-wire replay allocation live |
| checkpoint-as-rank / unrank table | the map checkpoint -> sign-sequence has no known closed form; absent an algebraic identity it degenerates to one of the classes above |

Injectivity of the checkpoint on the accepted support remains unproven (the
prior QF_BV `unknown` stands). It is now moot: even granting injectivity,
no bounded decoder exists in any constructive class.

## Reopen condition

Only a genuinely new algebraic identity that recovers `v_0` (or streams the
signs in replay order) from the 280-bit checkpoint in a reversible circuit
under ~31,483 executed T would reopen this. No such identity is known; 2-adic
continued-fraction structure puts the early signs in the expansion direction,
which the reduced checkpoint does not expose without the matrix the signs
themselves define.

## Shipping audit

- `git diff 6b5c82c -- src/` is empty; no evaluator, generated operation
  stream, or helper binary was added to the worktree.
- The falsifier model lives outside the repository in the job's temporary
  directory and does not ship.
- No nonce hunt, no GPU or provider spend, no submission, no edits outside
  this worktree.
