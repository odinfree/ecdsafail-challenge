# FLASH status (resumable) — updated 19:10Z

DEADLINE 2026-09-15T02:55:43Z. Model deepseek-flash max. Session 01a0a14a-0e89-7cc0-9269-072fb11a6e59.

## Bound parent
Official 88dc9f4 (welttowelt) Q793/T682,564,189. Worktree flash-bench @38c7fe6b
(reset 88dc9f4 onto harness 9700396), branch codex/flash-20260914.
Baked seven selectors ON; Q793_A18/A19 OFF.

## Route flash-a24 (claimed->implementing)
Support-gated A=253/254 pruning in q793_cargo_r02.rs.
- Flag Q793_CARGO_A_SUPPORT, default "0" in mod.rs (bake "1" only after gates).
- at()/below253() now take circ; a_pruned() = active(flag) && value!=255 && q797_a_support hi<=253.
- Blocks 0..124 (A_SUPPORTS hi<=253) are pruned; 125..201 must be bit-identical.
Falsifier: t-census per-block T: b0..124 drop only, b125..201 unchanged; whole-stream 0/0/0.

## Refreeze requirement
trailmix_port/mod.rs asserts EXACT (ops, structural_T) equality when
candidate_configuration() && codex10h_resources().is_some() (baked seven).
After A24 ON, must update codex10h_resources() to new measured totals
(require Q793_CARGO_A_SUPPORT active). Measure via whole-count panic printout
or t-census + whole-count eprintln.

## Gate chain (LOWQ_Q793_NATIVE_MODE)
t-census (~4 min, per-template T) -> whole-count (count-only whole, prints ops/T)
-> whole-stream (sprint 64-shot style, 0/0/0) -> whole-9024 (compact, ~50 min, RAM).
Baseline (flag OFF) first for identity; then flag=1.

## Next levers to scout
A22-FCFC flags, A29 R01 term-banks, A34 exit-transfer, A39/A40 small (verify
not already baked in build03). R01 low4 finding (849a3a6) fold support_end=3.
