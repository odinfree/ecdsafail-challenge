# Direct Two-Register Affine-Shell Transducer Design

Status: approved for local structural falsification on 2026-08-24.

## Mission

Delete the complete `pp_mul_walk`, `pp_mul_replay`, and
`pp_mul_walkback` traversal from the promoted Q1266 point-add family. Replace
the second affine multiply callback with one exceptional-safe, two-register
reversible transducer. The campaign target is a whole-circuit score at least
10% below the promoted leader while preserving exact value, relative-phase,
and ancilla correctness.

This is a structural fork. It changes the multiplication algorithm, live state,
and cleanup strategy. A smaller ladder, width, round count, repair window,
nonce, or measurement threshold does not satisfy this design.

## Authoritative binding

- Research branch base commit:
  `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f`.
- Base tree and promoted tree:
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Promoted platform source:
  `522d00296ab014b0f4d128915b53851516f17f4d`.
- Promoted artifact: Q1266, rounded T911402, integer score
  `1,153,834,932`, official evaluator `0/0/0` over 9,024 shots.
- Protected leader worktree:
  `/Users/odin/Documents/coding with codin/ecdsafail-submit-q1266-odd-passenger`.
- Structural worktree:
  `/Users/odin/Documents/coding with codin/ecdsafail-structural-history-fiber`
  on `research/codex-affine-shell-transducer-20260824`.

The protected leader is read-only for this mission. Research results do not
become candidate, promotion, or submission evidence without a later clean
shipping bridge and the independent gates listed below.

## Current resource equation

The source-bound deterministic 64-lane profile of the promoted tree gives the
following screening equation:

```text
T_current                 = 911367.14
T_pp_mul_walk             =  95137.00
T_pp_mul_replay           =  17498.00
T_pp_mul_walkback         = 314210.00
T_complete_mul            = 426845.00
T_without_complete_mul    = 484522.14
Q_current                 = 1266
```

The diagnostic phase prices are screening evidence, not official score
components. The complete artifact is remeasured after every admitted source
change because measurement-stream movement can shift later executed-Toffoli
counts.

At unchanged Q1266 the replacement plus any new companion work must satisfy:

| Classification | Whole-score ceiling | Total-T ceiling | Replacement ceiling |
|---|---:|---:|---:|
| strict beat | `< 1,153,834,932` | `< 911402` | `< 426879.86` |
| 5% structural admission | `<= 1,096,143,185` | `<= 865831` | `<= 381308.86` |
| 10% campaign target | `<= 1,038,451,438` | `<= 820261` | `<= 335738.86` |

The 10% row is the mission target. The 5% row is an admission checkpoint, not
completion. A strict beat below 5% remains defense or research.

## Algebraic interface

At the current affine-shell boundary, after the first division and symmetric
square, the two live field registers are:

```text
T      = d + 3a - lambda^2 = a - x3
lambda = (y - b) / (x - a)
```

The classical point is `C=(a,b)`. Define totalized field operations:

```text
u(z)    = z if z != 0 else 1
iota(z) = inverse(u(z))
z0(T)   = 1 if T == 0 else 0
m(T)    = T if T != 0 else 1
lambda0 = 3*a^2*iota(2*b)
```

The replacement transducer consumes `(T,lambda)` and produces the final
quantum coordinates directly:

```text
X = a - T
Y = m(T)*lambda - b - z0(T)*lambda0
```

Its explicit mathematical inverse is:

```text
T      = a - X
lambda = (Y+b)/T          if T != 0
         Y+b+lambda0      if T == 0
d      = T - 3a + lambda^2
e      = lambda*u(d)
x      = d+a
y      = e+b
```

This map is a permutation of the complete two-register field space for every
fixed classical `(a,b)`. On valid curve inputs, the `T=0` branch maps the
`P=-2C` case to `-C` instead of collapsing the zero fiber.

## Required structural fingerprint

The admitted implementation must have all of these properties:

1. It replaces the complete second multiply traversal, not one cell or one
   schedule window.
2. The ABI contains only the two 256-bit quantum coordinate registers and two
   256-bit classical registers.
3. No third 256-bit quantum word remains live across the transducer.
4. No branch, quotient, sign, row, or path transcript grows linearly with the
   number of arithmetic iterations.
5. No old `lambda`, curve residual, zero flag, quotient word, or product word
   remains after the transducer.
6. The zero-fiber correction is computed and cleaned inside the same
   permutation.
7. The implementation has an explicit inverse or a source-level
   compute/action/uncompute proof that covers every scratch wire.
8. No exponential truth table, QROM, or width-specific synthesized permutation
   is credited as a scalable construction.

The historical direct-centered shadow at
`a5e8bdfd7e7c034ed67bc470ca2e26259a76236a` is archaeology only. Its envelope
uses 796 scratch qubits (Q1308 before point-add integration), retains 117
explicit branch bits, and prices the projected branch tail at 210,665 Toffoli
before a complete multiplier. Replaying that representation does not advance
this mission.

The previously measured TrailMix two-register shadow is also closed: it
retains a long history plus a temporary word, measures around Q1150/T628k for
the component, and fails an edge case. A new candidate must change the cleanup
representation rather than tune that implementation.

