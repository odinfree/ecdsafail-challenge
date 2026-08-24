# Reduced-width structural probes

Originating hypothesis: Justin Drake proposed autoresearch on smaller adders,
such as 64-bit instead of 256-bit, to reveal hidden Pareto steps faster and
then test whether the mechanisms lift.

`chunk_boundary_oracle.py` is the first falsifier. It exhaustively checks the
phase-repair identity used when a measured carry crosses a replay-adder chunk
boundary. The current implicit-zero repair is approximate. Supplying the
carry that enters the retained top window makes the Boolean oracle exact.

This does **not** yet prove a circuit win. The candidate still needs a
reversible checkpoint schedule that retains or recomputes the window-entry
carry, discharges it phase-cleanly, and improves the 256-bit whole-circuit
qubit/Toffoli product. Small-width constants and tail nonces do not transfer.

Run:

```bash
python3 research/small_width/chunk_boundary_oracle.py --max-chunk-width 10 \
  > research/small_width/chunk-boundary-results.jsonl
```
