from typing import Dict, List, Any


def compute_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    broken = [r for r in rows if r["kind"] == "broken"]
    correct = [r for r in rows if r["kind"] == "correct"]
    repaired = [r for r in broken if r["success"]]

    return {
        "total_cases": total,
        "broken_cases": len(broken),
        "correct_cases": len(correct),
        "pass@1": round(sum(1 for r in correct if r["success"]) / max(1, len(correct)), 3),
        "repair_success": round(len(repaired) / max(1, len(broken)), 3),
        "avg_iterations": round(sum(r["iterations"] for r in rows) / max(1, total), 2),
        "avg_diff_size": round(sum(r["diff_size"] for r in rows) / max(1, total), 1),
    }
