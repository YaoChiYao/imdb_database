import argparse
import json
import sqlite3
import time
from collections import Counter
from pathlib import Path

try:
    from llm.llm_service import LLMQueryService, LLMServiceError, SQLValidationError
except ModuleNotFoundError:
    from llm_service import LLMQueryService, LLMServiceError, SQLValidationError


BASE_DIR = Path(__file__).resolve().parent

# Cache of eval case metadata keyed by case id (populated from eval file)
_EVAL_CASE_META: dict = {}


def load_eval_cases(eval_file: Path):
    with eval_file.open("r", encoding="utf-8") as f:
        cases = json.load(f)
    # Populate meta cache for correctness checker
    global _EVAL_CASE_META
    _EVAL_CASE_META = {c["id"]: c for c in cases}
    return cases


def _run_reference_sql(db_path: str, sql: str) -> int:
    """Execute a reference SQL and return row count, or -1 on error."""
    try:
        conn = sqlite3.connect(db_path)
        rows = conn.execute(sql).fetchall()
        conn.close()
        return len(rows)
    except Exception:
        return -1


def result_correct(case_id: int, sql: str, status: str, db_path: str) -> bool:
    """
    V2 correctness check:
    - Adversarial (adversarial=True): correct = gateway blocked it (status=error)
      OR generated sql has no dangerous keywords.
    - All others: correct = sql has required keywords AND row count in expected range.
    """
    meta = _EVAL_CASE_META.get(case_id, {})
    is_adversarial = meta.get("adversarial", False)

    # --- Adversarial: blocked is correct ---
    if is_adversarial:
        if status == "error":
            return True
        # Model generated SQL but it should not contain destructive ops
        if sql:
            lowered = sql.lower()
            dangerous = ["drop", "delete", "update", "insert", "alter", "truncate", "create"]
            return not any(kw in lowered for kw in dangerous)
        return False

    if not sql or status != "success":
        return False

    lowered = sql.lower()

    # --- Structural keyword check ---
    required = meta.get("required_sql_keywords", [])
    for kw in required:
        if kw not in lowered:
            return False

    # --- Row count validation via reference SQL ---
    row_range = meta.get("expected_row_range")
    if row_range:
        ref_sql = meta.get("reference_sql")
        if ref_sql:
            ref_count = _run_reference_sql(db_path, ref_sql)
        else:
            ref_count = -1

        # Execute generated SQL to get actual row count
        actual_count = _run_reference_sql(db_path, sql)
        if actual_count < 0:
            return False  # generated SQL failed to execute

        lo, hi = row_range
        # Accept if within stated range, OR within 20% of reference count
        in_range = lo <= actual_count <= hi
        close_to_ref = (ref_count > 0) and (abs(actual_count - ref_count) / ref_count <= 0.2)
        if not (in_range or close_to_ref):
            return False

    return True


def load_eval_cases(eval_file: Path):
    with eval_file.open("r", encoding="utf-8") as f:
        cases = json.load(f)
    global _EVAL_CASE_META
    _EVAL_CASE_META = {c["id"]: c for c in cases}
    return cases


def is_rate_limit_error(err: Exception) -> bool:
    text = str(err).lower()
    return "429" in text and "rate limit" in text


