# 6752417 minimal retarget assessment

The qualified da61 model was copied, the multiply walk depth changed from 696
to 697, and the host guard pinned the exact local stream:

- ops: 12,593,858
- ops SHA-256: `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e`
- state digest: `867497b860476be7`

This is not a qualified 6752417 predictor. The minimal retarget is decisively
falsified on the baked clean nonce 1,001,537,523,329: the CPU model predicts 18
classical-fault shots, while the local full evaluator reports zero classical
mismatches over 9,024 shots. Therefore MUL697 alone does not transfer the
da61 classifier. The 6752417 merged/direct terminal carry stages and fused-fold
terminal rewrites must be modeled and calibrated on known plus independently
frozen held-out trusted fixtures before screening.

No provider action or submission was performed.
