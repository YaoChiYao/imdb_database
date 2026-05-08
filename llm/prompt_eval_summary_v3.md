# Prompt Strategy Evaluation Summary

| Strategy | #Cases | Success | Error | Executable Rate | Correct | Correctness Rate | Avg Latency All (ms) | Avg Latency Success (ms) | Avg Latency Error (ms) | Top Error |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| zero-shot | 21 | 21 | 0 | 100.00% | 21 | 100.00% | 1607 | 1607 | 0 |  |
| few-shot | 21 | 21 | 0 | 100.00% | 21 | 100.00% | 1620 | 1620 | 0 |  |
| constrained | 21 | 21 | 0 | 100.00% | 21 | 100.00% | 2859 | 2859 | 0 |  |
| hybrid | 21 | 21 | 0 | 100.00% | 21 | 100.00% | 1859 | 1859 | 0 |  |

## Persistent Failures Across Strategies

No case failed in all selected strategies.

## Most Unstable Cases

| Case ID | Task | Query | Fail Count |
|---:|---|---|---:|
