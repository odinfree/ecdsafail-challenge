#!/usr/bin/env python3
"""Compose the sealed Q1273 phase trace onto the repaired classical model.

This is deliberately a hash-bound three-way source transform.  The phase
donor contributes trace-only helpers and immutable schedule fixtures.  The
repaired target keeps its finite-width walk/terminal/replay semantics.
"""

from __future__ import annotations

import hashlib
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[3]
PHASE_COMMIT = "031083cc"
BASE_COMMIT = "41df51a"
MODEL = pathlib.Path(".lane/q1273-predictor/src/pp_model.h")

EXPECTED_BASE = "8e97b9b94d313e05bbe7fb844a53381b17c9c3fbd027a744feb41edaa993976d"
EXPECTED_REPAIRED = "da56cb95e2c423e67e8d400b423117cc54d007505aa7281e7725bcadd2ea19ab"
EXPECTED_PHASE = "0a82f88f4bb262e7a8578800febcaca6d58fe0ec362b4bf689bea2ddd9a38b9a"
EXPECTED_AUTO_MERGE = "8cebbeaadeba3a646436a0fb0ba10f15bc58102da215912090fb55de3efca4c6"

IMPORTS = {
    ".lane/q1273-phase/Q1273_PHASE_FIXTURES.tsv":
        "e148f24d99ae45b3c6930a33d49173fd31b2c236593d98375956077b3feb4d1b",
    ".lane/q1273-phase/Q1273_PHASE_SCHEDULE.tsv":
        "a4043530337b91e97d7a42dde2aff7e5a967a0b820ad1a9a120b3c366d7a5294",
    ".lane/q1273-phase/src/pp_phase_schedule.h":
        "4249864aca9e2928a33865ea086b99ef8ecccc9eb596ba4c3e57468ba88d25e5",
    ".lane/q1273-phase/tools/generate_phase_schedule.py":
        "83bfa142f2cf546ea5673de424597bf26ed3a57db0173d2b177a009ad9f8e966",
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_show(spec: str) -> bytes:
    return subprocess.run(
        ["git", "show", spec], cwd=ROOT, check=True, stdout=subprocess.PIPE
    ).stdout


OLD_TRACE = r'''PP_HD u32 pp_shot_fault_phase_trace_s(const u64 tx[4], const u64 ty[4], const u64 ox[4],
                                      const u64 oy[4], const u64 lam[4], u64 signs_d[11],
                                      u64 signs_m[11], const u16* wtab, PP_PhaseTrace* tr) {
    u64 rx[4], ry[4];
    pp_expected_add(tx, ty, ox, oy, lam, rx, ry);

    u64 x2[4], y2[4];
    pp_coord_sub_phase_model(tx, ox, x2, tr);
    pp_coord_sub_phase_model(ty, oy, y2, tr);

    bool wd_fault, wd_term_ok, wd_u_neg, wd_v_neg;
    pp_walk_sig(x2, PP_ROUNDS_DIV, &wd_fault, &wd_term_ok, &wd_u_neg, &wd_v_neg, signs_d, wtab);
    if (wd_fault || !wd_term_ok || pp_walkback_fold_fault(x2)) return PP_F_WALK_DIV;

    u64 xd[4], y2d[4];
    pp_divide_replay_phase(y2, signs_d, wd_u_neg, wd_v_neg, xd, y2d, tr);
    if (!pp_eq(xd, y2d)) return PP_F_REPLAY_DIV;

    u64 three[4], x2b[4], x2c[4];
    pp_fadd(ox, ox, three);
    pp_fadd(three, ox, three);
    pp_mod_add_exact_model(three, x2, x2b);
    pp_square_phase_model(y2d, x2b, x2c, tr);

    if (pp_is_zero(x2c)) return PP_F_WALK_MUL;
    bool wm_fault, wm_term_ok, wm_u_neg, wm_v_neg;
    pp_walk_sig(x2c, PP_ROUNDS_MUL, &wm_fault, &wm_term_ok, &wm_u_neg, &wm_v_neg, signs_m, wtab);
    if (wm_fault || !wm_term_ok || pp_walkback_fold_fault(x2c)) return PP_F_WALK_MUL;

    u64 xm[4], y2m[4];
    pp_multiply_replay_phase(y2d, signs_m, wm_u_neg, wm_v_neg, xm, y2m, tr);
    if (!pp_is_zero(xm)) return PP_F_REPLAY_MUL;

    u64 y2f[4], x2f[4];
    pp_coord_sub_phase_model(y2m, oy, y2f, tr);
    pp_coord_rsub_model(x2c, ox, x2f);
    if (!pp_eq(x2f, rx) || !pp_eq(y2f, ry)) return PP_F_RESULT;
    return 0;
}'''

NEW_TRACE = r'''PP_HD u32 pp_shot_fault_phase_trace_s(const u64 tx[4], const u64 ty[4], const u64 ox[4],
                                      const u64 oy[4], const u64 lam[4], u64 signs_d[11],
                                      u64 signs_m[11], const u16* wtab, PP_PhaseTrace* tr) {
    u64 rx[4], ry[4];
    pp_expected_add(tx, ty, ox, oy, lam, rx, ry);

    u64 x2[4], y2[4];
    pp_coord_sub_phase_model(tx, ox, x2, tr);
    pp_coord_sub_phase_model(ty, oy, y2, tr);

    bool wd_fault, wd_term_ok, wd_u_neg, wd_v_neg;
    pp_walk_sig(x2, PP_ROUNDS_DIV, &wd_fault, &wd_term_ok, &wd_u_neg, &wd_v_neg, signs_d, wtab);
    u64 x2_after_div[4];
    for (int i = 0; i < 4; i++) x2_after_div[i] = x2[i];
    if (wd_fault) {
        pp_walk_wrapped_restore(x2, PP_ROUNDS_DIV, signs_d, &wd_u_neg, &wd_v_neg,
                                x2_after_div, wtab);
    } else if (!wd_term_ok || pp_walkback_fold_fault(x2)) {
        return PP_F_WALK_DIV;
    }

    u64 xd[4], y2d[4];
    pp_divide_replay_phase(y2, signs_d, wd_u_neg, wd_v_neg, xd, y2d, tr);
    if (!pp_eq(xd, y2d)) return wd_fault ? PP_F_WALK_DIV : PP_F_REPLAY_DIV;

    u64 three[4], x2b[4], x2c[4];
    pp_fadd(ox, ox, three);
    pp_fadd(three, ox, three);
    pp_mod_add_exact_model(three, x2_after_div, x2b);
    pp_square_phase_model(y2d, x2b, x2c, tr);

    if (pp_is_zero(x2c)) return wd_fault ? PP_F_WALK_DIV : PP_F_WALK_MUL;
    bool wm_fault, wm_term_ok, wm_u_neg, wm_v_neg;
    pp_walk_sig(x2c, PP_ROUNDS_MUL, &wm_fault, &wm_term_ok, &wm_u_neg, &wm_v_neg, signs_m, wtab);
    u64 x2_after_mul[4];
    for (int i = 0; i < 4; i++) x2_after_mul[i] = x2c[i];
    if (wm_fault) {
        pp_walk_wrapped_restore(x2c, PP_ROUNDS_MUL, signs_m, &wm_u_neg, &wm_v_neg,
                                x2_after_mul, wtab);
    } else if (!wm_term_ok || pp_walkback_fold_fault(x2c)) {
        return wd_fault ? PP_F_WALK_DIV : PP_F_WALK_MUL;
    }

    u64 xm[4], y2m[4];
    pp_multiply_replay_phase(y2d, signs_m, wm_u_neg, wm_v_neg, xm, y2m, tr);
    if (!pp_is_zero(xm)) {
        if (wd_fault) return PP_F_WALK_DIV;
        return wm_fault ? PP_F_WALK_MUL : PP_F_REPLAY_MUL;
    }

    u64 y2f[4], x2f[4];
    pp_coord_sub_phase_model(y2m, oy, y2f, tr);
    pp_coord_rsub_model(x2_after_mul, ox, x2f);
    if (!pp_eq(x2f, rx) || !pp_eq(y2f, ry)) {
        if (wd_fault) return PP_F_WALK_DIV;
        return wm_fault ? PP_F_WALK_MUL : PP_F_RESULT;
    }
    return 0;
}'''


def main() -> None:
    target = ROOT / MODEL
    current = target.read_bytes()
    if sha(current) != EXPECTED_REPAIRED:
        raise SystemExit(f"compose-phase: repaired input hash mismatch: {sha(current)}")

    base = git_show(f"{BASE_COMMIT}:{MODEL}")
    phase = git_show(f"{PHASE_COMMIT}:{MODEL}")
    if sha(base) != EXPECTED_BASE or sha(phase) != EXPECTED_PHASE:
        raise SystemExit("compose-phase: base or phase donor hash mismatch")

    with tempfile.TemporaryDirectory(prefix="q1273-phase-merge.") as tmp_name:
        tmp = pathlib.Path(tmp_name)
        paths = []
        for name, raw in (("current", current), ("base", base), ("phase", phase)):
            path = tmp / name
            path.write_bytes(raw)
            paths.append(path)
        merged = subprocess.run(
            ["git", "merge-file", "-p", *(str(path) for path in paths)],
            cwd=ROOT,
            stdout=subprocess.PIPE,
        )
        if merged.returncode != 0 or b"<<<<<<<" in merged.stdout:
            raise SystemExit("compose-phase: three-way merge conflict")
        if sha(merged.stdout) != EXPECTED_AUTO_MERGE:
            raise SystemExit(f"compose-phase: auto-merge hash mismatch: {sha(merged.stdout)}")

    text = merged.stdout.decode("utf-8")
    if text.count(OLD_TRACE) != 1:
        raise SystemExit("compose-phase: donor trace surface is not unique")
    text = text.replace(OLD_TRACE, NEW_TRACE)
    target.write_text(text, encoding="utf-8", newline="\n")

    for relative, expected in IMPORTS.items():
        raw = git_show(f"{PHASE_COMMIT}:{relative}")
        if sha(raw) != expected:
            raise SystemExit(f"compose-phase: import hash mismatch: {relative}")
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    print(f"compose-phase: PASS model_sha256={sha(target.read_bytes())}")
    for relative in IMPORTS:
        print(f"{sha((ROOT / relative).read_bytes())}  {relative}")


if __name__ == "__main__":
    main()
