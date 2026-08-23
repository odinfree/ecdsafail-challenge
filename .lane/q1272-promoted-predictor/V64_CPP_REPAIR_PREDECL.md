# Promoted Q1272 wrapped-restore C++ repair predeclaration

Date: 2026-08-23

Verdict before edit: `PREDECLARED / NO_MODEL_EDIT_YET / CUDA_HOLD`.

The frozen V64 reveal proves one shared-C++ false negative at nonce
`90522024612912`, shot `2544`: corrected Rust and the unchanged trusted
evaluator both report a classical fault, while the C++ model returns clean.
The trusted fault channel is `PP_F_WALK_MUL` (`mask=4`). Division traversal is
clean and terminal-valid on the witness.

The cause is bounded to the overflow-only walk fallback. The current C++
`pp_wrapped_output_correct` records wrapped signs but silently substitutes the
ideal pre-walk denominators (`x2` and `x2c`) after lossy traversal. The circuit
instead canonicalizes the terminal passenger registers to signed `+/-1`,
walks them back through the fixed-width recurrence, and carries the restored
denominator into the subsequent shell. Reusing `x2c` makes shot 2544 appear
clean; using the restored multiply denominator produces `PP_F_WALK_MUL`.

## Frozen inputs

- target structural commit:
  `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- target ops SHA-256:
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- current model SHA-256:
  `120979945f82318e9df77014fabea3d2f8a9dea3c433e1ff5636cb3cb654424b`;
- current host SHA-256:
  `b635c95deb5bab2b89ea65de4dafdba22ea4184a647c82d4bb5680450f976435`;
- current CPU driver SHA-256:
  `37550fe3d8d1f1130cdc03a746ed5b4ea6bdb619475eebcddaeb087342457352`;
- V64 nonce corpus SHA-256:
  `9db8b3a0fc0f277f8cea77cac181cc6133a667c96d5e73a97397a7116a6ec1bd`;
- sealed Rust V64 prediction SHA-256:
  `c3f5bf182ab37716e9dfaa03174de35ce703099ceb2c845a2c9e720b840ad862`;
- trusted V64 summary SHA-256:
  `8f398581aaedfaa629ce15db4322e99dd463eed662fdab8c23063776553e6fea`.

## Exact committed donor and bounded edit

The only semantic donor is the committed and pushed CPU handoff
`83ad631e1a99db3db1c3886b4d61ff9ded94b0f5`, tree
`e96c542e73c8b265eadfe3c4bbcb71df1096a024`. Its complete `pp_model.h`
SHA-256 is
`0d4c9a812892b9dac598cb59a8345c443b9e21663ac29743578f4e651b39b92a`.
No uncommitted file is eligible.

The repair is limited to the donor's source-equivalent classical recurrence:

1. replace `pp_walk_sig_wrapped` with `pp_s320_pm1`,
   `pp_walk_wrapped_forward`, `pp_round0_reverse_sparse`, and
   `pp_walk_wrapped_restore`;
2. replace `pp_wrapped_output_correct` with `pp_wrapped_shell_correct`;
3. feed `x2_after_div` into `pp_mod_add_exact_model` and
   `x2_after_mul` into the final `pp_coord_rsub_model`;
4. switch only the two existing overflow fallback call sites to the repaired
   shell.

Phase-trace code, phase tables, Q1273 data, unrelated model changes, and
driver behavior are explicitly outside this edit.

## Frozen gates

After the edit, the exact shot-2544 witness must return mask `4`, then the
shared C++ model must reproduce every complete Rust/trusted classical mask on
inherited + H64 + spent D32 + revealed V64. Any new false positive, false
negative, crash, source mismatch, or nondeterminism is a hard stop.

If retrospective parity passes, a new deterministic disjoint holdout must be
predeclared and sealed before trusted reveal. V64 is spent and cannot be reused
as the terminal holdout. CUDA compilation, provider activation, scan ranges,
hunting, and submission remain disabled.
