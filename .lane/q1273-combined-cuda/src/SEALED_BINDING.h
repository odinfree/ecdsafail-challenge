#pragma once

// Terminal combined CPU GO integrated from exact commit 3c1a49c, tree
// 70ab3c0196b85abd74835399094642aeb828b323. These hashes are checked again by
// verify_ready.sh before compilation.
#define Q1273_CUDA_HANDOFF_SEALED 1
#define Q1273_COMBINED_CPU_GO_COMMIT "3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e"
#define Q1273_COMBINED_HOST_SHA256 "bc2df2182beb8ebcc103a3fc498a8ca65911bf52439566dbfa1284e88407f98a"
#define Q1273_COMBINED_MODEL_SHA256 "14fc9230b55d2b2a84721e50d860933764a18d1357ad30331e5999280f764261"
#define Q1273_COMBINED_CPU_SHA256 "1d93d46803670324401443ed9f625ee641c6fa8ef77ba4a920baebff83ea24ce"

#if Q1273_CUDA_HANDOFF_SEALED != 1
#error "Q1273 combined CPU source is not sealed; CUDA compilation is disabled"
#endif
