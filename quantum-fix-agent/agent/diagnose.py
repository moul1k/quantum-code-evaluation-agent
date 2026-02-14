from typing import Dict, Any, List


def diagnose(static_result: Dict[str, Any], run_result: Dict[str, Any], quantum_result: Dict[str, Any]) -> List[str]:
    hints: List[str] = []

    if not static_result.get("syntax_ok"):
        hints.append("Fix syntax errors before runtime fixes.")

    stderr = (run_result.get("stderr") or "").lower()
    exports = run_result.get("exports", [])

    if "nameerror" in stderr and "quantumcircuit" in stderr:
        hints.append("Add missing import: from qiskit import QuantumCircuit")
    if "aer" in stderr and "nameerror" in stderr:
        hints.append("Add Aer import and backend run path")
    if "get_counts" in stderr:
        hints.append("Use result.get_counts() after backend job.result()")

    if not exports:
        hints.append("Ensure snippet assigns circuit or counts or statevector variable")

    qerr = (quantum_result.get("error") or "") + " " + (quantum_result.get("summary") or "")
    qerr = qerr.lower()
    if "no counts" in qerr:
        hints.append("Generate counts by measuring and running on Aer simulator")
    if "not enough shots" in qerr:
        hints.append("Increase shots to at least 256")
    if "not concentrated" in qerr or "50/50" in qerr:
        hints.append("Fix entanglement circuit structure for target task")

    return hints
