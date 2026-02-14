from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

circuit = QuantumCircuit(3, 3)
circuit.h(0)
circuit.cx(0, 1)
circuit.cx(1, 2)
circuit.measure([0,1,2], [0,1,2])
backend = Aer.get_backend('aer_simulator')
job = backend.run(transpile(circuit, backend), shots=32)
counts = job.result().get_counts()
