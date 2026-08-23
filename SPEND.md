# Model spend

Recovered Claude fallback session:

- session: `2ea01d9d-75dc-4055-9e71-8a6d36c980b9` (local session `80479`);
- model: `claude-opus-5`, effort `high`;
- transcript SHA-256:
  `3e0ec03736333dc5663cd823cb984d7ef464f1d86819f5f4e71929f6cd5b49f9`;
- 44 unique API requests after deduplicating streamed JSONL records by
  `requestId`;
- tokens: input `88`, one-hour cache write `195,963`, cache read `5,323,478`,
  output `66,373`, web searches `0`;
- Claude Code `2.1.240` baked `claude-opus-5` rates, USD per million tokens:
  input `5`, one-hour cache write `10`, cache read `0.5`, output `25`;
- exact modeled session spend: **USD `6.281134`**.

Formula:

`88*5e-6 + 195963*10e-6 + 5323478*0.5e-6 + 66373*25e-6 = 6.281134`.

The Codex recovery invoked no additional Claude session: **USD `0.000000`**.
Total Claude spend attributable to this lane remains **USD `6.281134`**, below
the USD `20` session cap.
