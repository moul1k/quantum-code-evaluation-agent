from typing import Dict


def classify_code(code: str, task_hint: str = "") -> Dict[str, str]:
    task = (task_hint or "").strip().lower()
    if task not in {"bell", "ghz"}:
        lowered = code.lower()
        if "ghz" in lowered or "000" in lowered or "111" in lowered:
            task = "ghz"
        else:
            task = "bell"
    return {"framework": "qiskit", "task": task}
