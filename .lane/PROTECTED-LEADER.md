# Protected leader: exact `6b5c82c`

Updated: 2026-08-22T20:30:05Z

This file protects the live artifact while a separate Burn-the-House-Down
descent challenges its assumptions. Teddy Pender supplied the operating method:
protect the leader, file executable overturns, replay the descent, compose
across ancestors, and grind last. The current doctrine was refreshed from
`odinfree/burn-the-house-down` at `b6ad6381029ce4893e368b0ab677a03698eb607c`.

## Live receipt

| field | frozen value |
|---|---|
| benchmark | `gpsanant/ecdsafail-challenge` |
| live check | `2026-08-22T20:30:05Z` |
| source | `Layr-Labs/ecdsafail-challenge` `main` |
| source identity | `6b5c82cbe723b33c296c8926876f14f1ac3307a8` |
| submission | `32cf5c7` |
| solver | `moscowchill` |
| peak qubits | `1278` |
| average executed Toffoli | `918357.924`, rounded to `918358` |
| score | `1278 * 918358 = 1173661524` |
| status | promoted |
| CLI close | `1/1/27, 12:59 AM`, as rendered in `Europe/Zurich` |

The CLI close string is preserved verbatim. It must be reopened before any
future shipping decision rather than converted into an assumed server-side
timestamp.

## Objective and strict gate

The trusted evaluator computes:

```text
T = round(average executed CCX + CCZ across 9,024 shots)
score = peak_qubits * T
strict win at Q1 iff Q1 * T1 < 1,173,661,524
strict maximum rounded T at Q1 = floor((1,173,661,524 - 1) / Q1)
```

At unchanged Q1278, a new candidate needs rounded `T <= 918357`.

The editable construction remains under `src/point_add/**`. The trusted
contract is the unchanged evaluator over all 9,024 Fiat-Shamir shots with
classical mismatches, phase-garbage batches, and ancilla-garbage batches all
exactly `0/0/0`. Campaign filters, short samples, component self-tests, and
nonce screens cannot replace that contract.

## Forced clean reproduction

The normal path was reproduced from a clean `git archive` of the full source
identity, with a new target directory and no inherited `ops.bin`, `target`, or
environment override:

```bash
BURN_REPRO_TMP=$(mktemp -d)
BURN_CC=$(command -v clang || command -v cc)
git archive --format=tar 6b5c82cbe723b33c296c8926876f14f1ac3307a8 \
  | tar -xf - -C "$BURN_REPRO_TMP"
(
  cd "$BURN_REPRO_TMP"
  CC="$BURN_CC" CARGO_NET_OFFLINE=true RUSTFLAGS="-C linker=$BURN_CC" \
    cargo build --release --locked --offline \
      --bin build_circuit --bin eval_circuit
  mkdir emitted
  (
    cd emitted
    ../target/release/build_circuit
    ../target/release/eval_circuit --note burn-clean-reproduction-6b5c82c
  )
  shasum -a 256 emitted/ops.bin score.json
)
```

Observed receipt:

- emitted operations: `12,950,916`
- stream SHA-256: `88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb`
- `score.json` SHA-256: `c33c8d2ead08a6c37b993ac5f6b0ae6599dda90c0d123baacc3d7844ee5027c7`
- Q/T/score: `1278 / 918357.924 -> 918358 / 1173661524`
- trusted 9,024-shot result: classical `0`, phase `0`, ancilla `0`

No generated stream, score, build target, or temporary evaluator is present in
this worktree.

## Exact-live peak census

`PROFILE_ACTIVE_TIMELINE=1 PP_PROFILE=1` preserved the normal stream hash and
found a three-way Q1278 plateau:

| phase | peak Q | peak operation | exact-live owner summary |
|---|---:|---:|---|
| `pp_div_replay` | 1278 | 2,643,328 | 355 walk/tape, 256 active replay numerator `y`, 256 replay coefficient, 128 replay carry block, plus residual state |
| `square_product_register` | 1278 | 6,770,626 | 258 product, 247 shell allocation, two 129-wide square families, and restored divide state |
| `pp_mul_walkback` | 1278 | 8,976,984 | 563 walk/tape, 256 caller `y`, 256 replay allocation, and walkback ladders |
| `pp_mul_replay` | 1276 | phase maximum | near-binder, two qubits below the plateau |

The three `B0_CENSUS` diagnostics and the profiler each emitted the same normal
stream hash above. This census is evidence about `6b5c82c`, not a law about a
future architecture.

## Adjacent accepted delta

`6b5c82c` is the direct child of `9805dee`. The accepted source delta is:

- fixed ping-pong depth `698 -> 694`;
- endpoint fold window `20 -> 26`;
- tail nonce `68367898080254 -> 1400958`.

The public score moved from Q1278/T919754 to Q1278/T918358. The nonce is a
source-bound search artifact. The depth/window trade is evidence to remeasure,
not an axiom for the clean descent.

## Separation rule

This worktree is research-only. It may not hunt, use provider capacity, submit,
push, publish, or replace the protected leader from a component receipt. A
future structural winner must cross a fresh official-base shipping tree and the
full unchanged trusted contract.

If such a winner later qualifies, the public model sentence is exactly:
`Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.` The API
attribution remains exactly `kimi`. This seed commit makes no public claim.
