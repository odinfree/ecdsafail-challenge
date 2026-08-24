# Register-Shared Euclid Anti-Rot Reconciliation

Verdict: `HARD_NACK_DUPLICATE_LITERAL_ROUTE`.

## Binding

- Current base: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f`, tree
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current campaign target: delete the complete multiply traversal with a
  replacement component at most Q1100 and T335738.86.
- Prior exact ping-pong row evidence: commits `2b0bd4c`, `bab2824`, and
  `44eae42`.
- Prior generic in-place multiplication and register-sharing review: commits
  `800dd1e` and `10beec3`.

## Reconciled result

The current ping-pong row does not become reversible from the live post-row
walk state plus bounded metadata. Reachable trajectories at rounds 600 and 650
share the same decoder-visible walk state with opposite required signs. When
the complete coefficient state is included, exact endpoint-history fibers at
widths 5 and 6 still require 4 and 5 retained bits respectively: `n-1`, not
`O(log n)`. Materializing the retained-denominator decoder reaches Q1284 before
its first sign/carry scratch, while ordinary two-traversal recomputation has an
exact 375720-T floor on the bound ancestor.

The different register-sharing EEA of Luo et al. is also already priced. Its
published leading inversion term is `195*n^2`, or 12779520 Toffoli at n=256,
before the complete point-add schedule. That is more than an order of magnitude
above this campaign's full score allowance and about 38 times the complete
335738.86-T replacement budget.

These results do not prove that every possible signed-Euclid row needs linear
metadata. They do prove that rerunning the question without first specifying a
different row is duplicate discovery work, not a new structural experiment.

## Changed-premise reopen

Reopen only with one explicit row transition that:

1. differs algebraically from both current ping-pong and Luo register sharing;
2. exposes its reverse branch from post-row state plus a declared `O(log n)`
   metadata formula;
3. survives exhaustive adjacent-width reachability;
4. has a complete 256-bit live-wire and executed-Toffoli equation below Q1100
   and T335738.86; and
5. accumulates no branch, quotient, location, or carry transcript.

The active ball therefore moves to a changed equation: exact curve-support
relations that might eliminate the second denominator rather than another
encoding of its sign tape.

Provider, nonce, push, public-note, promotion, and submission authority remain
closed.
