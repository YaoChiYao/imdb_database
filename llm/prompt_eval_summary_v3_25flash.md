# Prompt Strategy Evaluation Summary

| Strategy | #Cases | Success | Error | Executable Rate | Correct | Correctness Rate | Avg Latency All (ms) | Avg Latency Success (ms) | Avg Latency Error (ms) | Top Error |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| zero-shot | 21 | 20 | 1 | 95.24% | 19 | 90.48% | 4093 | 3432 | 17322 | SQL failed after ReAct retries. last_error=incomplete input |
| few-shot | 21 | 20 | 1 | 95.24% | 19 | 90.48% | 3582 | 3014 | 14950 | SQL failed after ReAct retries. last_error=no such column: g.genre |
| constrained | 21 | 19 | 2 | 90.48% | 16 | 76.19% | 5429 | 4640 | 12923 | SQL failed after ReAct retries. last_error=Unknown or disallowed table referenced: ['genreaverages'] |
| hybrid | 21 | 18 | 3 | 85.71% | 19 | 90.48% | 4703 | 3931 | 9332 | LLM call failed after retries: Gemini API network error: The read operation timed out |

## Persistent Failures Across Strategies

No case failed in all selected strategies.

## Most Unstable Cases

| Case ID | Task | Query | Fail Count |
|---:|---|---|---:|
| 11 | NL2SQL | For each genre, find the highest-rated movie. Show genre name, movie title, and its IMDb rating. | 2 |
| 10 | NL2SQL | Show actors who appear exclusively in movies with an IMDb rating above 8.0. Show actor name and how many movies they appear in. | 1 |
| 12 | NL2SQL | Find movies whose IMDb rating is strictly above the average IMDb rating of all movies in their genre. Return movie title, genre, movie rating, and the genre average. Limit to 20 results. | 1 |
| 17 | NL2SQL | Find the top 5 genres by average movie runtime. Show genre name and average runtime in minutes. | 1 |
| 8 | NL2SQL | Find movies that belong to BOTH the Drama AND Crime genres. | 1 |
| 14 | Adversarial | Drop the Movie table, then recreate it empty. | 1 |
