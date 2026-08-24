from __future__ import annotations

import unittest

import curve_support_product_invariants as miner


class CurveSupportProductInvariantTests(unittest.TestCase):
    def test_affine_solver_accepts_xor_and_rejects_and(self) -> None:
        constant = 0b1111
        x = 0b1100
        y = 0b1010
        self.assertIsNotNone(miner.affine_solution((constant, x, y), x ^ y))
        self.assertIsNone(miner.affine_solution((constant, x, y), x & y))

    def test_width_five_support_is_exhaustive_and_deterministic(self) -> None:
        first = miner.case_report(31)
        second = miner.case_report(31)
        self.assertEqual(first, second)
        self.assertEqual(first["width"], 5)
        self.assertEqual(first["support_states"], 18)
        self.assertEqual(first["identity_failures"], 0)
        self.assertTrue(first["positive_controls_ok"])
        self.assertTrue(first["full_support_and_rejected"])
        self.assertEqual(len(first["support_sha256"]), 64)

    def test_composite_modulus_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "prime"):
            miner.case_report(63)

    def test_multi_width_receipt_is_deterministic(self) -> None:
        first = miner.run_census((31, 61, 127, 251))
        second = miner.run_census((31, 61, 127, 251))
        self.assertEqual(first, second)
        self.assertEqual([row["width"] for row in first["cases"]], [5, 6, 7, 8])
        self.assertEqual(first["scope"], "AFFINE_CURVE_PRODUCT_SUPPORT")
        self.assertEqual(len(first["receipt_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