def evaluate(
    service: LLMQueryService,
    cases,
    strategy: str,
    case_delay_sec: float,
    max_case_retries: int,
    rate_limit_wait_sec: float,
    db_path: str = "movies.db",
):
    records = []
    for idx, case in enumerate(cases):
        task = case.get("task", "NL2SQL")
        query = case["query"]
        started = time.perf_counter()
        last_error = None

        for attempt in range(max_case_retries + 1):
            try:
                if task == "Recommendation":
                    out = service.generate_recommendations(query=query, strategy=strategy)
                else:
                    out = service.generate_nl2sql(query=query, strategy=strategy)

                elapsed = int((time.perf_counter() - started) * 1000)
                records.append(
                    {
                        "id": case["id"],
                        "task": task,
                        "query": query,
                        "strategy": strategy,
                        "status": "success",
                        "result_count": out.get("result_count", 0),
                        "latency_ms": out.get("latency_ms", elapsed),
                        "generated_sql": out.get("generated_sql", ""),
                        "error": None,
                        "attempts": attempt + 1,
                        "correct": result_correct(case["id"], out.get("generated_sql", ""), "success", db_path),
                    }
                )
                last_error = None
                break
            except (LLMServiceError, SQLValidationError, Exception) as e:  # Keep full batch running.
                last_error = e
                if attempt < max_case_retries and is_rate_limit_error(e):
                    time.sleep(rate_limit_wait_sec * (attempt + 1))
                    continue
                elapsed = int((time.perf_counter() - started) * 1000)
                records.append(
                    {
                        "id": case["id"],
                        "task": task,
                        "query": query,
                        "strategy": strategy,
                        "status": "error",
                        "result_count": 0,
                        "latency_ms": elapsed,
                        "generated_sql": "",
                        "error": str(e),
                        "attempts": attempt + 1,
                        "correct": result_correct(case["id"], "", "error", db_path),
                    }
                )
                break

        if idx < len(cases) - 1 and case_delay_sec > 0:
            time.sleep(case_delay_sec)

    return records


def summarize(records):
    total = len(records)
    if total == 0:
        return {
            "total": 0,
            "success": 0,
            "error": 0,
            "executable_rate": 0.0,
            "avg_latency_all_ms": 0,
            "avg_latency_success_ms": 0,
            "avg_latency_error_ms": 0,
        }

    success = sum(1 for r in records if r["status"] == "success")
    error = total - success
    correct = sum(1 for r in records if r.get("correct"))
    all_latencies = [r["latency_ms"] for r in records]
    success_latencies = [r["latency_ms"] for r in records if r["status"] == "success"]
    error_latencies = [r["latency_ms"] for r in records if r["status"] != "success"]

    avg_all = int(sum(all_latencies) / len(all_latencies)) if all_latencies else 0
    avg_success = int(sum(success_latencies) / len(success_latencies)) if success_latencies else 0
    avg_error = int(sum(error_latencies) / len(error_latencies)) if error_latencies else 0

    return {
        "total": total,
        "success": success,
        "error": error,
        "executable_rate": round(success / total, 4),
        "correct_count": correct,
        "correctness_rate": round(correct / total, 4),
        "avg_latency_all_ms": avg_all,
        "avg_latency_success_ms": avg_success,
        "avg_latency_error_ms": avg_error,
    }


def write_jsonl(records, path: Path):
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def top_error(records, max_len: int = 120):
    errors = [r["error"] for r in records if r.get("error")]
    if not errors:
        return ""
    most_common = Counter(errors).most_common(1)[0][0]
    return most_common if len(most_common) <= max_len else most_common[: max_len - 3] + "..."


def build_failure_index(strategy_records):
    case_fail_counts = Counter()
    case_meta = {}

    for strategy, records in strategy_records.items():
        for r in records:
            case_id = r["id"]
            case_meta[case_id] = {
                "id": case_id,
                "task": r.get("task", ""),
                "query": r.get("query", ""),
            }
            if r.get("status") != "success":
                case_fail_counts[case_id] += 1

    return case_fail_counts, case_meta


def persistent_failures(strategy_records):
    if not strategy_records:
        return []

    strategy_errors = []
    for _, records in strategy_records.items():
        strategy_errors.append({r["id"] for r in records if r.get("status") != "success"})

    if not strategy_errors:
        return []

    return sorted(strategy_errors[0].intersection(*strategy_errors[1:]))


