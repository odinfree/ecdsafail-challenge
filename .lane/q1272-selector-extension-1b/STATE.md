# Q1272 selector one-billion extension state

- decision: `SUPERSEDED_UNACTIVATED / PROVIDER_UNUSED / RANGE_UNDECLARED`
- source: `14608572e84daf89397768c43ac0d812c714c3bd`
- operation identity: `12,908,488 / 678c149f...22f0`
- checkpoint identity: `0dbd3723...c361`
- prior pilot: 5,000,000 exact rows, 100/100 chunks, 0 survivors
- harvested prior tree: exactly 714 files; terminal receipt `10680f70...`
- proposed bounded wave: `[100000036457280,100001036457280)`
- layout: 20 contiguous slots of 50,000,000; 50 chunks of 1,000,000 per slot
- scan: exact complete 9,024-shot classical predictor, not early-exit mode
- confirmation: every classical-zero survivor through the unchanged full
  9,024-shot evaluator; candidate requires `0/0/0`
- frozen score gate: live snapshot `4eb93cb`, score `1,163,831,339`; Q1272
  rounded T must be at most `914,961`
- candidate reference: T914727.660 -> rounded 914,728 -> score
  `1,163,534,016`, frozen margin `297,323`
- provider snapshot: 0/104 running, `$0/h` compute, retained host `48241642`
  stopped/stopped/exited
- stop reason: live-source commit `7342270` produced a different exact Q1272
  stream (`ea19759d...`) before this packet was authorized; never activate or
  reuse this older-source map
