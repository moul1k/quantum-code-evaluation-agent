import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any


RUNNER = r'''
import json
import traceback

result = {
    "ok": False,
    "stdout": "",
    "stderr": "",
    "counts": None,
    "statevector": None,
    "circuit_qasm": None,
    "exports": [],
}

code = __CODE__
g = {}
try:
    exec(code, g, g)
    exports = [k for k in ["counts", "statevector", "circuit"] if k in g]
    result["exports"] = exports

    if "counts" in g and isinstance(g["counts"], dict):
        result["counts"] = {str(k): int(v) for k, v in g["counts"].items()}

    if "statevector" in g:
        sv = g["statevector"]
        try:
            data = list(sv.data)
            result["statevector"] = [[float(c.real), float(c.imag)] for c in data]
        except Exception:
            pass

    if "circuit" in g:
        circ = g["circuit"]
        try:
            result["circuit_qasm"] = circ.qasm()
        except Exception:
            try:
                from qiskit import qasm2
                result["circuit_qasm"] = qasm2.dumps(circ)
            except Exception:
                pass

    result["ok"] = True
except Exception:
    result["stderr"] = traceback.format_exc()

print(json.dumps(result))
'''


def run_code(code: str, timeout_s: int = 10) -> Dict[str, Any]:
    wrapper = RUNNER.replace("__CODE__", repr(code))
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "runner_tmp.py"
        path.write_text(wrapper, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    stdout, stderr = proc.stdout, proc.stderr
    parsed: Dict[str, Any] = {
        "ok": False,
        "stdout": stdout,
        "stderr": stderr,
        "counts": None,
        "statevector": None,
        "circuit_qasm": None,
        "exports": [],
    }
    if proc.returncode != 0 and not stdout.strip():
        parsed["stderr"] = stderr or f"Process failed with code {proc.returncode}"
        return parsed

    try:
        data = json.loads(stdout.strip().splitlines()[-1])
        parsed.update(data)
        parsed["stdout"] = stdout
        parsed["stderr"] = parsed.get("stderr", "") + ("\n" + stderr if stderr else "")
        return parsed
    except Exception:
        parsed["stderr"] = (stderr or "") + "\nFailed to parse runner JSON output."
        return parsed
