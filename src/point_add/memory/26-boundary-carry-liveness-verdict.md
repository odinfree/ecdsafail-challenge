# Boundary carry and output-host liveness: verdict

## Verdict

`HARD_NACK` for the one-entry-carry/output-host schedule as a structural route
to a lower-Q or leading-score circuit.

Supplying the entry carry is the correct Boolean repair for truncated boundary
phase cleanup.  The missing result is its lifetime: one output or source host
cannot erase the information.  At the live binder, exact restoration requires
the omitted 106-bit prefix state or its replay.  The claimed one-wire schedule
therefore does not close.

This verdict is narrow.  It does not reject every possible global liveness
rearchitecture, and it preserves the exact window-entry carry as a correctness
defense mechanism.

## Source and evidence binding

- official source commit:
  `67524171baaf568dc3dc606f38515745f70804ff`;
- official source tree:
  `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`;
- official zero-environment stream SHA-256:
  `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e`;
- canonical semantic op SHA-256:
  `bd3612b1494a257234e8def20fb55a397f14246c1647e6c8c240080ef7e0ad37`;
- executable certificate:
  `src/point_add/memory/repro/pp_boundary_liveness.py`, SHA-256
  `d7bdeea48e59bcc9579bc2b78753ce83f17c07884faddd6751875798ded38745`;
- tests:
  `src/point_add/memory/repro/test_pp_boundary_liveness.py`, SHA-256
  `dca566a710db1574861334d506db3c2f5a7b04d4c30eed278d192c68059fff61`;
- receipt:
  `src/point_add/memory/25-boundary-carry-liveness-receipt.json`, SHA-256
  `165f1303c4d2ad6798077d3383618899351e33767e3a3b9cb398024e6bac06fb`.

The exact-window Boolean premise was not duplicated.  It is inherited from
Justin-controller commit `e06c1810f17c97d5b0ee964ee63f62b8a05d83e9`,
the reduced-width circuit at `e0322f5eddb5fb169ed89a8430a269a36dbc58e0`,
and the Pareto artifact at `d76c426f7ad568355ecdb29be946a2a455226ecb`.
The earlier exact source/output host implementation and pricing are bound at
`8d261ea9449bcd37c9a6d9a1d981a90761ec7b57`.

## Live owner equation

The rebuilt source emits 12,593,858 operations at Q1267.  Its fixed-64 profile
is exact at 0/0/0 with executed T911220.66; this is a diagnostic population,
not a replacement for the trusted live T911390 receipt.

The built-in allocation census at operation 913,421 in `pp_div_replay` gives:

```text
335 tape + 512 replay words + 292 walk limbs
          + 126 owned carries + 2 boundaries = 1267.
```

All families are semantically live.  The 126 owned carries and external
carry-out identify the binding 127-bit chunk.  With the baked 21-bit compare
window, the exact window-entry state is `c106`.

## Information result

For a fixed addend, the map

```text
(accumulator, carry_in) -> (wrapped_sum, carry_out)
```

is not injective.  Exhaustive widths 1 through 8 found respectively

```text
2, 12, 56, 240, 992, 4032, 16256, 65280
```

ambiguous output keys.  The first witness at every width is already enough:
`(acc=0,cin=1)` and `(acc=1,cin=0)` produce the same sum and carry-out for
addend zero.  Therefore next-chunk semantic outputs cannot coherently clear
the incoming boundary bit.  An output host preserves the missing information;
it does not remove it.

For every strict top window at widths 2 through 8, the exhaustive oracle also
found states with identical visible `(addend_top,sum_top,chunk_cin)` and
different final carry-outs.  This independently confirms that the exact entry
carry is necessary.

## Source-host restoration result

The older Cuccaro MAJ/UMA hybrid passes all eight Boolean cases.  Its hosted
state is exactly reversible while the predecessor carry is live.  Removing
that predecessor makes the hosted state non-injective.

Inductively, restoring a source-hosted `c106` needs `c105`; restoring that
checkpoint needs `c104`; and so on through the existing chunk input `c0`.
There are only two exact choices:

1. keep the 106-state predecessor chain (105 additional internal wires when
   `c0` is the existing boundary); or
2. recompute/replay the omitted 106-bit prefix.

The first moves the peak from Q1267 to at least Q1372 for a source-hosted
entry.  The second is a prefix replay, which is the predeclared hard falsifier
and does not remove any resident semantic term.  A separately allocated entry
carry alone would move to Q1268, where the strict ceiling is T910671 and at
least 719 rounded T must be saved, but it still cannot be restored without one
of the two choices above.

## Reopen interface

Reopen only with an architecture that supplies one of:

1. a named idle donor at the exact operation-913,421 owner plus a complete
   non-recursive restore proof;
2. a measurement/feed-forward schedule that consumes the boundary before the
   predecessor information disappears and includes its full phase semantics;
3. a codec or arithmetic map that makes the boundary input recoverable from
   the semantic outputs; or
4. an independently priced multi-pebble schedule that clears the Q1267 score
   equation without relabeling prefix replay as hosting.

No production Rust change, trusted 9,024-shot replay, provider, nonce, fleet,
queue, push, public note, protected-instance, or submission action was taken.
