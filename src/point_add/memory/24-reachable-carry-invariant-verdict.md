# Reachable carry invariant census: verdict

## Verdict

`HARD_NACK` for reachable-state affine carry invariants as the structural-cut
route to a large score win or a changed lower-Q equation.

The exact census found a few legitimate but constant-size parities.  None
scales into a material fraction of the carry ladder, none shortens a resident
carry segment, and none changes the Q1267 binder.  They remain defense-only
observations and do not authorize a production edit.

## Binding and artifacts

- official source commit:
  `67524171baaf568dc3dc606f38515745f70804ff`;
- official source tree:
  `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`;
- live score equation: Q1267/T911390, score 1,154,731,130;
- harness:
  `src/point_add/memory/repro/pp_reachable_carry.py`, SHA-256
  `8db3f0581105a7c59170409107dc8af16f3b299a8b0230bcc053c93ffa3a9a66`;
- tests:
  `src/point_add/memory/repro/test_pp_reachable_carry.py`, SHA-256
  `b54634ddd02585639e82db4f89937f76df36f0a3422a84d51cc3e741b5641d7c`;
- exact receipt:
  `src/point_add/memory/23-reachable-carry-invariant-receipt.json`, SHA-256
  `5c56eea7a4656611d0e25295eac56fa707d983afa6a1f2fc6805eafc94bee3ce`.

The receipt covers all 32,692 legal denominators for ten odd moduli of bit
width 5 through 14: 1,276,398 exact pre-round observations, of which 962,750
are active and 313,648 terminal.  Every reported support/result table has its
own SHA-256 digest.

## What was searched

Each walk add ran in a fixed `N+3` two's-complement envelope, avoiding the
production sampled width schedule entirely.  At every active round and cell,
the solver tested whether

```text
delta_i = c_(i+1) xor c_i
```

is affine in the Clifford-linear span of all wires already available there:
the sign, every source bit, every target bit, and every earlier live carry.
The GF(2) solve has no term-count cutoff.  The exact smallest envelope required
by each round was computed separately so that cells belonging to width shrink,
the terminal cell, the top guard, and the already-specialized first two rounds
could not masquerade as a new interior mechanism.

The positive controls held on all 1,276,398 observations:

```text
c1 = 1 xor sign
c2 = source[1].
```

Full Boolean support also correctly rejected affine synthesis of a generic
AND.

## Scaling result

New eligible interior affine-cell counts by modulus bit width were:

```text
bits:       5  6  7  8  9  10 11 12 13 14
cells:      1  3  0  1  1   1  0  1  3  1
fraction: 8.3 10.3 0 1.41 .96 .75 0 .46 1.08 .31 percent
```

The repeated observation is one round-2/bit-2 parity.  It appears for several
moduli but remains exactly one cell as width grows, is absent at widths 7, 11,
and 13, and has density tending to zero.  It can save at most a constant number
of nonlinear cells across the complete point-add shell and cannot lower peak
width.

The two literal zero-products at width 6 disappear at width 7.  The three
width-13 relations occur only for the special Mersenne modulus 8191, at
different rounds and bit positions, and do not recur at width 14.  These are
the support-specific mirages the cross-width gate was designed to reject.

## Reopen interface

Reopen this route only with an invariant family that:

1. affects `Omega(N)` active interior cells or removes a resident carry segment;
2. survives adjacent widths and non-special odd moduli;
3. has an arbitrary-width proof on the production legal domain;
4. maps its affine inputs to wires live at the exact replacement point; and
5. clears the Q1267 score equation before any Rust source prototype or trusted
   9,024-shot replay.

No production source, provider, nonce, fleet, queue, push, public note,
protected instance, or submission state was changed.
