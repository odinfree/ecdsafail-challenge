from __future__ import annotations

import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pingpong_third_passenger_support as support  # noqa: E402


REPO = HERE.parents[3]


class SourceAndLifetimeContractTests(unittest.TestCase):
    def test_current_source_and_binder_windows_are_parsed(self) -> None:
        contract = support.load_source_contract(REPO)

        self.assertEqual(contract.rounds_div, 694)
        self.assertEqual(contract.rounds_mul, 694)
        self.assertEqual(contract.r1_div, 335)
        self.assertEqual(contract.r1_mul, 315)
        self.assertEqual(contract.r2, 645)
        self.assertEqual(contract.peak, 1267)
        self.assertEqual(contract.walk_peak, 1267)
        self.assertEqual(contract.endpoint_fold_window, 26)
        self.assertEqual(contract.loaned_bits, ("u[0]", "v[0]"))
        self.assertEqual(
            contract.pingpong_sha256,
            "67f6b692b1fed3641dad487b062ce0304958b312c4627355e772bc3954eea842",
        )
        self.assertEqual(
            contract.builder_sha256,
            "63f9568027fd4ce15523872d124fe374b3d1f1430ae08c62fb31d9ab2b2a3838",
        )

    def test_both_directional_loan_windows_are_covered(self) -> None:
        contract = support.load_source_contract(REPO)
        divide = support.loan_sites(contract, "divide")
        multiply = support.loan_sites(contract, "multiply")

        self.assertEqual(divide[0], support.LoanSite("divide", "prefix-batch", 334))
        self.assertEqual(divide[1], support.LoanSite("divide", "interleaved", 335))
        self.assertEqual(divide[-1], support.LoanSite("divide", "interleaved", 645))
        self.assertEqual(len(divide), 312)
        self.assertEqual(multiply[0], support.LoanSite("multiply", "prefix-batch", 314))
        self.assertEqual(multiply[1], support.LoanSite("multiply", "interleaved", 315))
        self.assertEqual(multiply[-1], support.LoanSite("multiply", "interleaved", 645))
        self.assertEqual(len(multiply), 332)
        self.assertTrue(all(contract.widths[site.after_round + 1] >= 3 for site in divide))
        self.assertTrue(all(contract.widths[site.after_round + 1] >= 3 for site in multiply))

    def test_q1265_and_q1264_profiles_have_the_two_expected_binders(self) -> None:
        self.assertEqual(
            support.BINDING_CONFIGS,
            (
                support.BindingConfig("q1265", 1267, 1266, 1265),
                support.BindingConfig("q1264", 1266, 1265, 1264),
            ),
        )


class ExactInvariantTests(unittest.TestCase):
    def test_low_bit_transition_lemma_exhausts_all_odd_operands(self) -> None:
        result = support.exhaustive_low_bit_transition()

        self.assertEqual(result.rows, 16)
        self.assertEqual(result.violations, ())

    def test_scaled_secp_low_bits_hold_exhaustively(self) -> None:
        result = support.exhaustive_scaled_support(width=6, f=9, through_round=39)

        self.assertEqual(result.modulus, 55)
        self.assertEqual(result.denominators, 54)
        self.assertEqual(result.checks, 2_106)
        self.assertEqual(result.violations, ())

    def test_modulus_low_bits_are_part_of_the_certificate(self) -> None:
        result = support.exhaustive_scaled_support(width=6, f=5, through_round=4)

        self.assertGreater(len(result.violations), 0)
        # f = 5 makes the fused-round-1 correction h = (f - 1) / 2
        # congruent to 2 mod 4, so it immediately changes the proposed
        # passenger bit.  Secp256k1 has f = 2^32 + 977 = 1 mod 8, hence
        # h = 0 mod 4 and does not have this failure.
        self.assertEqual(result.violations[0].round_index, 1)

    def test_source_exact_full_width_probe_covers_every_loan_round(self) -> None:
        contract = support.load_source_contract(REPO)
        result = support.production_probe(contract, samples=128)

        self.assertEqual(result.samples, 128)
        self.assertEqual(result.first_round, 314)
        self.assertEqual(result.last_round, 645)
        self.assertEqual(result.checks, 42_496)
        self.assertEqual(result.violations, ())
        self.assertEqual(
            result.input_digest,
            "38090b4131e7d89a408274dbfdba70e4082ad860e723677d1bf74ad1f77345e2",
        )

    def test_two_cnot_clear_and_restore_work_for_both_parities(self) -> None:
        contract = support.load_source_contract(REPO)
        denominator = support.deterministic_denominator(0)

        for round_index in (314, 315, 334, 335, 645):
            checkpoint = support.production_checkpoint(
                contract,
                denominator,
                round_index,
            )
            self.assertTrue(support.relation_holds(checkpoint))
            cleared = support.apply_third_passenger_xors(checkpoint)
            passenger = cleared.v if round_index % 2 == 0 else cleared.u
            self.assertEqual((passenger >> 1) & 1, 0)
            self.assertEqual(
                support.apply_third_passenger_xors(cleared),
                checkpoint,
            )

    def test_local_current_sign_family_obeys_the_predeclared_falsifier(self) -> None:
        contract = support.load_source_contract(REPO)
        for round_index, passenger in ((314, "v"), (315, "u"), (334, "v"), (335, "u")):
            with self.subTest(round_index=round_index, passenger=passenger):
                collision = support.find_local_boolean_collision(
                    contract,
                    round_index=round_index,
                    passenger=passenger,
                    samples=32,
                )

                self.assertIsNotNone(collision)
                assert collision is not None
                self.assertEqual(
                    collision.left.reconstructors,
                    collision.right.reconstructors,
                )
                self.assertEqual(collision.left.reconstructors[-2:], (1, 1))
                self.assertNotEqual(
                    collision.left.passenger_bit,
                    collision.right.passenger_bit,
                )


if __name__ == "__main__":
    unittest.main()
