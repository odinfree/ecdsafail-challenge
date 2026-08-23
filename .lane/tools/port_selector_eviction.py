#!/usr/bin/env python3
"""Hash-bound transplant of the selector-eviction donor delta.

This applies only the two source-file delta from donor 14608572 relative to
its parent onto the promoted 4eb93cb source.  Three-way merge output hashes
were frozen read-only before this script was written; any source drift or
merge ambiguity aborts before either target file is changed.
"""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DONOR_PARENT = "71a5aae760e612345ffed924cd14381010d98ac1"
DONOR = "14608572e84daf89397768c43ac0d812c714c3bd"

FILES = {
    "src/point_add/pingpong_div.rs": {
        "target_before": "a247d6c7f31fd382b3041e4cb2f21d13d7870551fe68344e22615a02e11c0d20",
        "parent": "92ffe2f17886334e9db863e81683ef31911c46b759b7b7acac65017591e6c66d",
        "donor": "de5e347383a9bab4d76a2776b3bcee4bebda4fecb65beb3dd1ad4c1cbf4c1095",
        "target_after": "6e7cce578663d8419c032190a9caa405ca0d84e0512104b766b9c68540f01994",
    },
    "src/point_add/mod.rs": {
        "target_before": "da681f674c2bd0be2c507eafcc7785e045530d920fa343a52593aecf65619ba9",
        "parent": "6f0cf6561cbe4177f7b774100db0683e8e73524c5941ff40fbea07801cf537a1",
        "donor": "3106691965fbd0002fc0dc427e07f28f30654be49b748beb08d93b30c21db490",
        "target_after": "0c9e9a920d9078f2390028009895f03d495096fdac9d2b596c7913c064e03e63",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(commit: str, relpath: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{relpath}"], cwd=ROOT
    )


def merged(current: bytes, parent: bytes, donor: bytes) -> bytes:
    with tempfile.TemporaryDirectory(prefix="selector-port-") as tmp:
        tmpdir = Path(tmp)
        current_path = tmpdir / "current"
        parent_path = tmpdir / "parent"
        donor_path = tmpdir / "donor"
        current_path.write_bytes(current)
        parent_path.write_bytes(parent)
        donor_path.write_bytes(donor)
        proc = subprocess.run(
            [
                "git",
                "merge-file",
                "-p",
                str(current_path),
                str(parent_path),
                str(donor_path),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        if proc.returncode != 0:
            raise SystemExit(
                f"merge ambiguity (rc={proc.returncode}): "
                f"{proc.stderr.decode(errors='replace')}"
            )
        return proc.stdout


def main() -> None:
    outputs: dict[Path, bytes] = {}
    for relpath, expected in FILES.items():
        target = ROOT / relpath
        current = target.read_bytes()
        parent = git_blob(DONOR_PARENT, relpath)
        donor = git_blob(DONOR, relpath)
        observed = {
            "target_before": sha(current),
            "parent": sha(parent),
            "donor": sha(donor),
        }
        for name, digest in observed.items():
            if digest != expected[name]:
                raise SystemExit(
                    f"{relpath}: {name} hash drift: {digest} != {expected[name]}"
                )
        output = merged(current, parent, donor)
        digest = sha(output)
        if digest != expected["target_after"]:
            raise SystemExit(
                f"{relpath}: merged output drift: {digest} != {expected['target_after']}"
            )
        outputs[target] = output

    # All hashes and both merges have passed; only now mutate the worktree.
    for target, output in outputs.items():
        target.write_bytes(output)
        print(f"PORT_SELECTOR_EVICTION: {target.relative_to(ROOT)} {sha(output)}")


if __name__ == "__main__":
    main()
