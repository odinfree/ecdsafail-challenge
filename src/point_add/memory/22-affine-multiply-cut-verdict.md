# Affine multiply-cut: destructive-map and cleanup verdict

## Verdict

`HARD_NACK` for the tested algebraic families that claim to remove the second
ping-pong traversal by rearranging the affine formula, polarizing the product
through squares, or transplanting the new low-space EEA point-add architecture.
Every tested rearrangement either retains the same quantum-by-quantum in-place
product, leaves a full slope word as garbage, or misses the live score ceiling
by more than an order of magnitude before challenge-specific overhead.

This is not a lower bound against every curve-domain two-register permutation.
It closes the named schedules and gives a precise reopen interface.

## Source-bound affine equation

At the second callback in the current shell, the two quantum words are

```text
d = Qx - Rx
lambda = (Py - Qy) / (Px - Qx)
```

and the required destructive map is

```text
(d, lambda) -> (Rx, Ry) = (Qx - d, lambda*d - Qy).
```

The current callback implements `lambda *= d` while preserving `d`, after
which the shell applies the cheap classical-offset transform `d -> Qx-d`.
Merely noting that the shell later destroys `d` is a changed premise, but it is
not yet an implementation: a replacement must be a clean reversible map on the
legal curve domain and must restore every non-output wire.

## Polarization does not close in place

The field identity

```text
2*lambda*d = (lambda+d)^2 - lambda^2 - d^2
```

can compute the product into a third clean field word using square/add cells.
After swapping that result onto the output ABI, however, the third word holds
the old `lambda`. Clearing it requires the inverse relation

```text
lambda = (Ry + Qy) / (Qx - Rx),
```

which is exactly a variable modular division. H-measurement does not remove
the obligation: its feed-forward phase oracle is the same nonlinear function.
Thus square polarization is a cheap out-of-place product, not a clean in-place
multiply cut.

The ambient map has Jacobian determinant `-d`, whereas a composition of the
tested add/constant/square shears has constant nonzero determinant. Therefore
that shear family cannot equal the destructive map on the full two-word field
domain. This argument does not rule out a construction specialized to the
elliptic-curve support; such a construction must exhibit its support proof and
cleanup rather than invoking polarization alone.

## July 2026 low-space construction

The primary artifact inspected was:

- Han Luo et al., *Quantum Algorithm for Elliptic Curve Discrete Logarithms
  with Space-Efficient Point Addition*, arXiv:2607.13816;
- public implementation:
  `https://github.com/ZeroWang030221/Quantum-Algorithm-for-Elliptic-Curve-Discrete-Logarithms-with-Space-Efficient-Point-Addition`;
- inspected repository commit:
  `b5e4c664de212bdb0981d93d70964a1dca1a0ec9`.

Its exact register-sharing EEA changes the space equation materially: the
reported secp256k1 point-add width is Q835. Its in-place division/multiplication
schedule nevertheless retains a third 256-bit work word, runs forward and
inverse EEA blocks, and uses three modular multiply blocks plus measurement
feed-forward cleanup. The published leading counts are

```text
modular inversion: 195*n^2 = 12,779,520 Toffoli at n=256
point addition:     914*n^2 = 59,899,904 Toffoli at n=256
```

At the live score `1,154,731,130`, Q835 permits at most T1,382,911 for a
strict beat. The inversion leading term alone is 9.24 times that complete
point-add ceiling; the point-add leading term is 43.3 times the ceiling. This
is a static product failure, so a production port is unwarranted.

As an additional favorable census, the paper's classical optimized EEA model
was run at exact secp256k1 width for 64 deterministic random nonzero inputs.
Its 1,476 fixed steps visited 330,236 to 352,342 arithmetic bit positions per
forward pass (mean 345,228.3125), before location controls, swaps, length
updates, inverse execution, modular replay, or the second affine call. This is
a cost diagnostic for that literal recurrence, not a universal lower bound.

## Changed-premise reopen

Reopen affine multiply elimination only with one explicit construction that:

1. maps `(d,lambda)` directly to `(Rx,Ry)` on a stated independently checked
   domain;
2. leaves no hidden slope, product, inverse, quotient, or history word;
3. supplies a complete value, phase, ancilla, and ABI inverse schedule;
4. measures below the removed multiply traversal's approximately 425,000
   executed-Toffoli budget, including cleanup; and
5. preserves or lowers the Q1267 global binder and clears the strict score
   equation before any trusted 9,024-shot run.

No source prototype, provider, nonce, fleet, queue, push, public note,
protected-instance, or submission action was taken.
