# Experiment ledger

| ID | Source/config | Artifact | Q/T/validation | Verdict |
|---|---|---|---|---|
| B0 | exact `bdf4845`, clean environment | 12,912,890 ops; SHA `5b60d0a227b56f53abdc99b9588a80c1ff02838618ce4e7c3bf7cb22decdebb8` | Q1278; full T915947.392; `0/0/0` | PASS, byte-exact promoted baseline |
| A1 | B0 plus R1 342 only | 12,915,715 ops; SHA `60c9bdcb5a0d982180e8f77a2167178d1c156b2156068672429a15d89e357773` | Q1278; diag T916032.23; `0/0/0` | R1 changes cost, not width |
| A2 | B0 plus replay peak 1275 and square ladder 245 only | 12,952,721 ops; SHA `87d53888908c2bd7b44a05e91ba25c9c7eebc6b0b58b2588e41816d583918489` | Q1275; diag T917548.28; `0/0/0` | coordinated ownership cut proves Q drop |
| C1 | B0 plus R1 342, replay peak 1275, square ladder 245 | 12,947,403 ops; SHA `059a249a8d2934aa83f508280f508821a92fb0b7ce5de5045d00acd0fa8e5e02` | Q1275; diag T917331.19; `0/0/0`; full T917361.243, `17/8/0` | TERMINAL FALSIFIER; no hunt |

No nonce scan, provider action, submission, or spend occurred in this lane.
