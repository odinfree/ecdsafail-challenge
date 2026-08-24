# Controlled-Constant Product-Code Verdict

Verdict: `HARD_NACK_CONTROLLED_CONSTANT_PRODUCT_CODE`

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Exact receipt: `58-controlled-constant-product-receipt.json`, embedded
  SHA-256
  `71a6b75b765bdeb0c0b7d76cc49d0a5ec627ce5aaa8735b6623f6ae83e9795b0`.

## Result

The proposed construction would factor the quantum multiplier into independent
classical-unit selections:

```text
T = K * product_j C_j[window_j(T)] mod p.
```

Every such disjoint-window product has zero multiplicative rectangle residual.
For bits `i` and `j` in different windows and a distinct context bit `k`, the
actual field multiplier has the four legal values

```text
2^k,
2^k+2^i,
2^k+2^j,
2^k+2^i+2^j,
```

whose rectangle residual is exactly `-2^(i+j) mod p`, never zero.

The production certificate checked all 32,640 secp256k1 bit pairs. Every
three-bit context lies below the prime, every residual matches the symbolic
formula, and none is zero. Its pair ledger SHA-256 is
`da12e315a820cf1b4c03f2686791959bc995106cdd720a2d6cea0fbcb1b97a6a`.

The reduced-width census independently checked all 2,025 unordered two-window
partitions at widths 5 through 11. Every target partition failed and every
synthetic product-code control passed.

## Scope

No partition of the 256 standard binary digits into two or more independent
windows can select fixed in-place constant multipliers whose product equals
`T`. A single 256-bit window has `p-1` entries and is either an exponential
lookup or the original variable unit primitive; it is excluded by the scalable
fingerprint.

This does not reject overlapping-window factors, adaptive factor selection,
or an arithmetic circuit whose factors interact. The next grammar is
`OVERLAPPING_NONLOCAL_UNIT_ACTION`, and it must expose how those interactions
are computed and reversed rather than hide them in a table.

## Authority

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
