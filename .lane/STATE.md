# Fable takeover: exact-live dead-low descent

Created: 2026-08-22
Source: `6b5c82c`
Branch: `research/fable-deadlow-6b5c`
Status: active bounded Fable falsifier; no hunt or submission authority

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

Execution provenance: Claude Fable 5, max effort, took over the unfinished
Kimi dead-low objective after the Kimi account reached its cycle limit. The
campaign model declaration above is preserved verbatim; this lane does not
conceal who ran the actual experiment.

## Protected leader and transfer boundary

- Exact live source: `6b5c82c`.
- Live receipt at transfer: Q1278 / rounded T918358 / score1173661524.
- Strict unchanged-Q beat requires rounded T at most 918357.
- Gate-off control: 12,950,916 operations and SHA-256
  `88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb`.
- No nonce hunt, provider work, spend, push, publication, or submission.

## Teddy Pender overturn

The stale `9805dee` Kimi audit proved that four tempting modular call sites
were unreachable from the production ping-pong path. It also proved the live
dead-low candidates already promoted there. Do not repeat those sites.

Assumption to overturn: the exact `6b5c82c` ping-pong path has no additional
constant or caller-proved low carry/borrow position that can be skipped without
changing emitted state, phase, or cleanup.

Cheapest falsifier: source-index every live carry/borrow ladder invoked from
`build_pingpong_point_add`; enumerate its bit-zero predicate and invocation
count; discard any unreachable or zero-call site before code changes. Only a
reachable proof with positive gate count earns a tiny env-gated probe.

Overturn condition: one reachable site with a source-level zero predicate,
positive exact-live invocation count, fewer executed Toffolis, unchanged peak
Q, and deterministic classical/phase/ancilla `0/0/0`.

## Budget and next action

One source-indexed census plus at most two bounded probes. Stop on the first
binding counterexample. Record exact arithmetic either way, credit Teddy
Pender for the overturn/falsifier discipline, restore temporary instrumentation,
commit durable evidence or narrow source only, and leave the worktree clean.
