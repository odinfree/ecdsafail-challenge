# Promoted-source Q1272 predictor state

- decision: `LOCAL_CPP_CLASSICAL_GO / HOLD_CUDA / HOLD_RANGE`
- target: `73422709` / tree `fe77bddf...` / ops `ea19759d...`
- evidence: `41dd0b45` / exact diagnostic `23/8/0`
- predictor source SHA-256: `39371fca9e77d7aab3cfda7111bdbc03c11d8cfc03966cd15b2ea77d79836e38`
- inherited classical index SHA-256: `c46041ff454200ba4d2ab3cffcefb2b118e4afd839f674431762b24da37f8848`
- inherited result: evaluator = predictor = 23, first shot 292, complete set equal
- shared CPU model: exact 23 fault masks; 18 first-width deficits / 5 hard
- shared checkpoint/tail digest: `e9b2d20ecd1169a8`
- causal fixture SHA-256: `ab647dc2345fade447d47547037962e399d66142e57519563769cfe3a93d8fcb`
- H64 result: 64/64 complete masks, 1,144/1,144 faults
- H64 summary SHA-256: `88cf50daa6a90f3bbf5404fb9df01924a39e7688d8ce596ad62bff9b58f38821`
- D32 result: 31/32 complete masks; nonce `66961008849867` undercounts
  26/27 with evaluator-only shot `8729`
- D32 reveal SHA-256: `e2754ae5090b52ff6318920b9385579690213f5712bdf5ce1bed696bedc54c83`
- retrospective result: inherited 23/23, H64 1,144/1,144, spent D32
  559/559, all complete masks exact
- V64 pre-evaluator disagreement: nonce `90522024612912`, Rust/C++ 18/17,
  Rust-only shot `2544`; trusted V64 unopened at seal time
- trusted V64 adjudication: corrected Rust 64/64 masks, 1,131/1,131 faults;
  shared C++ falsified by trusted shot `2544`
- repaired shared model SHA-256:
  `d417865bcc119686dc2d9a3d45ca8e801332cf824c8ed95aefb5e0195f1318b2`
- repaired C++ witness: nonce `90522024612912`, shot `2544`, mask `4`;
  full nonce restored to 18/18 faults
- repaired C++ retrospective: inherited 23/23; H64 64/64 and 1,144/1,144;
  spent D32 32/32 and 559/559; V64 64/64 and 1,131/1,131; all complete
  masks byte-identical to corrected Rust/trusted evidence
- W64 corpus SHA-256:
  `db43f935ec97561cdab7f1e0c86d11ea439f9b75f0da815a7a92b999bc5575a0`
- W64 pre-evaluator seal: Rust/C++ 64/64 complete masks byte-identical,
  1,138 predicted faults, output SHA-256 `0e395369f6b6e8d5...`; trusted
  evaluator unopened at seal boundary
- W64 trusted reveal: Rust/C++/evaluator 64/64 complete masks exact,
  1,138/1,138 faults; every row Q1272/9,024 shots/ancilla 0; trusted summary
  SHA-256 `80eb7ad77b4bd922...`, manifest `213221a677f0c92e...`
- final retrospective replay: inherited 23/23, H64 1,144/1,144, D32
  559/559, V64 1,131/1,131, W64 1,138/1,138; 225 nonces and 2,030,400
  complete modeled shots with zero Rust/C++ mask differences
- final negatives: 12/12 fail closed with empty rejection stdout; positive
  state digest `e9b2d20ecd1169a8`; normalized receipt SHA-256
  `1eb7ea3b06970d900539c80b1a490e157cd15a791692a286aa95909685a8976d`
- scan mode: disabled and negative-tested
- phase: independently owned by the combined-phase lane; no phase claim here
- provider/range/hunt/submission: none
- next action: none inside this bounded local C++ repair; any phase/CUDA/range
  work requires a separate source-bound predeclaration and gate
