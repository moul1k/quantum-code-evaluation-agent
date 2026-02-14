from pathlib import Path
from typing import Dict, Any, List

from agent.orchestrator import run_agent_loop
from eval.metrics import compute_metrics


ROOT = Path(__file__).resolve().parents[1]


def _load_tasks() -> Dict[str, Any]:
    text = (ROOT / "eval" / "tasks.yaml").read_text(encoding="utf-8")
    tasks: Dict[str, Any] = {}
    in_tasks = False
    for line in text.splitlines():
        raw = line.rstrip()
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if raw.strip() == "tasks:":
            in_tasks = True
            continue
        if in_tasks and raw.startswith("  ") and raw.strip().endswith(":") and not raw.strip().startswith("description"):
            name = raw.strip().rstrip(":")
            tasks[name] = {}
        if in_tasks and "description:" in raw and tasks:
            tasks[list(tasks.keys())[-1]]["description"] = raw.split("description:", 1)[1].strip()
    return tasks


def _collect_cases(task: str) -> List[Path]:
    return sorted((ROOT / "eval" / "cases" / task).glob("*.py"))


def run_eval() -> Dict[str, Any]:
    tasks = _load_tasks()
    rows: List[Dict[str, Any]] = []

    for task in tasks.keys():
        for case in _collect_cases(task):
            code = case.read_text(encoding="utf-8")
            result = run_agent_loop(code, task)
            rows.append(
                {
                    "task": task,
                    "case": case.name,
                    "kind": "correct" if "correct" in case.name else "broken",
                    "success": result.success,
                    "iterations": result.iterations,
                    "diff_size": len(result.diff.splitlines()) if result.diff else 0,
                }
            )

    metrics = compute_metrics(rows)
    return {"rows": rows, "metrics": metrics}


def _print_summary(report: Dict[str, Any]) -> None:
    print("\n=== Case Results ===")
    for r in report["rows"]:
        status = "PASS" if r["success"] else "FAIL"
        print(f"{r['task']:4} | {r['case']:<34} | {r['kind']:<7} | {status} | iters={r['iterations']}")

    print("\n=== Metrics ===")
    for k, v in report["metrics"].items():
        print(f"{k:16}: {v}")


if __name__ == "__main__":
    report = run_eval()
    _print_summary(report)
