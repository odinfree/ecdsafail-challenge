#!/usr/bin/env python3
"""A2 falsifier: exact symbolic sweep of segment-aggregate transition matrices.

Replay semantics (src/point_add/pingpong_div.rs):
  halving  round r>=2 (pp_div_replay):  target <- (target + (-1)^sign * source)/2 mod p
  doubling round r>1  (pp_mul_walkback): target <- 2*target + (-1)^sign * source mod p
  parity of r alternates (source,target) between the pair (coefficient, numerator).

For a k-round segment the coefficient update factors through
  M_seg(s) = M_{r+k-1}(s_{k-1}) ... M_r(s_0)   (2x2 over Z[1/2], applied mod p).

This sweep computes, EXACTLY over all 2^k sign patterns for k = 1..K:
  - injectivity of s -> M_seg (representation lower bound: any register from which
    the segment action is applicable must hold >= k qubits);
  - max signed numerator bit-width b(k) of the dyadic entries (materialized
    register width per entry);
  - max denominator exponent (halving) / max integer magnitude (doubling).

Proved bounds used for extrapolation past K (checked by the sweep on 1..K):
  halving:  every entry stays in [-1, 1] (induction: (a+-b)/2 with |a|,|b|<=1),
            denominators divide 2^k  =>  b(k) <= k+1 signed bits per entry.
  doubling: |entry| <= 3^k (induction: |2a+-b| <= 3*max) => b(k) <= ceil(k*log2 3)+1.
  injectivity mod p: numerators fit in < 2^(k+1) (halving) / 3^k (doubling), both
            < p for k <= 160, so Z[1/2]-injectivity implies mod-p injectivity there.
"""
from fractions import Fraction
from itertools import product

def mat_mul(A, B):
    return (
        (A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]),
        (A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]),
    )

def round_matrix(direction, r, sigma):
    h = Fraction(1, 2)
    if direction == "halving":
        # even r: y <- (y + sigma*x)/2 ; odd r: x <- (x + sigma*y)/2
        if r % 2 == 0:
            return ((1, 0), (sigma * h, h))
        return ((h, sigma * h), (0, 1))
    else:  # doubling
        # even r: y <- 2y + sigma*x ; odd r: x <- 2x + sigma*y
        if r % 2 == 0:
            return ((1, 0), (sigma, 2))
        return ((2, sigma), (0, 1))

def sweep(direction, K, start_round=2):
    print(f"\n== {direction} (rounds {start_round}..), exact over Z[1/2] ==")
    print(f"{'k':>2} {'distinct':>10} {'2^k':>10} {'inj':>4} {'b(k)':>5} "
          f"{'maxden_e':>8} {'3*b(k)':>7} {'bound':>6}")
    for k in range(1, K + 1):
        seen = set()
        max_num_bits = 0
        max_den_e = 0
        for signs in product((1, -1), repeat=k):
            M = ((1, 0), (0, 1))
            for j, s in enumerate(signs):
                M = mat_mul(round_matrix(direction, start_round + j, s), M)
            key = tuple(Fraction(M[i][j]) for i in range(2) for j in range(2))
            seen.add(key)
            for e in key:
                f = Fraction(e)
                max_num_bits = max(max_num_bits, abs(f.numerator).bit_length() + 1)
                max_den_e = max(max_den_e, f.denominator.bit_length() - 1)
        inj = len(seen) == 2 ** k
        bound = k + 1 if direction == "halving" else -(-k * 1585 // 1000) + 1
        ok = max_num_bits <= bound
        print(f"{k:>2} {len(seen):>10} {2**k:>10} {str(inj):>4} {max_num_bits:>5} "
              f"{max_den_e:>8} {3*max_num_bits:>7} {'<=' if ok else 'VIOLATED':>6}{bound}")
        assert inj, f"injectivity failed at k={k} ({direction})"
        assert ok, f"proved bound violated at k={k} ({direction})"

if __name__ == "__main__":
    sweep("halving", 14)
    sweep("halving", 14, start_round=3)  # odd-start parity
    sweep("doubling", 14)
    sweep("doubling", 14, start_round=3)
    print("\nAll injectivity + growth bounds hold exactly.")
