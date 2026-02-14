import ast
from typing import Dict, Any


REQUIRED_EXPORTS = {"circuit", "counts", "statevector"}


def run_static_check(code: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"ok": False, "syntax_ok": False, "exports_present": []}
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        out.update({"error": f"SyntaxError: {e.msg} at line {e.lineno}"})
        return out

    out["syntax_ok"] = True
    assigned = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    assigned.add(tgt.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assigned.add(node.target.id)

    present = sorted(REQUIRED_EXPORTS.intersection(assigned))
    out["exports_present"] = present
    out["ok"] = True
    if not present:
        out["warning"] = "No required output variable assigned (circuit/counts/statevector)."
    return out
