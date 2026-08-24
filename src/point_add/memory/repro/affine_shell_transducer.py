#!/usr/bin/env python3
"""Exact reduced-width model of the exceptional-safe affine shell."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldCase:
    prime: int
    a: int
    b: int

    def __post_init__(self) -> None:
        if self.prime <= 2 or self.prime % 2 == 0:
            raise ValueError("prime must be an odd integer")
        if not (0 <= self.a < self.prime and 0 <= self.b < self.prime):
            raise ValueError("coordinates must be canonical field elements")
        if (self.b * self.b - self.a**3 - 7) % self.prime != 0:
            raise ValueError("classical point is not on y^2=x^3+7")


def inv(value: int, prime: int) -> int:
    value %= prime
    if value == 0:
        raise ZeroDivisionError("zero has no field inverse")
    return pow(value, prime - 2, prime)


def unit(value: int, prime: int) -> int:
    value %= prime
    return value if value else 1


def lambda_zero(case: FieldCase) -> int:
    return (3 * case.a * case.a * inv(unit(2 * case.b, case.prime), case.prime)) % case.prime


def transducer(case: FieldCase, t: int, lam: int) -> tuple[int, int]:
    p = case.prime
    t %= p
    lam %= p
    x_out = (case.a - t) % p
    if t:
        y_out = (t * lam - case.b) % p
    else:
        y_out = (lam - lambda_zero(case) - case.b) % p
    return x_out, y_out


def inverse_transducer(case: FieldCase, x_out: int, y_out: int) -> tuple[int, int]:
    p = case.prime
    t = (case.a - x_out) % p
    if t:
        lam = ((y_out + case.b) * inv(t, p)) % p
    else:
        lam = (y_out + case.b + lambda_zero(case)) % p
    return t, lam


def shell_from_input(case: FieldCase, x: int, y: int) -> tuple[int, int]:
    p = case.prime
    d = (x - case.a) % p
    e = (y - case.b) % p
    lam = (e * inv(unit(d, p), p)) % p
    t = (d + 3 * case.a - lam * lam) % p
    return transducer(case, t, lam)


def unshell_to_input(case: FieldCase, x_out: int, y_out: int) -> tuple[int, int]:
    p = case.prime
    t, lam = inverse_transducer(case, x_out, y_out)
    d = (t - 3 * case.a + lam * lam) % p
    e = (lam * unit(d, p)) % p
    return (d + case.a) % p, (e + case.b) % p


def ec_add(case: FieldCase, x: int, y: int) -> tuple[int, int] | None:
    p = case.prime
    if x % p == case.a:
        if (y + case.b) % p == 0:
            return None
        slope = (3 * x * x * inv(2 * y, p)) % p
    else:
        slope = ((y - case.b) * inv(x - case.a, p)) % p
    x_out = (slope * slope - x - case.a) % p
    y_out = (slope * (x - x_out) - y) % p
    return x_out, y_out


def first_curve_point(prime: int) -> FieldCase:
    for a in range(prime):
        rhs = (a**3 + 7) % prime
        for b in range(1, prime):
            if b * b % prime == rhs:
                return FieldCase(prime=prime, a=a, b=b)
    raise ValueError(f"no nonzero-y curve point found for p={prime}")


def reference_report(case: FieldCase) -> dict[str, int]:
    p = case.prime
    outputs: set[tuple[int, int]] = set()
    inverse_failures = 0
    curve_failures = 0
    valid_t_zero_inputs = 0
    curve_inputs = 0
    for x in range(p):
        for y in range(p):
            out = shell_from_input(case, x, y)
            outputs.add(out)
            if unshell_to_input(case, *out) != (x, y):
                inverse_failures += 1
            if (y * y - x**3 - 7) % p == 0 and x != case.a:
                expected = ec_add(case, x, y)
                if expected is not None:
                    curve_inputs += 1
                    d = (x - case.a) % p
                    lam = ((y - case.b) * inv(d, p)) % p
                    t = (d + 3 * case.a - lam * lam) % p
                    valid_t_zero_inputs += int(t == 0)
                    if out != expected:
                        curve_failures += 1
    return {
        "states": p * p,
        "unique_outputs": len(outputs),
        "inverse_failures": inverse_failures,
        "curve_inputs": curve_inputs,
        "curve_failures": curve_failures,
        "valid_t_zero_inputs": valid_t_zero_inputs,
    }


def target_nonzero_determinants(case: FieldCase) -> set[int]:
    """Jacobian determinants of (T,L)->(a-T,T*L-b) for T != 0.

    The derivative matrix is [[-1, 0], [L, T]], so det=-T. The
    returned set is normalized to positive field representatives.
    """
    p = case.prime
    return {(-t) % p for t in range(1, p)}


def low_degree_shear_certificate(case: FieldCase) -> dict[str, object]:
    """Close the additive-shear grammar by its determinant invariant.

    Translations and additive triangular shears have determinant one; swaps
    have determinant minus one; multiplication by a classical field unit has
    a fixed nonzero determinant. A composition therefore has one constant
    nonzero determinant on the nonzero-T region. The target has determinant
    -T and assumes every nonzero value when p > 3.
    """
    determinants = target_nonzero_determinants(case)
    variable = len(determinants) > 1
    return {
        "grammar": "LOW_DEGREE_TWO_REGISTER_SHEARS",
        "grammar_determinant_class": "constant_nonzero",
        "target_determinants": sorted(determinants),
        "target_determinant_count": len(determinants),
        "target_is_variable": variable,
        "zero_branch_relevant": False,
        "proof_scope": "nonzero T fibers; zero-only corrections cannot repair the mismatch",
        "verdict": "HARD_NACK_LOW_DEGREE_SHEAR" if variable else "INCONCLUSIVE",
        "next_grammar": "REGISTER_SHARED_EUCLID",
    }
