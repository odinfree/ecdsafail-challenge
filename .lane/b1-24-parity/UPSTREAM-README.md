# `pingpong_filter` — a classical prefilter for grinding the tail nonce

The ping-pong point-add circuit is built with a Fiat–Shamir tail nonce
(`SUB4_PINGPONG_TAIL_NONCE`, `src/point_add/mod.rs`). `eval_circuit` demands a
*perfect* run — 0 classical mismatches, 0 phase-garbage batches, 0 ancilla-garbage
batches across all 9,024 draws — so landing a submission means grinding nonces until
one comes up clean.

Done blind, that is ~0.06 nonces/s (a full `build_circuit` + `eval_circuit` each).
This tool predicts a nonce's **`classical mismatches` count exactly**, without building
or simulating the 13.0M-op stream:

| pipeline | nonces/s | vs blind |
|---|---|---|
| blind `build_circuit` + `eval_circuit` | 0.06 | 1× |
| `pingpong_filter` (CPU, 16 threads) | ~13 | ~215× |
| `pingpong_gpu --screen` (one RTX 4090) | ~12,800 | ~210,000× |

## It is a SCREEN, not a VALIDATOR

It models the **classical** channel only. The **phase** channel is invisible to it, so
every classically-clean survivor still needs a real `eval_circuit` confirm. In our runs
roughly 1 survivor in 300 was a true island at the configuration we shipped.

Practically: use the GPU to reduce millions of nonces to hundreds of candidates, then
confirm those candidates properly.

## How it works

It ports the divider's classical value model (walk, fold, replay, round-0 lift) and
reuses a **nonce-independent SHAKE256 prefix checkpoint** — the expensive sponge work is
done once (~2.7 s), after which each nonce costs ~2 ms on CPU. The nonce only perturbs
the SHAKE digest, so the circuit's function, Toffoli count and qubit count are all
nonce-invariant; only the 9,024 test inputs change.

## Build

CPU (from the benchmark repo root):

```bash
cp pingpong_filter.rs src/bin/
printf '\n[[bin]]\nname = "pingpong_filter"\npath = "src/bin/pingpong_filter.rs"\n' >> Cargo.toml
cargo build --release
```

CUDA:

```bash
cd gpu_filter && bash build.sh      # nvcc -arch=sm_89 -O3 ...
```

`build.sh` shells through `vcvars64.bat` on Windows — a bare `nvcc` from Git Bash fails
with `nvcc fatal : Cannot find compiler 'cl.exe' in PATH`.

## Use

```bash
# 1. fingerprint + checkpoint for THIS circuit configuration
pingpong_filter --dump-checkpoint ck.bin        # prints the op count

# 2. screen a range on the GPU (0 = classically clean)
pingpong_gpu --checkpoint ck.bin --ops <count> --from A --to B \
             --screen --batch 524288 --window 512

# 3. confirm every survivor for real
SUB4_PINGPONG_TAIL_NONCE=<n> build_circuit && SUB4_PINGPONG_TAIL_NONCE=<n> eval_circuit
```

Other modes: `--nonces <file>` scores an explicit list (the checkpoint cost is paid once,
not per nonce); default mode prints exact counts and is diffable against the GPU;
`PF_PHASE=1` adds the phase-ordering column described below.

## The model must match your circuit

The filter carries the divider's tuned windows as compiled-in defaults, overridable by
the same env vars the circuit reads:

```
SUB4_PP_ROUNDS  SUB4_PP_ROUNDS_MUL  SUB4_PP_REPLAY_FOLD_WINDOW  SUB4_PP_ENDPOINT_FOLD_WINDOW
```

It also hardcodes `value_width`'s schedule constants (`BREAK_1/2`, `SLOPE_1/2/3`, `MARGIN`).
**These drift.** As shipped they match frontier commit `8d7051b` (`rounds_mul = rounds()-2`,
`endpoint = 20`, `SLOPE_2 = 34`). A stale constant produces a silently wrong screen.

