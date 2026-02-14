import re
from typing import List


def _ensure_imports(code: str) -> str:
    lines = code.splitlines()
    joined = "\n".join(lines)
    inserts = []
    if "QuantumCircuit" in code and "from qiskit import" not in joined:
        inserts.append("from qiskit import QuantumCircuit, transpile")
    elif "from qiskit import" in joined and "transpile" not in joined:
        joined = joined.replace("from qiskit import", "from qiskit import transpile,")
    if "Aer" not in joined and "qiskit_aer" not in joined:
        inserts.append("from qiskit_aer import Aer")
    if inserts:
        return "\n".join(inserts + [code])
    return joined


def _ensure_measurement(code: str) -> str:
    if "circuit" not in code:
        return code
    if ".measure" in code or ".measure_all" in code:
        return code
    return code + "\n\n# auto-fix: ensure measurement\ncircuit.measure_all()\n"


def _ensure_backend_run(code: str) -> str:
    if "counts" in code and "backend.run" in code:
        return code
    if "circuit" not in code:
        return code

    if "Aer.get_backend" in code and "get_counts" in code:
        return code

    block = """
# auto-fix: run on simulator
backend = Aer.get_backend('aer_simulator')
tqc = transpile(circuit, backend)
job = backend.run(tqc, shots=512)
counts = job.result().get_counts()
""".strip("\n")
    return code.rstrip() + "\n\n" + block + "\n"


def _fix_counts_usage(code: str) -> str:
    code = re.sub(r"counts\s*=\s*backend\.run\((.*?)\)\.result\(\)", r"job = backend.run(\1)\ncounts = job.result().get_counts()", code, flags=re.S)
    code = code.replace("counts = result.get_counts", "counts = result.get_counts()")
    return code


def _ensure_min_shots(code: str) -> str:
    if "shots=" not in code:
        return code

    def repl(match: re.Match) -> str:
        val = int(match.group(1))
        return f"shots={max(256, val)}"

    return re.sub(r"shots\s*=\s*(\d+)", repl, code)


def apply_patch(code: str, hints: List[str]) -> str:
    patched = code
    patched = _ensure_imports(patched)
    patched = _fix_counts_usage(patched)
    patched = _ensure_measurement(patched)
    patched = _ensure_backend_run(patched)
    patched = _ensure_min_shots(patched)
    return patched