## Falsifier architecture

The first source-produced artifact is a reduced-width transducer laboratory,
not production Rust arithmetic. It has four layers.

### 1. Reference permutation

For an odd prime `p`, classical point `C=(a,b)`, and every `(x,y)` in `F_p^2`,
the oracle computes the totalized shell and its inverse. It exhaustively checks:

- `unshell(shell(x,y)) == (x,y)` for all states;
- the shell image has exactly `p^2` states;
- every valid curve input with `x != a` matches reference EC addition;
- valid and invalid `T=0`, `d=0`, `lambda=0`, and off-curve states;
- deterministic result hashes for provenance.

Required widths are two independently configured prime fields with at least
5-bit and 7-bit moduli. A third 8-bit-or-larger field is required before
production transfer if exhaustive runtime remains bounded.

### 2. Scalable action language

Candidate programs are expressed in a typed reversible action language. The
only admissible actions are parameterized field operations with explicit
inverses:

- in-place modular add/subtract between the two live words;
- add/subtract a classical constant;
- conditional add/subtract or negation under a clean one-bit predicate;
- swap or wire permutation;
- exact halve/double over the fixed prime field;
- zero/nonzero predicate compute and explicit uncompute;
- a bounded-width carry/length/location register whose width has a declared
  formula sublinear in `n`;
- measurement-uncompute only when its relative-phase repair is emitted and
  checked.

Every action publishes symbolic live-wire and emitted-Toffoli formulas. Search
may choose action order and bounded integer parameters. It may not insert an
arbitrary truth-table gate.

### 3. Forward-and-reverse executor

The executor applies a candidate program and its declared inverse to every
state at each reduced width. A survivor must preserve both input words required
by the action contract, return every scratch bit to zero, and accumulate no
relative phase. Branch predicates are recomputed from the declared live state;
they are never silently supplied by the oracle.

### 4. Resource projection

Projection is derived from action formulas, not fitted from wall-clock time.
For `n=256`, a survivor must satisfy:

```text
Q_component <= 1100
T_component + T_companions <= 335738.86
persistent_third_field_words = 0
linear_history_bits = 0
```

`Q_component <= 1100` prevents the new transducer from becoming the next deep
qubit wall. The whole circuit may initially remain Q1266 because the independent
division replay wall is outside this component. The component must nonetheless
leave enough shape for a later Q reduction.

## Verdicts

The reduced-width phase ends in exactly one evidence-backed verdict:

- `ADMIT`: the same normalized program passes at two widths, has an explicit
  scalable formula, satisfies the projected Q/T gates, and has no omitted
  cleanup.
- `HARD_NACK`: a predeclared invariant fails, including non-bijection, dirty
  scratch, phase dirt, hidden transcript growth, exponential lookup, third-word
  persistence, or conservative economics above the 10% ceiling.
- `COMPLETE`: reserved for an admitted implementation that later passes the
  production gates and reaches the declared discontinuity; it is not available
  to the reduced-width artifact alone.

Failure of one action grammar kills that grammar, not every possible circuit
for the mathematical permutation. The terminal receipt must state the exact
scope of the result.

## Production admission path

Only an `ADMIT` reduced-width receipt permits an opt-in Rust implementation.
The implementation sequence is:

1. Add a standalone transducer component behind a default-off environment
   switch.
2. Add exact small-width forward/inverse tests and production-width component
   resource census.
3. Insert it only at the second callback in `ec_add_with_division`; the first
   ping-pong division remains unchanged.
4. Assert that no `pp_mul_*` phase is emitted under the switch.
5. Run a clean release build and deterministic component self-check.
6. Run whole-source B0 owner census and 64-lane value/phase/ancilla gate.
7. Stop if global Q/T cannot reach at least the 5% structural threshold.
8. Run the frozen independent 9,024-shot evaluator only when the conservative
   whole-score equation passes.
9. Treat the result as research until a distinct clean shipping bridge
   reproduces it from the official base and all candidate gates pass.

The repository-wide `cargo test` target is already broken on the untouched
promoted tree by stale test-only symbols and simulator API references. That
baseline failure is not modified or waived. New work uses isolated tests,
`cargo build --release --locked --offline --bin build_circuit`, focused
component checks, and the independent evaluator. Any new failure in those
scoped gates is attributable to this mission.

## Authority and spending

This design grants local research authority only.

- Provider mutation: closed.
- Vast/RunPod spend: zero for the falsifier phase.
- Nonce grind: closed.
- Fleet and protected queue: closed.
- Push: closed unless separately authorized for this new branch.
- Public note: closed.
- Submission and promotion: closed.

The pingpong prefilter remains part of later candidate admission. It is not a
substitute for the deterministic algebra, cleanup, owner, or evaluator gates.

## Anti-rot checkpoints

- Ball owner: the controller in this task.
- Exact next action: implement the reduced-width oracle and action-language
  tests from a written plan.
- A structural tick requires a new source-produced falsifier, an overturned
  assumption, an architecture checkpoint, or a measured leading-term change.
- More samples, more prose, a new nonce, or a smaller local constant do not
  advance this mission.
- The protected leader remains available throughout the descent.

