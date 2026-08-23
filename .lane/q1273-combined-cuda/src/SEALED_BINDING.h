#pragma once

// This deliberate compile barrier is replaced only after a terminal committed
// combined CPU GO is independently delivered to this lane.
#define Q1273_CUDA_HANDOFF_SEALED 0
#define Q1273_COMBINED_CPU_GO_COMMIT "UNSEALED"
#define Q1273_COMBINED_HOST_SHA256 "UNSEALED"
#define Q1273_COMBINED_MODEL_SHA256 "UNSEALED"
#define Q1273_COMBINED_CPU_SHA256 "UNSEALED"

#if Q1273_CUDA_HANDOFF_SEALED != 1
#error "Q1273 combined CPU source is not sealed; CUDA compilation is disabled"
#endif
