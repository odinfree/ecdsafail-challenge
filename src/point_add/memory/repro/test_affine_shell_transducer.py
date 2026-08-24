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
        self.assertEqual(
            certificate["identity_requirement"],
            "symbolic identity on the nonzero-T open set",
        )
        self.assertEqual(certificate["target_determinant_count"], 30)
        self.assertEqual(certificate["next_grammar"], "REGISTER_SHARED_EUCLID")

    def test_wave1_receipt_is_deterministic_and_multi_width(self) -> None:
        first = shell.run_wave1((31, 127, 251))
        second = shell.run_wave1((31, 127, 251))
        self.assertEqual(first, second)
        self.assertEqual(first["verdict"], "HARD_NACK_LOW_DEGREE_SHEAR")
        self.assertEqual([row["prime"] for row in first["cases"]], [31, 127, 251])
        self.assertTrue(all(row["inverse_failures"] == 0 for row in first["cases"]))
        self.assertTrue(all(row["curve_failures"] == 0 for row in first["cases"]))
        self.assertEqual(len(first["receipt_sha256"]), 64)

    def test_curve_support_shared_denominator_identity_multi_width(self) -> None:
        reports = [
            shell.curve_support_report(shell.first_curve_point(prime))
            for prime in (31, 127, 251)
        ]
        self.assertTrue(all(row["identity_failures"] == 0 for row in reports))
        self.assertTrue(all(row["lambda_recovery_failures"] == 0 for row in reports))
        self.assertTrue(all(row["output_failures"] == 0 for row in reports))
        self.assertTrue(all(row["reformulated_output_failures"] == 0 for row in reports))
        self.assertTrue(all(row["maximum_t_fiber_size"] <= 2 for row in reports))
        self.assertTrue(all(row["reformulated_jacobian_count"] > 1 for row in reports))
        self.assertEqual([row["support_states"] for row in reports], [18, 124, 249])

    def test_curve_support_wave_receipt_separates_information_from_cost(self) -> None:
        first = shell.run_curve_support_wave((31, 127, 251))
        second = shell.run_curve_support_wave((31, 127, 251))
        self.assertEqual(first, second)
        self.assertEqual(first["verdict"], "HOLD_CURVE_SUPPORT_CLEANUP_OPEN")
        self.assertEqual(first["support_result"], "ADMIT_INFORMATION_ONLY")
        self.assertEqual(
            first["current_diagnostic"]["ops_sha256"],
            "715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184",
        )
        self.assertEqual(
            first["literal_point_decompression"]["verdict"],
            "HARD_NACK_CURRENT_SQUARE_FERMAT_DECOMPRESS",
        )
        self.assertEqual(
            first["literal_point_decompression"]["binary_exponent_squarings"], 253
        )
        self.assertGreater(
            first["literal_point_decompression"]["budget_multiple"], 40.0
        )
        self.assertEqual(len(first["receipt_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
