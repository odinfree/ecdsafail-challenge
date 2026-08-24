import hashlib
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import final_carry_handoff as handoff


REPO = pathlib.Path(__file__).resolve().parents[4]
EVIDENCE = pathlib.Path(__file__).with_name("final_carry_handoff_evidence.json")


class SourceInventoryTests(unittest.TestCase):
    def test_exact_source_binding_and_economics(self) -> None:
        inventory = handoff.build_inventory(REPO)

        self.assertEqual(
            inventory["source_commit"],
            "522d00296ab014b0f4d128915b53851516f17f4d",
        )
        self.assertEqual(
            inventory["source_tree"],
            "eab2326ce33549eceeb5c10aa64eae33f148b0ac",
        )
        self.assertEqual(inventory["rounds"], {"divide": 694, "multiply": 693})
        self.assertEqual(inventory["cell_calls"], {"divide": 692, "multiply": 691})
        self.assertEqual(inventory["fold_width"], {"divide": 54, "multiply": 53})
        self.assertEqual(inventory["flag_compare_width"], 22)
        self.assertEqual(inventory["chunk_compare_width"], 22)
        self.assertEqual(inventory["flag_compare_ccx_per_cell"], 21)
        self.assertEqual(inventory["flag_compare_condition_depth"], 1)
        self.assertEqual(inventory["flag_compare_average_t"], 14_521.5)
        self.assertEqual(inventory["minimum_uniform_saved_ccx"], 3)
        self.assertEqual(inventory["three_ccx_gross_average_t"], 2_074.5)
        self.assertEqual(inventory["three_ccx_added_cost_ceiling"], 574.5)

        self.assertEqual(
            inventory["source_blobs"],
            {
                "src/point_add/pingpong_div.rs": "f4399563b1fe8c4beee568027ebf52df252e7555",
                "src/point_add/arith/compare.rs": "7c3c9cd4956799b8a93ff108ce4bc4d3358def91",
                "src/point_add/mod.rs": "8b497c16d804d9e128fd1139ad4858ddb1de56de",
            },
        )


class ReducedMiterTests(unittest.TestCase):
    def test_phase_blind_candidate_is_rejected(self) -> None:
        mismatch = handoff.first_phase_blind_mismatch(range(5, 10))
        self.assertEqual(mismatch["site"], "divide")
        self.assertEqual(mismatch["sign"], 0)
        self.assertEqual(mismatch["post_add_parity"], 0)
        self.assertEqual(mismatch["overflow"], 1)
        self.assertNotEqual(
            mismatch["baseline_phase_coefficient"],
            mismatch["candidate_phase_coefficient"],
        )

    def test_selector_only_publication_has_exact_divide_witness(self) -> None:
        witness = handoff.divide_parity_zero_exact_witness()
        self.assertEqual(witness["width"], 256)
        self.assertEqual(witness["sign"], 0)
        self.assertEqual(witness["post_add_parity"], 0)
        self.assertEqual(witness["selectors"], {
            "first_carry": 0,
            "minus_f": 0,
            "plus_f": 0,
            "plus_2f": 0,
        })
        self.assertEqual(witness["overflow"], 1)
        self.assertEqual(witness["flag_repair"], 0)
        self.assertEqual(witness["residual_phase_coefficient"], 1)

    def test_baseline_reduced_miter_all_arms_and_inverse_cleanup(self) -> None:
        report = handoff.run_reduced_miter(range(5, 10))
        self.assertEqual(report["widths"], [5, 6, 7, 8, 9])
        self.assertEqual(report["value_mismatches"], 0)
        self.assertEqual(report["selector_cleanup_mismatches"], 0)
        self.assertEqual(report["fold_cleanup_mismatches"], 0)
        self.assertEqual(report["inverse_mismatches"], 0)
        self.assertEqual(report["uncovered_sign_arms"], [])
        self.assertEqual(report["uncovered_measurement_arms"], [])
        self.assertGreater(report["basis_cases"], 0)
        self.assertGreater(report["phase_coefficients_checked"], report["basis_cases"])

    def test_exact_local_retained_chain_is_phase_clean_but_q_bounded(self) -> None:
        report = handoff.run_exact_local_chain_miter(range(5, 10))

        self.assertEqual(report["widths"], [5, 6, 7, 8, 9])
        self.assertEqual(report["value_mismatches"], 0)
        self.assertEqual(report["phase_mismatches"], 0)
        self.assertEqual(report["ancilla_mismatches"], 0)
        self.assertEqual(report["inverse_mismatches"], 0)
        self.assertEqual(report["uncovered_sign_arms"], [])
        self.assertEqual(report["uncovered_measurement_arms"], [])
        self.assertEqual(report["candidate_final_phase"], 0)
        self.assertGreater(report["carry_coefficients_checked"], report["basis_cases"])


