# Prompt Strategy Evaluation Summary

| Strategy | #Cases | Success | Error | Executable Rate | Avg Latency All (ms) | Avg Latency Success (ms) | Avg Latency Error (ms) | Top Error |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| zero-shot | 12 | 9 | 3 | 75.00% | 13916 | 4 | 55652 | SQL failed after ReAct retries. last_error=Only SELECT (or WITH...SELECT) queries are allowed. |
| few-shot | 12 | 8 | 4 | 66.67% | 22981 | 5 | 68932 | SQL failed after ReAct retries. last_error=Only SELECT (or WITH...SELECT) queries are allowed. |
| constrained | 12 | 7 | 5 | 58.33% | 30266 | 9 | 72625 | SQL failed after ReAct retries. last_error=Only SELECT (or WITH...SELECT) queries are allowed. |

## Persistent Failures Across Strategies

| Case ID | Task | Query | Fail Count |
|---:|---|---|---:|
| 9 | Recommendation | Recommend 5 emotional drama movies with high rating. | 3 |
| 10 | Recommendation | I like mind-bending sci-fi movies similar to Inception. | 3 |

## Most Unstable Cases

| Case ID | Task | Query | Fail Count |
|---:|---|---|---:|
| 9 | Recommendation | Recommend 5 emotional drama movies with high rating. | 3 |
| 10 | Recommendation | I like mind-bending sci-fi movies similar to Inception. | 3 |
| 7 | NL2SQL | Give me science fiction movies from 2010 to 2020 sorted by votes. | 2 |
| 2 | NL2SQL | Find drama movies with rating above 8.5. | 2 |
| 5 | NL2SQL | Which actor appears in the most movies in this dataset? | 1 |
| 6 | NL2SQL | Find the average IMDb rating of movies released after 2010 by genre. | 1 |