The compare widths (`SUB4_PP_REPLAY_CHUNK_COMPARE`, `SUB4_PP_REPLAY_FLAG_COMPARE`) are
deliberately **absent** from the model: they feed `cmp_lt_phase_conditioned` off an `hmr`
residual and are provably value-preserving (`arith/compare.rs`), so they cannot change a
classical count. Measured flat across 8 configurations at n=300 nonces each.

## Guards — please actually use these

Each of these caught a real, silent failure for us:

1. **Assert the commit.** `git checkout` of a commit your clone does not have *fails
   without stopping your script*. We swept an entire knob matrix against the wrong head
   before noticing the peak qubit count was 4 too high.
2. **Cross-check GPU against CPU on ~32 nonces and abort on mismatch**, before every
   screen. It costs about a second. It is the only thing that catches a patched-but-not-
   rebuilt `.cu` — the model constants live in both the source *and* the compiled binary.
3. **Treat the `--ops` fingerprint as a hard error, not a warning.** The checkpoint is
   valid only for the exact circuit that produced it.
4. **Sanity-check the survivor count against `e^-λ_c`.** A factor-of-two miss means the
   model is wrong. That is how we caught guard 2 failing.

**Islands never survive a configuration change.** Any knob edit changes the op stream,
which reseeds SHAKE256, which redraws all 9,024 inputs. Regenerate the checkpoint and
re-grind after any edit — and never compare per-nonce counts between two configurations,
because they share zero test inputs.

## Optional: phase-ordering (`PF_PHASE=1`)

The phase channel is deterministic — the simulator's `phase` is a plain `u64`, one lane
per shot, mutated only by XOR of Boolean functions of classical values. An `hmr`'s random
outcome is stored in a classical bit and the paired fixup is gated on that same bit, so
the pair's net phase is zero exactly when a purely classical predicate holds. The
randomness cancels.

For the two flag-repair sites that gives, with `S` the raw 256-bit sum, `D` the addend and
`w` the compare width:

```
residual = 1  iff  S[256-w..] == D[256-w..]  AND  S[..256-w] < D[..256-w]
```

`PF_PHASE=1` emits `K` = the number of shots carrying at least one predicted residual.
**Confirm survivors in ascending K.** Validated on 565 survivors with 4 known islands: all
four sat at K ≤ 3, the bottom 22% of the distribution (p ≈ 0.002 against the null) — a
~4.6× cut in confirms. On a later run the island surfaced in the first 24 of 296 confirms.

Two cautions:

- **Do not turn this into a rejection filter.** Each residual flips its lane with
  probability exactly ½, so `P(batch clean | k residuals) = 2^-k`. Rejecting any nonce
  with a predicted residual is a *superset* screen with acceptance `e^(-2λ_p)` instead of
  `e^(-λ_p)` — dramatically worse. Use K for **ranking only**.
- **K is an undercount.** It covers the flag sites but not the chunk-erase sites
  (`pingpong_div.rs`, the `erase` closure in `add_chunked_measured_with`), so `2^-K`
  overstates the pass rate and islands come back at K = 2–3 rather than 0. The chunk
  boundaries are derived from the interleaving plan rather than the data, so they are
  identical for every nonce and shot and can be dumped once — that is the natural way to
  finish the predictor.

A walk-shrink predicate is **not** worth adding: the width-shrink frees a wire after
`cx(u[lu-2], u[lu-1])`, which looks like a dirty-free source, but `walk_round` writes
`top = bit(w-1) ^ bit(w-2)` on every step, so the walk keeps itself sign-extended and the
freed wire is always clean. We implemented it and measured exactly zero contribution.

## Validation

- **Zero false negatives.** 5,563 nonces cross-checked in both directions in an
  independent audit, plus 200/200 and 44/44 exact GPU-vs-CPU agreement on the shipped
  configuration. The fatal direction (screen says dirty, truth says clean — discarding a
  good nonce) has never been observed.
- **Chain closed against `eval_circuit`.** `classical mismatches` equalled the prediction
  in every cross-checked evaluator run, including across three different circuits whose
  knob changes moved the op stream.
- **Known imperfection:** ~7 of 565 survivors in one run had nonzero classical mismatches
  under `eval_circuit` — false *positives* (wasted confirms, not lost islands). Not yet
  characterised.
