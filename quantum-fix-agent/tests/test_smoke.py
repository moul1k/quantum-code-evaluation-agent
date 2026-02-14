import importlib.util
import unittest

from agent.orchestrator import run_agent_loop


BELL_BROKEN = """from qiskit import QuantumCircuit
circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0,1)
"""


@unittest.skipUnless(importlib.util.find_spec("qiskit") is not None, "qiskit not installed")
class SmokeTests(unittest.TestCase):
    def test_repair_bell(self):
        result = run_agent_loop(BELL_BROKEN, "bell")
        self.assertTrue(result.success)
        self.assertIn("counts", result.quantum)


if __name__ == "__main__":
    unittest.main()
