#!/usr/bin/env python3
"""Import the hash-bound Q1273 combined CPU donor into the Q1272 namespace.

The imported files are inputs to a source-derived port, not qualified Q1272
artifacts.  Refuse any donor drift before writing.
"""

from __future__ import annotations

import hashlib
import pathlib
import subprocess


ROOT = pathlib.Path(__file__).resolve().parents[3]
DONOR = "3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e"
FILES = {
    ".lane/q1273-predictor/src/pp_host.h": (
        ".lane/q1272-live-phase/src/pp_host.h",
        "bc2df2182beb8ebcc103a3fc498a8ca65911bf52439566dbfa1284e88407f98a",
    ),
    ".lane/q1273-predictor/src/pp_model.h": (
        ".lane/q1272-live-phase/src/pp_model.h",
        "14fc9230b55d2b2a84721e50d860933764a18d1357ad30331e5999280f764261",
    ),
    ".lane/q1273-predictor/src/ppcpu.cpp": (
        ".lane/q1272-live-phase/src/ppcpu.cpp",
        "1d93d46803670324401443ed9f625ee641c6fa8ef77ba4a920baebff83ea24ce",
    ),
    ".lane/q1273-phase/tools/generate_phase_schedule.py": (
        ".lane/q1272-live-phase/tools/generate_phase_schedule.py",
        "83bfa142f2cf546ea5673de424597bf26ed3a57db0173d2b177a009ad9f8e966",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    for source, (destination, expected) in FILES.items():
        data = subprocess.run(
            ["git", "show", f"{DONOR}:{source}"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        actual = sha256(data)
        if actual != expected:
            raise SystemExit(f"donor drift: {source}: {actual} != {expected}")
        path = ROOT / destination
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f"{actual}  {destination}")


if __name__ == "__main__":
    main()
