# J2-D4 exact-675 origin archaeology

## Verdict

`HARD_NACK_ORIGIN_675_UNRECONCILED` as of the live origin census at
2026-08-24T08:32:49Z.  Of 107 live origin heads, seven have exact promoted
commit `67524171baaf568dc3dc606f38515745f70804ff` as their merge base.  All
seven tips, and all eight unique post-base commits they contain, are covered by
the predeclared reconciliation/exclusion ledger.  The unreconciled set is
empty, so this bounded origin family contains neither a validated Q/T
improvement nor an actionable proof-bearing mechanism to admit.

This is a branch/ref census, not a claim about deleted, unpushed, or
non-origin work, and not a general claim that no exact-675 optimization exists.

## Source and freshness binding

- Worktree: `ecdsafail-smallwidth-redteam-codex`
- Audit branch before report: `research/codex-smallwidth-redteam-20260824`
- Audit HEAD before report: `fef31d7e1117edd25fa8dec71d1608480f57fef2`
- Audit tree before report: `f3e2e6ca544064d3276633396119a832bae09d55`
- Promoted base: `67524171baaf568dc3dc606f38515745f70804ff`
- Promoted base tree: `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- `git fetch origin`: rc 0, 2026-08-24T08:32:49Z, without prune
- Live check: `git ls-remote --heads origin` returned 107 heads
- Local tracking check: 108 origin refs including the symbolic
  `origin/HEAD`; normalized live and tracking head names were identical

## Complete exact-675 origin set

Every row returned the promoted base itself from `git merge-base BASE TIP`.
`Ahead` counts unique commits in `BASE..TIP`.  Patch IDs are stable patch IDs
of the complete base-to-tip diff.

| Live origin branch | Tip commit | Tip tree | Ahead | Stable patch ID | Reconciliation |
| --- | --- | --- | ---: | --- | --- |
| `research/codex-675-window-entry-carry-20260824` | `848657bd00b9c7fef7aff2e64b4d7470118c8bf6` | `273dcff872662ea3e30fa7fcffd04b0783e69ca8` | 1 | `5f5af288c9fed34def9b985a75a8751960b3e1fc` | excluded `codex-675-*` / J1 family |
| `research/justin-drake-smallwidth-liftability-audit` | `28c12cd7111f787f2b5c931e097737a4653f049e` | `7a4302c0ed377ded54b3961df806ff0996b330c3` | 1 | `51d7766d1138d375b828f14ad5e08f22f539b7ab` | named known handoff |
| `research/q775-defense-6752417` | `744136752171711a3a8da6c11ba3a855a330aefa` | `89c1ed67d9f954fd78a8f4b01e3c8114f4459e3f` | 1 | `d62044b2f943cba2e5e3dbd468951b1d4bd8cf5f` | named q775-defense exclusion |
| `research/sol-675-microgrind` | `68ce67aee5f00bbbef3f050d84f03ace483b269c` | `1a504466f6e627447ae255cb68044e350a6ea24d` | 1 | `d660798313e7d51d649cbd27ad9ba46be0a2065a` | named microgrind/predictor exclusion |
| `research/sol-675-smallwidth-harness` | `e0322f5eddb5fb169ed89a8430a269a36dbc58e0` | `36f7301a8bc9fb3fa1aace68e7d681f06c6cf557` | 1 | `abc74391ab24e185d6b3b5b98fc0c32983d20191` | named known handoff |
| `research/sol-justin-controller` | `e06c1810f17c97d5b0ee964ee63f62b8a05d83e9` | `e8f50b30540fd6371d9c7abc09d792440223511e` | 2 | `7e4bb723acc7076c53c5311d438ed102c793e034` | named known handoff |
| `research/sol-smallwidth-analysis` | `d76c426f7ad568355ecdb29be946a2a455226ecb` | `9e749e1829b85b5fb6b80e3faf30b22d1452f83c` | 1 | `de5a31414257553e146e9e87b87a37fde54d33e5` | named known handoff |

The eight unique post-base commits are the seven one-commit tips above plus
`aa788549d735c13db376e9954dba4fa64cef450e` (tree
`e7f41357efd0043bb55c75cafde40f70dc9e68ff`), the first of the two commits
already contained by the reconciled `sol-justin-controller` tip.  There is no
post-base commit reachable from a live exact-675 origin head outside these
eight.

## Duplication and conflict check

The seven complete branch diffs have seven distinct stable patch IDs, so there
is no byte-equivalent whole-diff duplicate.  Five pairs touch a common path.
Read-only `git merge-tree BASE LEFT RIGHT` reports:

- textual conflict in `Cargo.toml` between `sol-675-microgrind` and
  `sol-675-smallwidth-harness`;
- textual conflict in `src/point_add/mod.rs` between
  `sol-675-smallwidth-harness` and `sol-smallwidth-analysis`;
- clean automatic merges for the three other overlaps:
  `codex-675-window-entry-carry` versus `sol-675-smallwidth-harness` in
  `src/point_add/pingpong_div.rs`, q775-defense versus each of the harness and
  analysis branches in `src/point_add/mod.rs`.

These are conflicts among already reconciled/excluded lines, not a new
candidate.  The live rooted set contains no protected/promoted submission ref
and no additional branch requiring diff/evidence inspection.

## Reproduction commands

Run from the bound worktree:

```sh
git status --short --branch
git rev-parse HEAD^{commit}
git rev-parse HEAD^{tree}
git rev-parse 67524171baaf568dc3dc606f38515745f70804ff^{tree}
git fetch origin
git ls-remote --heads origin
git for-each-ref --format='%(refname:short) %(objectname)' refs/remotes/origin
git merge-base 67524171baaf568dc3dc606f38515745f70804ff <origin-tip>
git rev-list --count 67524171baaf568dc3dc606f38515745f70804ff..<origin-tip>
git rev-list --topo-order --reverse --parents <seven-origin-tips> ^67524171baaf568dc3dc606f38515745f70804ff
git diff 67524171baaf568dc3dc606f38515745f70804ff <origin-tip> | git patch-id --stable
git diff --name-only 67524171baaf568dc3dc606f38515745f70804ff <origin-tip>
git merge-tree 67524171baaf568dc3dc606f38515745f70804ff <left-tip> <right-tip>
```

No production source was edited; no build, provider, GPU, push, or submission
was performed.  The next independent gate, if desired, is a later fresh-origin
delta census after a new exact-675 ref appears, not implementation from this
closed set.
