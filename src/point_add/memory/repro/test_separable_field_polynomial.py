from __future__ import annotations

import unittest

import separable_field_polynomial as miner


class SeparableFieldPolynomialTests(unittest.TestCase):
    def test_cycle_witness_closes_unrestricted_separation_at_p31(self) -> None:
        report = miner.case_report(31)
        self.assertFalse(report["unrestricted_separable"])
        self.assertIsNone(report["minimum_symmetric_degree"])
        self.assertNotEqual(report["cycle_witness"]["alternating_residual"], 0)
        self.assertTrue(miner.verify_cycle_witness(report["cycle_witness"]))

    def test_consistent_support_requires_half_field_interpolation(self) -> None:
        p61 = miner.case_report(61)
        p127 = miner.case_report(127)
        self.assertTrue(p61["unrestricted_separable"])
        self.assertTrue(p127["unrestricted_separable"])
        self.assertEqual(p61["minimum_symmetric_degree"], 29)
        self.assertEqual(p127["minimum_symmetric_degree"], 62)
        self.assertEqual(p61["solution_failures"], 0)
        self.assertEqual(p127["solution_failures"], 0)

    def test_neighboring_p251_support_is_not_separable_at_any_degree(self) -> None:
        report = miner.case_report(251)
        self.assertFalse(report["unrestricted_separable"])
        self.assertIsNone(report["minimum_symmetric_degree"])
        self.assertTrue(miner.verify_cycle_witness(report["cycle_witness"]))

    def test_synthetic_degree_three_control_is_admitted(self) -> None:
        report = miner.synthetic_control_report(61)
        self.assertLessEqual(report["minimum_symmetric_degree"], 3)
        self.assertEqual(report["solution_failures"], 0)

    def test_receipt_is_deterministic_and_hard_nacked(self) -> None:
        first = miner.run_census((31, 61, 127, 251))
        second = miner.run_census((31, 61, 127, 251))
        self.assertEqual(first, second)
        self.assertEqual(first["verdict"], "HARD_NACK_SEPARABLE_FIELD_POLYNOMIAL")
        self.assertFalse(first["material_family"])
        self.assertEqual(len(first["receipt_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
