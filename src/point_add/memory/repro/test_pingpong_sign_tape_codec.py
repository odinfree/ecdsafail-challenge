from __future__ import annotations

import unittest

import pingpong_sign_tape_codec as tape


class PingPongSignTapeRecurrenceTests(unittest.TestCase):
    def test_fused_round_zero_matches_all_four_low_bit_arms(self) -> None:
        p = 31
        expected = {
            4: (0, -29),  # floor(a/2) - p
            6: (0, 3),    # floor(a/2)
            5: (1, -13),  # floor(a/2) - (p-1)/2
            7: (1, 19),   # floor(a/2) + (p+1)/2
        }
        for value, want in expected.items():
            self.assertEqual(tape.fused_round_zero(p, value), want)

    def test_known_complete_toy_traces(self) -> None:
        expected = {
            1: "111100100011",
            2: "011110110011",
            3: "111101011111",
            4: "001000100110",
            5: "101010110000",
            7: "101011000110",
            11: "110001010011",
            16: "011011010010",
            30: "000011011100",
        }
        for value, want in expected.items():
            trace, terminal = tape.walk_trace(31, value, len(want))
            self.assertEqual(tape.bits_to_string(trace), want)
            self.assertEqual({abs(terminal[0]), abs(terminal[1])}, {1})

    def test_every_round_is_exactly_invertible_from_its_sign(self) -> None:
        for source in range(-31, 32, 2):
            for target in range(-31, 32, 2):
                sign, output = tape.signed_round(source, target)
                self.assertEqual(tape.signed_round_inverse(source, output, sign), target)

    def test_terminal_fixed_point_emits_a_constant_tail(self) -> None:
        trace, terminal, first_terminal = tape.walk_trace_with_convergence(31, 7, 24)
        self.assertIsNotNone(first_terminal)
        self.assertEqual({abs(terminal[0]), abs(terminal[1])}, {1})
        tail = trace[first_terminal:]
        self.assertTrue(tail)
        self.assertEqual(len(set(tail)), 1)


class PingPongSignTapeSupportTests(unittest.TestCase):
    def test_fixed_block_support_and_information_bits(self) -> None:
        traces = [tape.walk_trace(31, value, 12)[0] for value in range(1, 31)]
        row = tape.fixed_block_support(traces, start=0, width=4)
        self.assertEqual(row["samples"], 30)
        self.assertEqual(row["block_width"], 4)
        self.assertEqual(row["support"], len({tuple(trace[:4]) for trace in traces}))
        self.assertEqual(row["rank_bits"], (row["support"] - 1).bit_length())
        self.assertEqual(row["raw_minus_rank"], 4 - row["rank_bits"])

    def test_partition_information_bound_counts_each_position(self) -> None:
        traces = [tape.walk_trace(31, value, 12)[0] for value in range(1, 31)]
        row = tape.partition_bound(traces, block_width=4)
        expected = sum(
            (len({tuple(trace[start : start + 4]) for trace in traces}) - 1).bit_length()
            for start in range(0, 12, 4)
        )
        self.assertEqual(row["rank_bits"], expected)
        self.assertEqual(row["raw_bits"], 12)
        self.assertEqual(row["best_possible_saving"], 12 - expected)

    def test_gate_dump_parser_requires_complete_equal_length_rows(self) -> None:
        dump = """PINGPONG_TAPE_V1 rounds=4 lanes=2\nlane=0 denominator=0x1 tape=1010\nlane=1 denominator=0x2 tape=0111\n"""
        parsed = tape.parse_gate_dump(dump)
        self.assertEqual(parsed["rounds"], 4)
        self.assertEqual(parsed["rows"][1], {"lane": 1, "denominator": 2, "tape": [0, 1, 1, 1]})
        with self.assertRaises(ValueError):
            tape.parse_gate_dump(dump.replace("0111", "011"))


if __name__ == "__main__":
    unittest.main()
