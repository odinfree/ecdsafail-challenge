# da61 signed + fused-round-1 CPU predictor

Source stream: da61d487 early-sign, 12,812,623 ops, SHA-256
`cb3cb857a3eadbec699d59f08f125832292bb6e065fdf235879aa0b5f618b30f`.
The host guard pins state digest `3a16b78dd97e0960`.

The restored CPU model preserves the frozen exact shot-index calibration:

- known 14 fixture counts: 7, 9, 14, 6, 8, 6, 7, 9, 7, 5, 9, 13, 5, 7
- held-out 6 fixture counts: 28, 18, 15, 13, 15, 12

Known nonces:
`121376 478525 534989 575313 871204 1030507 1594019 1741528 1737010 1911033 2436810 2293158 2844114 2963816`.

Held-out nonces:
`8810424 8810425 8810431 8810447 8810479 8810511`.

The local CPU binary was rebuilt with clang. CUDA was not rebuilt because this
host has no `nvcc`.
