import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from agent.classify import classify_code
from agent.diagnose import diagnose
from agent.patch import apply_patch
from tools.diff import make_unified_diff
from tools.quantum_check import run_quantum_check
from tools.run_code import run_code
from tools.static_check import run_static_check


@dataclass
class StepLog:
    tool: str
    status: str
    summary: str
    key_outputs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    success: bool
    iterations: int
    original_code: str
    patched_code: str
    diff: str
    trace: List[StepLog]
    quantum: Dict[str, Any]


def evaluate_once(code: str, task: str) -> Dict[str, Any]:
    static_result = run_static_check(code)
    run_result = run_code(code, timeout_s=10)
    quantum_result = run_quantum_check(task, run_result) if static_result.get("syntax_ok") else {"ok": False, "error": "Syntax failure"}
    return {
        "static": static_result,
        "run": run_result,
        "quantum": quantum_result,
        "ok": static_result.get("syntax_ok") and run_result.get("ok") and quantum_result.get("ok"),
    }


def run_agent_loop(code: str, task_hint: str, max_iters: int = 3) -> AgentResult:
    info = classify_code(code, task_hint=task_hint)
    task = info["task"]

    trace: List[StepLog] = []
    cur = code
    last_eval = None

    for i in range(1, max_iters + 1):
        ev = evaluate_once(cur, task)
        last_eval = ev
        trace.append(StepLog("static_check", "ok" if ev["static"].get("syntax_ok") else "fail", "Parsed code", {"warning": ev["static"].get("warning", "")}))
        trace.append(StepLog("run_code", "ok" if ev["run"].get("ok") else "fail", "Executed snippet", {"stderr": (ev['run'].get('stderr') or '')[:280]}))
        trace.append(StepLog("quantum_check", "ok" if ev["quantum"].get("ok") else "fail", ev["quantum"].get("summary", ev["quantum"].get("error", "")), {"counts": ev["quantum"].get("counts", {})}))

        if ev["ok"]:
            break

        hints = diagnose(ev["static"], ev["run"], ev["quantum"])
        trace.append(StepLog("diagnose", "ok", "Generated repair hints", {"hints": hints}))
        nxt = apply_patch(cur, hints)
        trace.append(StepLog("patch", "ok" if nxt != cur else "fail", "Applied minimal patch", {"changed": nxt != cur}))
        if nxt == cur:
            break
        cur = nxt

    success = bool(last_eval and last_eval["ok"])
    return AgentResult(
        success=success,
        iterations=min(max_iters, len([t for t in trace if t.tool == "static_check"])),
        original_code=code,
        patched_code=cur,
        diff=make_unified_diff(code, cur),
        trace=trace,
        quantum=(last_eval or {}).get("quantum", {}),
    )


def _main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Fix Agent orchestrator")
    parser.add_argument("--file", required=True, help="Path to snippet file")
    parser.add_argument("--task", choices=["bell", "ghz"], required=True)
    args = parser.parse_args()

    code = Path(args.file).read_text(encoding="utf-8")
    result = run_agent_loop(code, args.task)

    print(f"Success: {result.success}")
    print(f"Iterations: {result.iterations}")
    print("\n=== Diff ===")
    print(result.diff or "(no changes)")
    print("\n=== Patched Code ===")
    print(result.patched_code)


if __name__ == "__main__":
    _main()
