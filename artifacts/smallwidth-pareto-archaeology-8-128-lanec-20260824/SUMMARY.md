# Reduced-width Pareto summary

Hypothesis origin: Justin Drake. Any promoted circuit win derived from this lane must credit him.

- Source: `67524171baaf568dc3dc606f38515745f70804ff`
- Widths: 8, 16, 32, 64, 96, 128
- Resource rows: 1164
- Detected peak-owner migrations: 18
- Detected qubit plateaus: 37
- Adder normalization: `Q/n`, `T/n`; `T/n^2` is retained for comparison with quadratic point-add stages.

## Boundary-repair lead

`topW_with_window_entry_carry` is locally exact, while `approximate_no_cin` has
uniform-input fault probability `2^-(W+1)`. Across measured widths/windows the exact
repair changes peak Q by [1] and emitted T by [0].
This is a candidate mechanism, not a 256-bit circuit win: the promoted route must still
prove or host the carry entering the top-W slice and re-run trusted validation.

## Lift classifications

- `boundary_repair` / `approximate_no_cin` at ratio 0.25: **constant_or_scale_specific** (CV Q/n=0.000, T/n=0.199).
- `boundary_repair` / `approximate_no_cin` at ratio 0.50: **finite_size_correction_needed** (CV Q/n=0.000, T/n=0.095).
- `boundary_repair` / `approximate_no_cin` at ratio 0.75: **finite_size_correction_needed** (CV Q/n=0.000, T/n=0.058).
- `boundary_repair` / `topW_with_window_entry_carry` at ratio 0.25: **constant_or_scale_specific** (CV Q/n=0.018, T/n=0.199).
- `boundary_repair` / `topW_with_window_entry_carry` at ratio 0.50: **finite_size_correction_needed** (CV Q/n=0.016, T/n=0.095).
- `boundary_repair` / `topW_with_window_entry_carry` at ratio 0.75: **finite_size_correction_needed** (CV Q/n=0.014, T/n=0.058).
- `co_binder_topclean` / `not_applicable` at ratio 0.00: **transferable_linear_mechanism** (CV Q/n=0.027, T/n=0.035).
- `co_binder_topclean` / `not_applicable` at ratio 0.25: **transferable_linear_mechanism** (CV Q/n=0.029, T/n=0.032).
- `co_binder_topclean` / `not_applicable` at ratio 0.50: **transferable_linear_mechanism** (CV Q/n=0.032, T/n=0.030).
- `co_binder_topclean` / `not_applicable` at ratio 0.75: **finite_size_correction_needed** (CV Q/n=0.054, T/n=0.028).
- `lowq` / `not_applicable` at ratio 0.00: **transferable_linear_mechanism** (CV Q/n=0.040, T/n=0.000).
- `topclean` / `not_applicable` at ratio 0.00: **transferable_linear_mechanism** (CV Q/n=0.027, T/n=0.000).
- `topclean` / `not_applicable` at ratio 0.25: **transferable_linear_mechanism** (CV Q/n=0.029, T/n=0.000).
- `topclean` / `not_applicable` at ratio 0.50: **transferable_linear_mechanism** (CV Q/n=0.032, T/n=0.000).
- `topclean` / `not_applicable` at ratio 0.75: **transferable_linear_mechanism** (CV Q/n=0.035, T/n=0.000).
