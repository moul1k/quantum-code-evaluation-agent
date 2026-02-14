from typing import Dict, Any, Tuple


VALID_STATES = {
    "bell": ("00", "11"),
    "ghz": ("000", "111"),
}


def _simulate_circuit(qasm: str, shots: int = 512) -> Dict[str, int]:
    if not qasm:
        return {}
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import Aer

    circuit = QuantumCircuit.from_qasm_str(qasm)
    if circuit.num_clbits == 0:
        circuit.measure_all()
    backend = Aer.get_backend("aer_simulator")
    tqc = transpile(circuit, backend)
    job = backend.run(tqc, shots=max(256, shots))
    result = job.result()
    return result.get_counts()


def _check_distribution(counts: Dict[str, int], task: str) -> Tuple[bool, str]:
    if task not in VALID_STATES:
        return False, f"Unsupported task: {task}"
    zeros, ones = VALID_STATES[task]
    total = sum(counts.values())
    if total < 256:
        return False, f"Not enough shots: {total}"

    p0 = counts.get(zeros, 0) / total
    p1 = counts.get(ones, 0) / total
    concentrated = (counts.get(zeros, 0) + counts.get(ones, 0)) / total

    if concentrated < 0.8:
        return False, f"Distribution not concentrated on {zeros}/{ones}: {concentrated:.2f}"
    if not (0.3 <= p0 <= 0.7 and 0.3 <= p1 <= 0.7):
        return False, f"Probabilities not near 50/50: p({zeros})={p0:.2f}, p({ones})={p1:.2f}"
    return True, "Quantum distribution check passed"


def run_quantum_check(task: str, run_result: Dict[str, Any]) -> Dict[str, Any]:
    counts = run_result.get("counts")
    if not counts and run_result.get("circuit_qasm"):
        try:
            counts = _simulate_circuit(run_result["circuit_qasm"], shots=512)
        except ModuleNotFoundError as e:
            return {"ok": False, "error": f"Missing dependency: {e}", "counts": {}}
        except Exception as e:
            return {"ok": False, "error": f"Simulation failed: {e}", "counts": {}}

    if not counts:
        return {"ok": False, "error": "No counts or simulatable circuit found", "counts": {}}

    ok, summary = _check_distribution(counts, task)
    return {"ok": ok, "summary": summary, "counts": counts}
