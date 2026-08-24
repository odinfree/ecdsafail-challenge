from __future__ import annotations

import unittest

import algebraic_root_compactor as gate


class AlgebraicRootCompactorTests(unittest.TestCase):
    def test_curve_root_identity_and_inverse_recovery_multi_width(self) -> None:
        reports = [gate.case_report(prime) for prime in (31, 127, 251)]
        self.assertEqual([row["support_states"] for row in reports], [18, 124, 249])
        self.assertTrue(all(row["root_identity_failures"] == 0 for row in reports))
        self.assertTrue(all(row["output_equality_failures"] == 0 for row in reports))
        self.assertTrue(all(row["inverse_slope_failures"] == 0 for row in reports))
        self.assertTrue(all(row["paired_root_sign_failures"] == 0 for row in reports))
        self.assertTrue(all(row["cubic_squarefree"] for row in reports))

    def test_secp_addition_chain_relaxation_exceeds_budget(self) -> None:
        report = gate.secp_addition_chain_report()
        self.assertEqual(report["prime_mod_4"], 3)
        self.assertEqual(report["root_exponent_bit_length"], 254)
        self.assertEqual(report["addition_chain_multiplication_lower_bound"], 253)
        self.assertGreater(report["relaxed_square_only_t"], 13_000_000)
        self.assertGreater(report["budget_multiple"], 40)
        self.assertEqual(report["verdict"], "HARD_NACK_ADDITION_CHAIN_DECOMPRESS")

    def test_receipt_is_deterministic_and_scoped(self) -> None:
        first = gate.run_gate((31, 127, 251))
        second = gate.run_gate((31, 127, 251))
        self.assertEqual(first, second)
        self.assertEqual(first["verdict"], "HARD_NACK_ALGEBRAIC_ROOT_COMPACTOR")
        self.assertEqual(
            first["rational_decoder"]["verdict"],
            "HARD_NACK_RATIONAL_ROOT_COMPACTOR",
        )
        self.assertEqual(len(first["receipt_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
