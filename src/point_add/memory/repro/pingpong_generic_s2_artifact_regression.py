#!/usr/bin/env python3
"""Freeze the exact retained/hosted generic-s2 structural differential."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

from artifact_io import HEADER_BYTES, RECORD_BYTES, _zstd, fingerprint, read_header


EXPECTED = {
    "retained": {
        "compressed_ops_sha256": "af93e51e59be19c85ffcb9064509466d29319cbc07ce00a517aec142d4555c73",
        "canonical_semantic_sha256": "aa0a8bf1da523175e8899ddec457cb929f9728f30da9a5fd330472ea51031a3b",
        "emitted_ops": 12_507_123,
        "qubits": 1264,
        "max_referenced_qubit_id": 1263,
    },
    "hosted": {
        "compressed_ops_sha256": "25c20d0c516e68f5235c6a6d721fc1ff775353ac705b08215e196e2d846170cc",
        "canonical_semantic_sha256": "f079be7738e7cbb7c8d8293d2f72d1fb69985f983a502321be998da7cf5aea97",
        "emitted_ops": 12_508_426,
        "qubits": 1263,
        "max_referenced_qubit_id": 1262,
    },
}

EXPECTED_KIND_DELTA = [0] * 18
EXPECTED_KIND_DELTA[6] = 12  # X
EXPECTED_KIND_DELTA[8] = 1292  # CX
EXPECTED_KIND_DELTA[13] = -1  # one exact complement-control CCX deletion

EXTRA_DROP = re.compile(
    r"CONSTPROP_TRANSFORM label=affine index=5982787 "
    r"decision=DropComplementCtrls \{ a: QubitId\(645\), b: QubitId\(1215\) \} "
    r"kind=CCX controls=\(645, 1215\) target=1184 condition=18446744073709551615"
)
TOTAL = re.compile(
    r"CONSTPROP TOTAL iters=(?P<iters>\d+).*?aff_drop=(?P<aff_drop>\d+) "
    r"aff_fold=(?P<aff_fold>\d+)"
)


def random_kind_stream(path: Path) -> dict[str, object]:
    digest = hashlib.sha256()
    count = 0
    remainder = b""
    with path.open("rb", buffering=0) as source:
        _, emitted = read_header(source)
        source.seek(HEADER_BYTES)
        decoder = subprocess.Popen(
            [_zstd(), "-d", "-q", "-c"],
            stdin=source,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert decoder.stdout is not None
        while data := decoder.stdout.read(RECORD_BYTES * 1_000_000):
            data = remainder + data
            complete = len(data) - len(data) % RECORD_BYTES
            events = bytearray()
            for offset in range(0, complete, RECORD_BYTES):
                kind = struct.unpack_from("<I", data, offset)[0]
                if kind in (11, 12):
                    events.append(kind)
            digest.update(events)
            count += len(events)
            remainder = data[complete:]
        stderr = decoder.stderr.read().decode(errors="replace") if decoder.stderr else ""
        returncode = decoder.wait()
    if returncode != 0 or remainder:
        raise RuntimeError(f"invalid event stream: rc={returncode} remainder={len(remainder)} {stderr}")
    return {"emitted_ops": emitted, "events": count, "sha256": digest.hexdigest()}


def trace_summary(path: Path) -> dict[str, int | bool]:
    text = path.read_text(errors="replace")
    total = TOTAL.search(text)
    if total is None:
        raise AssertionError(f"missing CONSTPROP TOTAL in {path}")
    return {
        "iters": int(total.group("iters")),
        "aff_drop": int(total.group("aff_drop")),
        "aff_fold": int(total.group("aff_fold")),
        "has_exact_extra_drop": EXTRA_DROP.search(text) is not None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retained", type=Path, required=True)
    parser.add_argument("--hosted", type=Path, required=True)
    parser.add_argument("--retained-trace", type=Path, required=True)
    parser.add_argument("--hosted-trace", type=Path, required=True)
    args = parser.parse_args()

    retained = fingerprint(args.retained)
    hosted = fingerprint(args.hosted)
    for label, actual in (("retained", retained), ("hosted", hosted)):
        for key, expected in EXPECTED[label].items():
            assert actual[key] == expected, f"{label} {key}: {actual[key]} != {expected}"

    delta = [
        candidate - control
        for candidate, control in zip(
            hosted["operation_kind_counts"], retained["operation_kind_counts"]
        )
    ]
    assert delta == EXPECTED_KIND_DELTA, delta

    retained_events = random_kind_stream(args.retained)
    hosted_events = random_kind_stream(args.hosted)
    assert retained_events["events"] == hosted_events["events"] == 1_908_044
    assert retained_events["sha256"] == hosted_events["sha256"]

    retained_trace = trace_summary(args.retained_trace)
    hosted_trace = trace_summary(args.hosted_trace)
    assert retained_trace == {
        "iters": 2,
        "aff_drop": 2,
        "aff_fold": 2,
        "has_exact_extra_drop": False,
    }
    assert hosted_trace == {
        "iters": 2,
        "aff_drop": 3,
        "aff_fold": 2,
        "has_exact_extra_drop": True,
    }

    print(
        json.dumps(
            {
                "retained": retained,
                "hosted": hosted,
                "kind_delta_hosted_minus_retained": delta,
                "random_event_kind_stream": retained_events,
                "retained_constprop": retained_trace,
                "hosted_constprop": hosted_trace,
                "verdict": "GREEN_EXACT_COMPLEMENT_DROP_NORMALIZATION",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