class PublicationRankTests(unittest.TestCase):
    def test_divide_selector_quotient_loses_overflow_on_both_sign_arms(self) -> None:
        report = handoff.analyze_publication_rank()
        divide = report["divide"]
        self.assertEqual(divide["local_rows"], 8)
        self.assertEqual(divide["ambiguous_groups"], 2)
        self.assertEqual(divide["ambiguous_signs"], [0, 1])
        self.assertEqual(len(divide["exact_witness_pairs"]), 2)
        for pair in divide["exact_witness_pairs"]:
            left, right = pair["states"]
            self.assertEqual(left["selectors"], right["selectors"])
            self.assertEqual(left["post_add_parity"], 0)
            self.assertEqual(right["post_add_parity"], 0)
            self.assertNotEqual(left["overflow"], right["overflow"])
            self.assertNotEqual(
                left["residual_phase_coefficient"],
                right["residual_phase_coefficient"],
            )

    def test_multiply_selector_quotient_retains_add_out_but_not_cleanup(self) -> None:
        report = handoff.analyze_publication_rank()
        multiply = report["multiply"]
        self.assertEqual(multiply["local_rows"], 16)
        self.assertEqual(multiply["ambiguous_groups"], 0)
        self.assertEqual(
            multiply["overflow_decoder"],
            "plus_f XOR doubled_out XOR minus_f",
        )
        self.assertEqual(multiply["decoded_rows"], 16)
        self.assertEqual(multiply["last_carrier_rank"], 1)

    def test_exact_multiply_transfer_covers_every_sign_doubled_carry_arm(self) -> None:
        report = handoff.exact_multiply_transfer_report()

        self.assertEqual(report["width"], 256)
        self.assertEqual(report["fold_width"], 53)
        self.assertEqual(report["covered_arms"], 8)
        self.assertEqual(report["missing_arms"], [])
        self.assertEqual(report["q_relation_mismatches"], 0)
        self.assertEqual(report["selector_decoder_mismatches"], 0)
        self.assertEqual(
            {(row["sign"], row["doubled_out"], row["add_out"]) for row in report["rows"]},
            {(sign, doubled, carry) for sign in (0, 1) for doubled in (0, 1) for carry in (0, 1)},
        )


class LifetimeLedgerTests(unittest.TestCase):
    def test_static_census_parser_pairs_add_and_cell_records(self) -> None:
        text = """\
CARRY_HANDOFF_ADD phase=pp_div_replay ops_start=10 ops_end=20 entry_active=1100 local_peak=1200 return_active=1101 ladder_target=Some(100) bounds=0-80,80-256
CARRY_HANDOFF_CELL site=divide phase=pp_div_replay ops_start=9 ops_end=30 entry_active=1100 after_add_active=1101 fold_entry_active=1142 fold_peak=1193 cell_peak=1200 end_active=1100
CARRY_HANDOFF_ADD phase=pp_mul_walkback ops_start=40 ops_end=50 entry_active=1101 local_peak=1201 return_active=1102 ladder_target=Some(101) bounds=0-128,128-256
CARRY_HANDOFF_CELL site=multiply phase=pp_mul_walkback ops_start=39 ops_end=60 entry_active=1100 after_add_active=1102 fold_entry_active=1139 fold_peak=1189 cell_peak=1201 end_active=1100
"""
        records = handoff.parse_static_census(text)
        summary = handoff.summarize_static_census(records, peak_limit=1_266)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["site"], "divide")
        self.assertEqual(records[0]["final_chunk_width"], 176)
        self.assertTrue(records[0]["final_chunk_has_boundary"])
        self.assertEqual(records[1]["final_chunk_width"], 128)
        self.assertEqual(summary["site_counts"], {"divide": 1, "multiply": 1})
        self.assertEqual(summary["literal_retention"]["fitting_cells"], 0)

    def test_literal_retention_charges_every_coexisting_final_chunk_carry(self) -> None:
        records = [
            {
                "site": "divide",
                "fold_peak": 1_200,
                "final_chunk_width": 80,
                "final_chunk_has_boundary": True,
            },
            {
                "site": "multiply",
                "fold_peak": 1_200,
                "final_chunk_width": 50,
                "final_chunk_has_boundary": True,
            },
        ]
        ledger = handoff.literal_retention_ledger(records, peak_limit=1_266)

        # The final carry is already live in the baseline fold peak.  Retaining
        # w-1 owned carries plus the incoming boundary therefore adds exactly w.
        self.assertEqual(ledger["records"][0]["retained_extra_wires"], 80)
        self.assertEqual(ledger["records"][0]["literal_peak"], 1_280)
        self.assertFalse(ledger["records"][0]["fits"])
        self.assertEqual(ledger["records"][1]["retained_extra_wires"], 50)
        self.assertEqual(ledger["records"][1]["literal_peak"], 1_250)
        self.assertTrue(ledger["records"][1]["fits"])
        self.assertEqual(ledger["fitting_cells"], 1)
        self.assertEqual(ledger["gross_average_t"], 10.5)


