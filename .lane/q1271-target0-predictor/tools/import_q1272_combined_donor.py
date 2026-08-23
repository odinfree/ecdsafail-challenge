#!/usr/bin/env python3
"""Import the hash-bound terminal Q1272 combined CPU donor.

The imported files are unqualified target inputs.  Target identities,
geometry, constants, and fixture parity must be re-derived locally.
"""

from __future__ import annotations

import hashlib
import pathlib
import subprocess


ROOT = pathlib.Path(__file__).resolve().parents[3]
DONOR = "83ad631e1a99db3db1c3886b4d61ff9ded94b0f5"
FILES = {
    ".lane/q1272-live-phase/src/pp_host.h": (
        ".lane/q1271-target0-predictor/src/pp_host.h",
        "aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2",
    ),
    ".lane/q1272-live-phase/src/pp_model.h": (
        ".lane/q1271-target0-predictor/src/pp_model.h",
        "0d4c9a812892b9dac598cb59a8345c443b9e21663ac29743578f4e651b39b92a",
    ),
    ".lane/q1272-live-phase/src/ppcpu.cpp": (
        ".lane/q1271-target0-predictor/src/ppcpu.cpp",
        "dd05545d33911e7e0ab44b0e373f03a759ae8ee4b990f20f2cc40ca6ee2063af",
    ),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    for source, (destination, expected) in FILES.items():
        data = subprocess.run(
            ["git", "show", f"{DONOR}:{source}"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        actual = digest(data)
        if actual != expected:
            raise SystemExit(f"donor drift: {source}: {actual} != {expected}")
        path = ROOT / destination
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise SystemExit(f"refusing to overwrite {path}")
        path.write_bytes(data)
        print(f"{actual}  {destination}")


if __name__ == "__main__":
    main()
