#!/usr/bin/env python3
"""Port the proven phase extension onto the exact Q1273 classical model."""

from __future__ import annotations

import hashlib
import pathlib
import sys


DONOR_SHA256 = "0419bcf5bc1b2c1d73b4a92a15ca4c6da0d78ed869ecc4ea741dec628dcc5d32"
TARGET_CLASSICAL_SHA256 = "8e97b9b94d313e05bbe7fb844a53381b17c9c3fbd027a744feb41edaa993976d"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"port-phase-model: expected one occurrence, got {count}: {old!r}")
    return text.replace(old, new)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: port_phase_model.py Q1274_PHASE_MODEL Q1273_MODEL")
    donor_path = pathlib.Path(sys.argv[1])
    target_path = pathlib.Path(sys.argv[2])
    donor_raw = donor_path.read_bytes()
    target_raw = target_path.read_bytes()
    if digest(donor_raw) != DONOR_SHA256:
        raise SystemExit("port-phase-model: donor hash mismatch")
    if digest(target_raw) != TARGET_CLASSICAL_SHA256:
        raise SystemExit("port-phase-model: Q1273 classical input hash mismatch")
    text = donor_raw.decode("utf-8")

    text = replace_once(
        text,
        "ROUNDS_DIV=698, ROUNDS_MUL=696), retargeted to the Q1274 repair-r100\n"
        "// stream at source commit fe0b7bac.",
        "ROUNDS_DIV=698, ROUNDS_MUL=696), retargeted to the Q1273 repair-r100\n"
        "// stream at source commit 093d85d.",
    )
    text = replace_once(
        text,
        "#define PP_ROUNDS_DIV 698 // exact Q1274 repair-r100 divide depth @fe0b7bac\n"
        "#define PP_ROUNDS_MUL 696 // exact Q1274 repair-r100 multiply depth @fe0b7bac\n",
        "#define PP_ROUNDS_DIV 698 // exact Q1273 repair-r100 divide depth @093d85d\n"
        "#define PP_ROUNDS_MUL 696 // exact Q1273 repair-r100 multiply depth @093d85d\n"
        "#define PP_REPLAY_PEAK 1273\n"
        "#define PP_SQUARE_LADDER 243\n",
    )
    text = replace_once(
        text,
        "// Exact source fe0b7bac WIDTH_REPAIR membership.",
        "// Exact inherited r100 WIDTH_REPAIR membership at source 093d85d.",
    )
    text = replace_once(
        text,
        "// Q1274 repair-r100 value_width():",
        "// Q1273 repair-r100 value_width():",
    )
    text = replace_once(
        text,
        "const int window = 20; // replay_chunk_compare() on frozen fe0b7ba",
        "const int window = 20; // replay_chunk_compare() on frozen 093d85d",
    )
    text = replace_once(
        text,
        "int allowance = 1274 - (tape_len + 2 * PP_N + 2 * walk_width);",
        "int allowance = PP_REPLAY_PEAK - (tape_len + 2 * PP_N + 2 * walk_width);",
    )
    replacements = {
        "pp_wide_add_phase(product, spread, n, 244, tr);":
            "pp_wide_add_phase(product, spread, n, PP_SQUARE_LADDER, tr);",
        "pp_wide_sub_phase(product, xext, n, 244, tr);":
            "pp_wide_sub_phase(product, xext, n, PP_SQUARE_LADDER, tr);",
        "pp_wide_sub_phase(slice, low, m, 244, nullptr);":
            "pp_wide_sub_phase(slice, low, m, PP_SQUARE_LADDER, nullptr);",
        "pp_wide_add_phase(slice, low, m, 244, nullptr);":
            "pp_wide_add_phase(slice, low, m, PP_SQUARE_LADDER, nullptr);",
        "pp_wide_add_phase(product, xext, n, 244, tr);":
            "pp_wide_add_phase(product, xext, n, PP_SQUARE_LADDER, tr);",
        "pp_wide_sub_phase(product, spread, n, 244, tr);":
            "pp_wide_sub_phase(product, spread, n, PP_SQUARE_LADDER, tr);",
        "pp_wide_add_phase(acc, add, add_bits, 244, tr);":
            "pp_wide_add_phase(acc, add, add_bits, PP_SQUARE_LADDER, tr);",
        "Shift 32's 225-bit add fits the 244-wire ladder.":
            "Shift 32's 225-bit add fits the source-bound square ladder.",
    }
    for old, new in replacements.items():
        text = replace_once(text, old, new)

    target_path.write_text(text, encoding="utf-8", newline="\n")
    print(f"port-phase-model: PASS output_sha256={digest(target_path.read_bytes())}")


if __name__ == "__main__":
    main()