class NonlinearLowerBoundTests(unittest.TestCase):
    def test_exact_secp_and_embedding_covers_both_sites_and_all_22bit_inputs(self) -> None:
        report = handoff.exact_secp_and_embedding_report(22)

        self.assertEqual(report["cases"], 1 << 22)
        self.assertEqual(report["comparison_mismatches"], 0)
        self.assertEqual(report["canonical_range_mismatches"], 0)
        self.assertEqual(report["divide"]["selector_mismatches"], 0)
        self.assertEqual(report["divide"]["parity_mismatches"], 0)
        self.assertEqual(report["multiply"]["q_mismatches"], 0)
        self.assertEqual(report["multiply"]["correction_digit_mismatches"], 0)
        self.assertEqual(report["multiply"]["fold_width"], 53)
        self.assertEqual(report["true_cases"], 1)

    def test_top_window_comparator_restricts_to_and_n(self) -> None:
        report = handoff.comparator_and_restriction_report(range(5, 10), 22)

        self.assertEqual(report["exhaustive_widths"], [5, 6, 7, 8, 9])
        self.assertEqual(report["restriction_mismatches"], 0)
        self.assertEqual(report["exact_width"], 22)
        self.assertEqual(report["exact_and_arity"], 22)
        self.assertEqual(report["multiplicative_complexity_lower_bound"], 21)
        self.assertEqual(report["source_comparator_ccx"], 21)
        self.assertTrue(report["source_comparator_is_optimal_in_xor_and_model"])

    def test_partial_suffix_needs_237_predecessors_to_save_three_ccx(self) -> None:
        below = handoff.retained_suffix_cost_bound(236, total_width=256)
        threshold = handoff.retained_suffix_cost_bound(237, total_width=256)

        self.assertEqual(below["exact_recompute_ccx_lower_bound"], 19)
        self.assertEqual(below["saved_ccx_upper_bound"], 2)
        self.assertEqual(below["all_cells_gross_average_t_upper_bound"], 1_383.0)
        self.assertFalse(below["can_reach_target_before_added_cost"])

        self.assertEqual(threshold["exact_recompute_ccx_lower_bound"], 18)
        self.assertEqual(threshold["saved_ccx_upper_bound"], 3)
        self.assertEqual(threshold["all_cells_gross_average_t_upper_bound"], 2_074.5)
        self.assertTrue(threshold["can_reach_target_before_added_cost"])

    def test_even_perfect_fold_host_reuse_cannot_fit_threshold_suffix(self) -> None:
        report = handoff.perfect_dirty_host_q_bound(
            retained_predecessors=237,
            fold_entry_min={"divide": 1_142, "multiply": 1_139},
            peak_limit=1_266,
        )

        self.assertEqual(report["divide"]["optimistic_peak"], 1_379)
        self.assertEqual(report["multiply"]["optimistic_peak"], 1_376)
        self.assertFalse(report["divide"]["fits"])
        self.assertFalse(report["multiply"]["fits"])
        self.assertEqual(report["assumption"], "all fold carry hosts replaced at zero cost")


class TerminalEvidenceTests(unittest.TestCase):
    def test_terminal_packet_is_bound_complete_and_hash_stable(self) -> None:
        raw = EVIDENCE.read_bytes()
        evidence = json.loads(raw)

        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "5862c7dd7e42fa76cd34f9296990989aa4a1d4741519e0078315e4e47be49cf7",
        )
        self.assertEqual(evidence["verdict"], "HARD_NACK_CARRY_HANDOFF_FAMILY")
        self.assertEqual(evidence["receipts"]["baseline_peak_q"], 1_266)
        self.assertEqual(
            evidence["receipts"]["ops_sha256"],
            "a4995dc4be4b7b314853d379941141b3b5753110412c07e8a2bc5d097d218ed1",
        )
        self.assertEqual(
            evidence["receipts"]["instrumentation_patch_sha256"],
            "3d95f32eaef0bab18e3c0408d0004484cfdf55c8cd53a99072989bdd1a9cd668",
        )
        self.assertEqual(evidence["static_census"]["records"], 1_383)
        self.assertEqual(
            evidence["static_census"]["site_counts"],
            {"divide": 692, "multiply": 691},
        )
        self.assertEqual(
            evidence["static_census"]["literal_retention"]["fitting_cells"], 0
        )
        self.assertEqual(
            evidence["static_census"]["literal_retention"]["global_literal_peak_min"],
            1_288,
        )
        self.assertEqual(
            evidence["suffix_cost_bounds"]["236"]["saved_ccx_upper_bound"], 2
        )
        self.assertEqual(
            evidence["suffix_cost_bounds"]["237"]["saved_ccx_upper_bound"], 3
        )
        self.assertTrue(
            all(route["state"] == "KILLED" for route in evidence["route_registry"].values())
        )



if __name__ == "__main__":
    unittest.main()
