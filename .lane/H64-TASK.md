# Claude Fable task — Q1274 three-stream H64 tiebreak

Work only in this clean isolated worktree and branch. Read the complete
burn-the-house-down skill, `.lane/PREDECLARATION.md`, and `.lane/STATE.md`.
Do not redo the completed structural matrix.

The two exact Q1274 streams are:

- control: PEAK1274/LADDER244/BREAK_1=30, base SHA `61a57ce6...`,
  Q1274/T917227.881, inherited `14/9/0`, score 1,168,548,472;
- score-optimal: PEAK1274/LADDER244/BREAK_1=24, base SHA `8bc29444...`,
  Q1274/T913684.649, inherited `24/17/0`, score 1,164,034,690.

Protected b523 is Q1278/T914789.886 and its trusted H64 receipt on nonces
`444000000000..444000000063` is frozen in the sibling Q1276 evidence. Reuse it
only after verifying exact protected source/operation identity and receipt
hash; otherwise rerun it unchanged.

Before evaluating either candidate, append a predeclaration to `.lane/STATE.md`
that freezes:

1. exactly the same 64 nonces `444000000000..444000000063` for all streams;
2. complete 9,024-shot classical/phase/ancilla totals and exact average T as the
   metrics; no row may be skipped;
3. explicit three-sigma non-inferiority ceilings versus protected b523, and a
   score-optimal-vs-control comparison rule computed before candidate totals;
4. selection rule: carry B1=24 forward if it is non-inferior to protected and
   not materially worse than control; otherwise carry control if it is
   non-inferior; otherwise hold both. Score margin never excuses density.

Build every nonce from a clean, source-bound configuration and run the
unchanged full evaluator on all 9,024 shots. Require Q1274 and ancilla zero on
all 128 candidate rows. Freeze row ledgers and receipt hashes outside Git;
commit only compact aggregate/selection evidence and any small TSV needed for
independent audit. Do not tune widths, adapt the corpus, or use results to add
a third stream.

Reopen live after the corpus. No predictor edit, provider, remote, range, scan,
hunt, submission, public note, or ecdsa-ops mutation. Restore generated files,
update durable state, commit, and push to
`odinfree/research/fable-b523-ladder-below1276`.
