# Teddy tape checkpoint audit

Updated: 2026-08-22T12:31Z

## Identity and authority

- Isolated worktree: `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/redescent-teddy-tape-checkpoint`
- Branch: `research/redescent-teddy-tape-checkpoint`
- Exact base: `0d15561e2c2985f42e7a30a9518863726f77e353`
- Source family: X004 `clankerFARM`, descended from Teddy Pender's first promoted ping-pong circuit.
- Authority: local research only. No provider compute, nonce hunt, spend, submission, push, or public note.

This audit follows Teddy Pender's fresh recommendation to attack the tape or replace it with a different representation. The private `burn-the-house-down` `SKILL.md` and `CASE-STUDY.md` were fetched from `odinfree/burn-the-house-down` before the experiment. Teddy's doctrine supplied the method: state the overturn, price the cheapest falsifier, preserve the leader, and grind last.

## Frozen objective

Fresh live receipt supplied at the start of the audit:

```text
source = 7ca0559911b8cd423c4acc74fe152f332fce0c63
Q = 1278
T = 921558
score = 1177751124
```

The universal strict gate is `Q*T < 1177751124`. Exact integer ceilings:

```text
Q1266: T <= 930293
Q1270: T <= 927363
Q1278: T <= 921557
```

## Overturn

Claim under test:

> The 703-bit sign tape can be erased/checkpointed/recomputed cheaply enough to free replay headroom, widen the replay plot, and bring X004 under the current product gate.

Kill condition for the Bennett sub-route:

- an exact erase-and-recompute cycle has a gate tax that dominates the headroom without moving the measured peak.

The claim is closed only for ordinary Bennett/hierarchical recomputation on this ancestor. A different representation whose combined walk/replay map replaces the log without paying the measured recomputation tax remains strongly open.

## Exact binder inventory

Command:

```text
B0_WIN_LO=9671450 B0_WIN_HI=9671650 B0_PHASE=tlm_forward_multiply ./target/release/build_circuit
```

At the exact Q1266 binder (`tlm_forward_multiply`, op 9,671,531), the live set is:

```text
703  sign-tape qubits allocated by value_walk
256  caller y register
256  replay coefficient register
42   current replay-plot carries
4    retained replay boundary qubits
5    singleton controls/carries
=1266
```

The tape is therefore real co-resident width, not an off-peak allocation.

## Fresh baseline reproduction

Default env, forced release build:

```text
emitted operations = 15730117
ops SHA-256 = 843558da6f504e3f8f2f41cae1edeccdf0cfed9e0dc216f8e880ebc1752e7b75
Q = 1266
64-lane affine T = 1036334.453
emitted Toffoli = 1174483
affine classical/phase/ancilla assertions = clean
```

This exactly reproduces the X004 source fingerprint and metrics.

## Cheapest falsifier: grant free tape deletion

Before implementing a codec, grant the hypothesis an impossible advantage: all 703 tape qubits disappear at zero gate cost. With the freed headroom, widen the replay plot. The T figures below are fresh deterministic 64-lane affine measurements; the Q figures are the unmodified circuit before the hypothetical tape deletion.

| Replay plot | Measured Q | Q after free 703-tape deletion | Q with a 256-qubit code | Affine T | Coded score floor |
|---:|---:|---:|---:|---:|---:|
| 48 | 1266 | 563 | 819 | 1036334.453 | 848757917 |
| 64 | 1286 | 583 | 839 | 999425.000 | 838517575 |
| 96 | 1306 | 603 | 859 | 980761.953 | 842474518 |
| 128 | 1348 | 645 | 901 | 962451.328 | 867168647 |
| 256 | 1475 | 772 | 1028 | 943810.000 | 970236680 |

These are component lower bounds, not full-circuit Q claims: deleting 703 live tape qubits changes the binding composition, so the next global owner must be re-profiled rather than assumed to remain at Q1266. The corrected economics are highly favorable. Even the conservative 256-bit code plus a single 256-bit replay plot gives Q1028/T943810, score about 970.2M, and can spend another 201862 T before reaching the live product gate. The 48-bit plot has still more theoretical gate budget. A tape representation is therefore a leading route; only reconstructing the same raw history through Bennett is closed.

## Exact recomputation tax

An env-gated value-exact diagnostic was added:

```text
SUB4_PP_TEDDY_TAPE_RECOMPUTE_CYCLE=1
```

For each public traversal it runs `value_walk_back`, clearing the full sign tape and restoring the input, then runs `value_walk` again to reconstruct the exact state consumed by replay. The switch defaults off. It intentionally claims no width reduction; it measures the minimum full-history erase-and-rebuild tax.

Deterministic 64-lane full affine result:

```text
Q = 1266
affine T = 1431657.594
emitted Toffoli = 1569851
classical/phase/ancilla assertions = clean
delta affine T = +395323.141 (+38.1%)
```

Forced build result:

```text
emitted operations = 20949341
ops SHA-256 = 2bff6969cebeec6243d2d19dc4363568a86b659b743a48115c619d6229833710
peak = 1266, unchanged
```

The public accepted 7ca0559 descendant independently reports the same direction: Bennett/hierarchical checkpointing was rejected at about +30% T with no peak reduction. That evidence is premise-specific, not an axiom; this fresh X004 measurement reproduces the closure at +38.1%.

## Verdict and next action

`KILL` only ordinary tape erase/recompute and hierarchical checkpointing on X004. The first exact recomputation cycle adds 395k T while leaving Q flat.

`CONTINUE` tape replacement as a primary structural route. The zero-cost table shows enough product headroom for a 256-qubit code to pay substantial reversible encode/decode cost. The next falsifier must change the representation premise: preserve or encode the original 256-bit denominator, regenerate/stream the required sign decisions, and re-profile the new global binder. No full-history rebuild and no inference that Q remains 1266 after the tape disappears.

The accepted 7ca0559 descendant's `SUB4_PP_PEAK=1266` env-only test has separately been killed: measured Q remained 1278 while T rose. It does not test tape replacement and does not close this route.
