# Pred0 canary status

Status: **open; bounded local run stopped after the committed prefix proved too slow**.

- Rule commit, pushed before search: `71fbd92`
- Exact predictor SHA-256: `384e724120ae4237b72ecc8889e41ada5a260aa3892e0ebe6274308549d5a6cd`
- Exact state digest: `0c0c07b906775f4f`
- Committed bound: `[269575048538290, 269575048800434)` = `262144` nonces
- Completed ascending prefix: `[269575048538290, 269575048546482)` = `8192` nonces
- Threads: `12`
- Survivors: `0`
- Wall time: `105.75` seconds
- Measured rate: `77.465721` nonces/second
- Full-bound projection at that rate: `3384.00` seconds = `56.40` minutes
- Remaining projection: `3278.25` seconds
- Predictor stdout SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty; no survivor)
- Predictor stderr/timing SHA-256: `5505dbd71c9226b635e5934e615dfc6d700d0bc1707385bf41654bfe4e1fb0fc`

No alternate range was tried. Since the committed prefix contained no `pred_cls=0`, there was no canary to send through the unchanged full evaluator. The pred0 gate is the only local calibration gate still open.
