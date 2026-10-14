# Evidence: context management

Source-of-truth for the claims on the site about how LoongCode manages context
(the home page "Context that lasts" section and the blog article "The context
window is a budget"). Every claim below is checkable against the LoongCode
source at `github.com/LoongLab/LoongCode`.

Recorded 2026-10-14 against LoongCode v0.1.4.

## Three layers

| Claim | Where it lives |
| --- | --- |
| Tool output is capped at the source and spilled to a file with a short preview | `packages/agent/src/tools/truncate.ts` — `THRESHOLD = 2048` bytes, `PREVIEW_LENGTH = 500`, spills to `<tmpdir>/loongcode-tool-output/` |
| Large file reads are bounded | `packages/agent/src/tools/read.ts` — `MAX_BYTES = 50 * 1024` |
| Other tools bound their output | `grep.ts` `MAX_MATCHES = 100`; `find.ts` `MAX_RESULTS = 200` |
| Older tool results are reduced at request time, oldest first, only when over budget | `packages/agent/src/context/projection.ts` — `pruneOldToolOutputs` |
| Reduction is triggered by budget pressure, not a turn count | `projection.ts` — enters reduction only when `max(lastInputTokens, estimate) > inputBudget` |
| The current user turn is protected in the pressure pass | `projection.ts` — stage 1 breaks at `lastUserIndex` |
| History is summarized when it truly overflows, preserving a recent tail | `packages/agent/src/context/compaction.ts` — `Compactor.compact`, `selectPreservedTail` (25% of the input budget, clamped to 2000–8000 tokens) |

## Reduction is reversible

| Claim | Where it lives |
| --- | --- |
| A withheld result is replaced by a structured marker, not deleted | `projection.ts` — `PrunedToolOutput`, `markerFor` |
| The marker carries a route back to the full output | `projection.ts` — `spillPath` (captured artifact), `sourcePath` + `resumeOffset` (re-readable file) |
| A route through a file is offered only while the file is intact | `projection.ts` — `routeIsSafe`, `sourcePathIsIntact`, `rewrittenAfter` |
| Failure evidence and errors are never withheld | `projection.ts` — `isReducible` returns false for `failureEvidence` and non-`text` output |
| Reduction never mutates durable history | `projection.ts` operates on a copy; markers are never persisted (tests: "no pruning marker is persisted", "durable messages are never mutated") |

## What is deliberately *not* claimed

- No percentage or absolute token saving is stated anywhere. A benchmark has not
  been run, so no number is published. This file records mechanism, not effect.
- The terminal session on the home page is labelled **illustrative**: it shows the
  tool loop (read → bash → edit → bash) but is not a recorded run.

## How to verify

```sh
git clone https://github.com/LoongLab/LoongCode.git
cd LoongCode
sed -n '1,70p' packages/agent/src/context/projection.ts
sed -n '1,60p' packages/agent/src/tools/truncate.ts
sed -n '1,60p' packages/agent/src/context/compaction.ts
```
