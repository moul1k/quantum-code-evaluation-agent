from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0,1], [0,1])
backend = Aer.get_backend('aer_simulator')
tqc = transpile(circuit, backend)
job = backend.run(tqc, shots=64)
counts = job.result().get_counts()
