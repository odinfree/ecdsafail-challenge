# Burn compact-history checkpoint on `6b5c82c`

Updated: 2026-08-22
Status: `KILL_BENNETT_RECONSTRUCTION`; direct checkpoint decoder remains open

Source: `6b5c82cbe723b33c296c8926876f14f1ac3307a8`

Branch: `research/burn-compact-history-6b5c82c`

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

## Teddy Pender credit

Teddy Pender receives primary credit for the Burn-the-House-Down re-descent,
the tape-replacement direction, the bounded-saddle discipline, and the rule to
price the composition before grinding. This checkpoint exists because Teddy
forced the campaign to test the replay architecture instead of polishing its
current nonce and width schedule.

## Measured geometry

- The exact divide plan sets `r1=356`.
- `value_width(356)=140`, so the live checkpoint is exactly `140 u + 140 v =
  280` wires.
- The current `pp_div_replay` peak decomposes exactly as `356 tape + 280
  checkpoint + 512 coefficient/numerator + 130 replay ladder = Q1278`.
- Gate off emits `12,950,916` operations with SHA-256
  `88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb`.
- Production `src/` at lane HEAD is byte-identical to `6b5c82c`.

## Verdict

The checkpoint width is real, but reconstructing the first 356 signs by an
extra reverse-and-forward pass through the existing walk is product-negative.
Ignoring round zero already costs exactly

```text
2 * sum(value_width(r) - 3, r=1..355) = 143,000 deterministic Toffoli.
```

The first composition saddle at Q1182 permits only `T<=992945`, or about
74,587 T over the protected rounded baseline. Teddy's exact sparse square adds
1,012 deterministic-64 executed T in the full affine diagnostic. Even granting
the checkpoint decoder zero extra gates beyond the two walk passes gives
rounded `T>=1,062,370`; that needs `Q<=1104` to beat the protected product.
The sparse square itself bottoms this composition at Q1148, so the route loses
before decoder logic, round-zero reconstruction, or cleanup is priced.

The symmetric multiply side is order-compatible with a backward decoder, but
the exact Fable lifetime census at `917cde9` killed freeing or aliasing its
256-wire replay allocation at the binding add. It supplies no independent path
below Q1148. No candidate entered nonce search or the full 9,024-shot gate.

## Exact next test

Reopen only with a direct reversible checkpoint rank/unrank decoder that:

1. proves the 280-wire round-356 checkpoint identifies every required sign on
   the accepted support;
2. reconstructs one sign at a time with non-growing scratch;
3. adds at most about 102,983 executed T after the sparse-square delta at
   Q1148, and preferably at most about 73,575 T at Q1182;
4. is consumed symmetrically in multiply walkback without a second tape or a
   live replay-allocation copy; and
5. passes a paired reference/oracle slice before any production port.

A bounded QF_BV collision query returned `unknown` and is not evidence for or
against checkpoint injectivity. Its temporary generator was removed. Do not
repeat that query without a stronger encoding or a machine-checkable proof.

Full arithmetic and composition evidence: `.lane/TEDDY-COMPACT-HISTORY-6B5C82C.md`.
