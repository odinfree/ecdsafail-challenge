from __future__ import annotations

import unittest

import affine_shell_transducer as shell


class AffineShellOracleTests(unittest.TestCase):
    def test_total_shell_is_bijective_and_invertible(self) -> None:
        case = shell.FieldCase(prime=17, a=1, b=5)
        report = shell.reference_report(case)
        self.assertEqual(report["states"], 17 * 17)
        self.assertEqual(report["unique_outputs"], 17 * 17)
        self.assertEqual(report["inverse_failures"], 0)
        self.assertEqual(report["curve_failures"], 0)
        self.assertGreaterEqual(report["valid_t_zero_inputs"], 1)

    def test_transducer_inverse_covers_zero_and_nonzero_fibers(self) -> None:
        case = shell.FieldCase(prime=17, a=1, b=5)
        for t in range(case.prime):
            for lam in range(case.prime):
                out = shell.transducer(case, t, lam)
                self.assertEqual(shell.inverse_transducer(case, *out), (t, lam))

    def test_first_curve_point_is_deterministic_and_valid(self) -> None:
        case = shell.first_curve_point(127)
        self.assertEqual(case.prime, 127)
        self.assertNotEqual(case.b, 0)
        self.assertEqual((case.b * case.b - case.a**3 - 7) % case.prime, 0)

    def test_target_has_variable_nonzero_fiber_determinant(self) -> None:
        case = shell.FieldCase(prime=17, a=1, b=5)
        determinants = shell.target_nonzero_determinants(case)
        self.assertEqual(determinants, set(range(1, case.prime)))

    def test_low_degree_shear_grammar_is_hard_nacked(self) -> None:
        case = shell.FieldCase(prime=31, a=0, b=10)
        certificate = shell.low_degree_shear_certificate(case)
        self.assertEqual(certificate["verdict"], "HARD_NACK_LOW_DEGREE_SHEAR")
        self.assertEqual(certificate["grammar_determinant_class"], "constant_nonzero")
        self.assertEqual(certificate["target_determinant_count"], 30)
        self.assertEqual(certificate["next_grammar"], "REGISTER_SHARED_EUCLID")


if __name__ == "__main__":
    unittest.main()
