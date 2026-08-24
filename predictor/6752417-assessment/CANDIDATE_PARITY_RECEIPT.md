# Q1266 odd-passenger classical predictor receipt

Verdict: `ADMIT` for bounded local classical prefiltering only.

The model frozen at commit
`fe223a25015adea2f6975ddb964745e16c14bb42` was not changed after the blind
fixture freeze. On the inherited calibration nonce it matched all 15 exact
source-simulator mismatch indices. It then matched all 117 mismatch indices
across six precommitted blind nonces with zero false positives and zero false
negatives.

## Tool binding

- predictor tree: `5af565a42a6f25ebcdd8dd0c2a3db369c87849da`
- predictor binary SHA-256: `2ad04b1a337af838b3b6836ff2bae7eeb78fae463234613268ed511dcce17dc1`
- exact source-simulator binary SHA-256: `ed45acf0fcef8ffc8dca8fa9d259da4ac0704b8b47e899f68a4862eaca4f05dc`
- tail-patch binary SHA-256: `036c60a5ac824534f20e99feecbeb065a3215433096e28123f6878241a95bfab`
- base candidate ops SHA-256: `5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c`

The predictor read the bound base stream and parameterized its final 96-op
identity tail with each declared nonce. The independent simulator read a
separately tail-patched full op stream for the same nonce.

## Exact blind results

- blind-0, nonce `20470091679775`, patched ops
  `53b1f3a29e092dc0ac3d252fc68041b36be7192feb03c58ece95600975f27ebd`:
  22 mismatches at `[235,1870,2596,2672,3776,3914,4259,4341,4842,5292,5478,5621,5825,5969,6168,6496,6584,7680,7845,8376,8572,8734]`.
- blind-1, nonce `40085678580434`, patched ops
  `d33a2674af9f6a09d86a544c87d154c507b7f61b4cb7cccff8b4ba080c9c2ae3`:
  22 mismatches at `[502,943,965,1348,1553,1742,1842,1843,1992,2413,4271,4539,5616,5941,6075,6819,7032,7171,7468,7989,8474,8691]`.
- blind-2, nonce `147141427920013`, patched ops
  `6319b2006b33a0fa52ac43aaf74c3b5a5ed20098a0d4f6278463a4c0d90722e6`:
  17 mismatches at `[188,944,1614,2889,3133,3242,3755,4375,4984,5239,5589,5692,5909,7319,8424,8653,8664]`.
- blind-3, nonce `112526367679094`, patched ops
  `3fc1239f50688d4ad4971d8d6bf9b420a6bc1444af09b992998e449db3311834`:
  19 mismatches at `[95,249,1115,1356,1628,1690,3534,3814,3843,4129,4350,4803,4986,5079,6567,7520,7961,8364,8895]`.
- blind-4, nonce `189375405644123`, patched ops
  `f5adc9ce037e0620ce19c43c2d3285617bae7c2118c61c25e34cce26d543fda1`:
  13 mismatches at `[965,987,1336,1621,2213,2265,3000,4280,4520,6071,6179,7462,7716]`.
- blind-5, nonce `224717271880508`, patched ops
  `e7ef4f30c38e746e9cbb14c575a762b76b802a3833ffb8027a7edf581cf9f7fc`:
  24 mismatches at `[442,857,1328,1565,1996,2200,2443,2981,3556,3837,3924,3927,4266,4335,4621,4659,4844,4882,5002,5112,7048,7105,7654,8165]`.

All six exact source simulations reported zero dirty batches. Their phase-batch
counts were respectively 15, 12, 11, 13, 8, and 15; phase prediction was not
part of this gate.

## Gate state

- local classical prefilter: `ADMIT`
- phase postfilter: `CLOSED` pending source-bound blind parity
- bounded nonce search: `CLOSED` pending phase gate and declared range
- provider/fleet/spend: `CLOSED`
- submission/public-note/push: `CLOSED`
