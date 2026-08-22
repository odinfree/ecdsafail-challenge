# Burn sparse-square lane

Branch: `research/burn-sparse-square-6b5c82c`

Source: `6b5c82cbe723b33c296c8926876f14f1ac3307a8`

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

Teddy Pender receives full credit for the Burn-the-House-Down re-descent that
identified the product square as a companion wall to the walk tape. This lane
does one thing: transfer his exact sparse structural-zero square lemma to the
protected source and stop before grinding.

## Commands

Build `build_circuit` in an isolated target directory, then run:

```bash
SUB4_PRODUCT_SQUARE_SELFTEST=1 build_circuit
SUB4_PRODUCT_SQUARE_SELFTEST=1 \
  SUB4_SQUARE_TEDDY_SPARSE_TRI_CORR=1 build_circuit
SUB4_PINGPONG_POINT_ADD_SELFTEST=1 build_circuit
SUB4_PINGPONG_POINT_ADD_SELFTEST=1 \
  SUB4_SQUARE_TEDDY_SPARSE_TRI_CORR=1 build_circuit
```

All four diagnostics completed without a value, phase, or ancilla assertion.
The exact receipts and composition gate are in `OVERTURN-LEDGER.md`.

## Durable verdict

`HOLD` the exact Q1148 square component. Global Q remains 1278 until the two
replay walls fall. The next objective-advancing action is composition at the
Q1182/T992945 saddle, not nonce search.
