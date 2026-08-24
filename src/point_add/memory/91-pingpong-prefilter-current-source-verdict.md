# Ping-Pong Prefilter Current-Source Verdict

Verdict: `E_PREFILTER_CURRENT_SOURCE_UNBOUND`

The requested prefilter is now integrated as a local binary at upstream commit
`da0e5721f14f5d956aa703b38311f4087388a7b1`, with source fingerprinting and a
hard diagnostic-only runtime guard. It has not been pushed because this lane's
push gate remains closed.

The published model is pinned to an older ping-pong stream. A deliberately
restricted compatibility profile disables the current signed replay frame and
fused early-round shortcuts and restores the model's linear width schedule.
That profile emits 12,886,147 operations at Q1266.

The bounded CPU diagnostic screened 32 nonces at 16.235 nonces/second. The
trusted evaluator cross-check did not close: nonces 13 and 14 were predicted at
5 and 4 classical mismatches but evaluated at 6 and 5. Both differences are in
the conservative direction expected when the high-level ping-pong model omits
another approximate point-add channel, but two examples do not prove the
zero-false-negative property required to reject candidates.

Accordingly the binary refuses every ordinary screening invocation. It runs
only when the exact compatibility profile and
`PINGPONG_FILTER_DIAGNOSTIC_ONLY=1` are both present. Reopen screening only
after the current source's remaining value approximations are modeled and a
source-bound evaluator subset check passes in the fatal direction.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
