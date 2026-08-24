#!/usr/bin/env python3
import re
import subprocess
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(
    subprocess.check_output(
        ["git", "-C", str(HERE), "rev-parse", "--show-toplevel"], text=True
    ).strip()
)
PARENT_675 = "67524171baaf568dc3dc606f38515745f70804ff"
TASK4_BASE = "8457b8b5a57cde84a001f5b79fd0ae262638c014"


def git_output(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def tracked_rust_sources() -> list[Path]:
    output = git_output("ls-files", "-z", "--", "*.rs")
    return [ROOT / path.decode() for path in output.split(b"\0") if path]


def source(path: str) -> str:
    return (ROOT / path).read_text()


def committed_source(commit: str, path: str) -> str:
    return git_output("show", f"{commit}:{path}").decode()


def function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        raise AssertionError(f"missing function signature: {signature}")
    brace = text.find("{", start)
    if brace < 0:
        raise AssertionError(f"missing function body: {signature}")
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[brace + 1 : index]
    raise AssertionError(f"unterminated function body: {signature}")


class Task5SourceBypassGate(unittest.TestCase):
    def test_traced_builder_matches_frozen_task4_body_and_preserves_callers(self):
        text = source("src/point_add/pingpong_div.rs")
        traced = function_body(
            text,
            "pub(crate) fn build_pingpong_point_add_traced() -> TracedOps",
        )
        wrapper = function_body(
            text, "pub(crate) fn build_pingpong_point_add() -> Vec<Op>"
        )
        self.assertEqual(traced.count("circ.take_traced_ops()"), 1)
        self.assertIn("pp_profile::report(\n            &stream[..],", traced)
        self.assertRegex(traced, r"\bstream\s*$")
        self.assertEqual(
            re.sub(r"\s+", "", wrapper),
            "build_pingpong_point_add_traced().into_ops()",
        )
        self.assertEqual(traced.count("pp_profile::report("), 1)

        task4 = function_body(
            committed_source(TASK4_BASE, "src/point_add/pingpong_div.rs"),
            "pub(crate) fn build_pingpong_point_add() -> Vec<Op>",
        )
        normalized_traced = re.sub(r"\bstream\b", "ops", traced)
        normalized_traced = normalized_traced.replace("take_traced_ops", "take_ops")
        normalized_traced = normalized_traced.replace("&ops[..]", "&ops")
        self.assertEqual(
            re.sub(r"\s+", "", normalized_traced),
            re.sub(r"\s+", "", task4),
            "operation construction changed outside traced extraction/profiling",
        )

        selfcheck = function_body(
            text, "pub(crate) fn pingpong_point_add_simulator_selfcheck()"
        )
        self.assertEqual(selfcheck.count("let ops = build_pingpong_point_add();"), 1)
        self.assertNotIn("build_pingpong_point_add_traced()", selfcheck)

    def test_promoted_path_orders_one_exact_tail_before_one_audit(self):
        text = source("src/point_add/mod.rs")
        build = function_body(text, "pub fn build() -> Vec<Op>")
        start = build.index('if std::env::var_os("SUB4_LEGACY_POINT_ADD").is_none()')
        end = build.index("let mut ops = trailmix_ludicrous::build_trailmix_ludicrous_ops()")
        promoted = build[start:end]

        self.assertEqual(promoted.count("build_pingpong_point_add_traced()"), 1)
        self.assertNotIn("build_pingpong_point_add()", promoted)
        self.assertIn("let mut targets = [QubitId(0); 96];", promoted)
        self.assertEqual(promoted.count("append_synthetic_tail(&[x; 96])"), 1)
        self.assertEqual(promoted.count("rewrite_synthetic_tail_targets("), 1)
        self.assertEqual(promoted.count("dead_gate_audit::audit_and_write("), 1)
        self.assertNotIn("apply_tail_nonce(", promoted)
        self.assertIn(
            re.sub(
                r"\s+",
                "",
                'std::env::var("SUB4_PINGPONG_TAIL_NONCE")\n'
                ".unwrap_or_default()\n"
                ".parse::<u64>()\n"
                ".unwrap_or(8107117281543)",
            ),
            re.sub(r"\s+", "", promoted),
        )

        targets_at = promoted.index("let mut targets = [QubitId(0); 96];")
        append_at = promoted.index("append_synthetic_tail(&[x; 96])")
        rewrite_at = promoted.index("rewrite_synthetic_tail_targets(")
        audit_flag_at = promoted.index("if j3_dead_gate_audit_enabled()")
        working_directory_at = promoted.index("let working_directory = std::env::current_dir()")
        audit_at = promoted.index("dead_gate_audit::audit_and_write(")
        return_at = promoted.index("return stream.into_ops();")
        self.assertLess(targets_at, append_at)
        self.assertLess(append_at, rewrite_at)
        self.assertLess(rewrite_at, audit_flag_at)
        self.assertLess(audit_flag_at, working_directory_at)
        self.assertLess(working_directory_at, audit_at)
        self.assertLess(audit_at, return_at)

        raw_stream_mutation = (
            r"\b(?:stream|ops)\s*(?:\[[^]]+\]\s*="
            r"|\.\s*(?:push|extend|truncate|reverse|splice|retain)\s*\()"
        )
        self.assertNotRegex(promoted, raw_stream_mutation)

    def test_tracked_rust_has_no_mutation_escape_or_second_audit_call(self):
        paths = tracked_rust_sources()
        self.assertTrue(paths)
        combined = "\n".join(path.read_text() for path in paths)
        for forbidden in ["DerefMut", "IndexMut", "ops_mut"]:
            self.assertNotIn(forbidden, combined)
        self.assertEqual(combined.count("dead_gate_audit::audit_and_write("), 1)

        pingpong = source("src/point_add/pingpong_div.rs")
        traced = function_body(
            pingpong,
            "pub(crate) fn build_pingpong_point_add_traced() -> TracedOps",
        )
        after_take = traced.split("circ.take_traced_ops()", 1)[1]
        self.assertNotRegex(
            after_take,
            r"stream\s*(?:\[[^]]+\]\s*="
            r"|\.\s*(?:push|extend|truncate|reverse|splice|retain)\s*\()",
        )

    def test_parent_675_venting_blob_and_twelve_pushes_are_unchanged(self):
        current = (ROOT / "src/point_add/venting.rs").read_bytes()
        parent = git_output("show", f"{PARENT_675}:src/point_add/venting.rs")
        self.assertEqual(current, parent)
        self.assertEqual(
            len(re.findall(rb"^\s*b\.ops\.push\(op\);\s*$", current, re.MULTILINE)),
            12,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
