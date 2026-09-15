# r-reader asymmetry (lane_seed_port, 2026-09-15T17:20Z)

Script: `chart16_crosscheck.py` (mode `r_full_check`, also runnable from the
committed copy in the lane repo `dev/`). Logs: `runtime/seed-chart16-crosscheck.log`
plus the outputs quoted below.

## What was measured

For a reader (`xor_r16` four-hole, `xor_r` three-hole) the emitted action is the
16-var (resp. 12-var) Möbius ANF over chart + A-case flags, with **every cube
emitted twice**: the second gate adds the boundary cofactor
`a_bits[bit-1..]` (the comment calls it the "exact zero cofactor from
t*r<=p"). So the reader's function is a function of `(chart, boundary)`, and the
question "is the reader the primitive's r bit?" must be asked per
`(chart, boundary)`.

Test: for every chart code, does **some** boundary value reproduce the
primitive's own r bit? (The weakest possible reading — one boundary value per
code is allowed.)

| reader | domain | codes with NO reproducing boundary |
|---|---|---|
| three-hole `xor_r` (bit 1) | 512 shared codes | **0 / 512** |
| three-hole `xor_r` (bit 2) | 512 shared codes | **0 / 512** |
| four-hole `xor_r16` (bit 1) | 4096 codes | **256 / 4096** |
| four-hole `xor_r16` (bit 2) | 4096 codes | **256 / 4096** |
| four-hole `xor_r16` (bit 3) | 4096 codes | **256 / 4096** |

The accepted three-hole reader has no such gap; the four-hole reader does. The
failing codes have a sharp pattern: `v = 1` together with `b = 2^bit - 1`
(bit1: `b=3,v=1`; bit2: `b=7,v=1`; bit3: `b=15,v=1`), plus a smaller
`(t|v)`-even remainder (64 / 96 / 112 codes for bits 1 / 2 / 3).

Primitive side is sound: the 228-op `PLAN` reproduces the documented scalar map
on all 4096 codes, is echo-independent and involutive, and `U16_TERMS` equals
its u-group ANF exactly (11/13/33 terms — see `runtime/seed-chart16-crosscheck.log`).

## What this does and does not say

* It does **not** say the four-hole artifact fails because of the r reader: the
  256 codes per bit could be unreachable. Reachability is not testable from the
  chart alone.
* It does say the asymmetry is real and not implied by the accepted design: the
  same "ANF + boundary cofactor" construction is complete in the three-hole
  reader and incomplete in the four-hole one.
* Reachability looks plausible rather than exotic (`v=1` is a small chart value,
  and the cargo classes' bounds `v<<S<=r` make small `v` the typical case), so
  this deserves an owner's verdict before the traversal port is credited with
  the whole defect.

## Cheapest way to settle it

Instrument the exit call sites (`q793_Aupdate::length_xor`,
`q793_transfer::length_xor`) in one real three-hole run — the drill's oracle side
already simulates them — and record the `(t,b,v,boundary,bit)` tuples actually
presented to `xor_r`. Any tuple whose `(t,b,v)` is one of the 256 codes above
means the gap is live and the r reader is a defect; none means the reader is
exonerated and `lanes/laneRoot/Q792-MOD16-PORT.md` remains the single critical
path.