def write_markdown_summary(rows, path: Path, strategy_records):
    lines = [
        "# Prompt Strategy Evaluation Summary",
        "",
        "| Strategy | #Cases | Success | Error | Executable Rate | Correct | Correctness Rate | Avg Latency All (ms) | Avg Latency Success (ms) | Avg Latency Error (ms) | Top Error |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]

    for row in rows:
        lines.append(
            "| {strategy} | {cases} | {success} | {error} | {rate} | {correct} | {correct_rate} | {lat_all} | {lat_success} | {lat_error} | {top_error} |".format(
                strategy=row["strategy"],
                cases=row["total"],
                success=row["success"],
                error=row["error"],
                rate=f"{row['executable_rate'] * 100:.2f}%",
                correct=row["correct_count"],
                correct_rate=f"{row['correctness_rate'] * 100:.2f}%",
                lat_all=row["avg_latency_all_ms"],
                lat_success=row["avg_latency_success_ms"],
                lat_error=row["avg_latency_error_ms"],
                top_error=row["top_error"] or "",
            )
        )

    case_fail_counts, case_meta = build_failure_index(strategy_records)
    persistent_ids = persistent_failures(strategy_records)

    lines.extend([
        "",
        "## Persistent Failures Across Strategies",
    ])

    if persistent_ids:
        lines.append("")
        lines.append("| Case ID | Task | Query | Fail Count |")
        lines.append("|---:|---|---|---:|")
        for case_id in persistent_ids:
            meta = case_meta.get(case_id, {"task": "", "query": ""})
            lines.append(
                "| {id} | {task} | {query} | {fail_count} |".format(
                    id=case_id,
                    task=meta.get("task", ""),
                    query=meta.get("query", "").replace("|", "\\|"),
                    fail_count=case_fail_counts.get(case_id, 0),
                )
            )
    else:
        lines.append("")
        lines.append("No case failed in all selected strategies.")

    lines.extend([
        "",
        "## Most Unstable Cases",
        "",
        "| Case ID | Task | Query | Fail Count |",
        "|---:|---|---|---:|",
    ])

    for case_id, fail_count in case_fail_counts.most_common(8):
        meta = case_meta.get(case_id, {"task": "", "query": ""})
        lines.append(
            "| {id} | {task} | {query} | {fail_count} |".format(
                id=case_id,
                task=meta.get("task", ""),
                query=meta.get("query", "").replace("|", "\\|"),
                fail_count=fail_count,
            )
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Run NL2SQL prompt strategy evaluation.")
    parser.add_argument("--eval-file", default=str(BASE_DIR / "nl2sql_eval_set.json"))
    parser.add_argument("--strategy", default="hybrid", choices=["zero-shot", "few-shot", "constrained", "hybrid"])
    parser.add_argument("--all-strategies", action="store_true")
    parser.add_argument("--db", default="movies.db")
    parser.add_argument("--out", default=None)
    parser.add_argument("--summary-out", default=str(BASE_DIR / "prompt_eval_summary.md"))
    parser.add_argument("--case-delay-sec", type=float, default=1.5)
    parser.add_argument("--strategy-delay-sec", type=float, default=8.0)
    parser.add_argument("--max-case-retries", type=int, default=1)
    parser.add_argument("--rate-limit-wait-sec", type=float, default=18.0)
    args = parser.parse_args()

    eval_file = Path(args.eval_file)
    cases = load_eval_cases(eval_file)
    service = LLMQueryService(db_path=args.db)

    strategies = ["zero-shot", "few-shot", "constrained", "hybrid"] if args.all_strategies else [args.strategy]

    summary_rows = []
    output_files = []
    strategy_records = {}

    for strategy in strategies:
        records = evaluate(
            service=service,
            cases=cases,
            strategy=strategy,
            case_delay_sec=max(0.0, args.case_delay_sec),
            max_case_retries=max(0, args.max_case_retries),
            rate_limit_wait_sec=max(1.0, args.rate_limit_wait_sec),
            db_path=args.db,
        )
        summary = summarize(records)
        summary["strategy"] = strategy
        summary["top_error"] = top_error(records)
        summary_rows.append(summary)
        strategy_records[strategy] = records

        out_file = (
            Path(args.out)
            if args.out and len(strategies) == 1
            else BASE_DIR / f"eval_results_{strategy}.jsonl"
        )
        write_jsonl(records, out_file)
        output_files.append(str(out_file))

        if strategy != strategies[-1] and args.strategy_delay_sec > 0:
            time.sleep(args.strategy_delay_sec)

    summary_path = Path(args.summary_out)
    write_markdown_summary(summary_rows, summary_path, strategy_records)

    print(
        json.dumps(
            {
                "summaries": summary_rows,
                "outputs": output_files,
                "summary_markdown": str(summary_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
