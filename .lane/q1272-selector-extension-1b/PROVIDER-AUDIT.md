# Provider and spend audit

Snapshot: `2026-08-23T11:37:19Z`.

- Vast inventory: 104 retained instances.
- Running or intended-running instances: 0.
- Compute rate: `$0/h`.
- Retained-disk rate: `$1.6088888888888877/h`.
- Current compute-plus-storage 24-hour projection: `$38.613333333333305`.
- Projection headroom under the authorized `$500/24h` cap:
  `$461.3866666666667`.
- Retained selector host `48241642`: `stopped/stopped/exited`.
- RunPod Q1276 calibration pod was previously terminated; its ledgered account
  baseline was `$0.033/h`. This lane made no RunPod call.

The recommended 20-host layout is a geometry recommendation, not permission to
start 20 hosts. Before activation, root must refresh both provider inventories,
recompute the rolling cap from current billing, assign exact retained IDs and
rates, and create a separate content-bound authorization. This packet contains
no host IDs, credentials, provider commands, or automatic scale path.
