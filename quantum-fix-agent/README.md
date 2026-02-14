# Quantum Fix Agent (MVP)

A weekend-shippable **Qiskit-only** agent that evaluates and auto-repairs broken quantum code for two tasks:
- `bell`
- `ghz` (3 qubits)

It runs a loop: **evaluate → diagnose → patch → re-run** (up to 3 iterations), then reports trace + diff.

## Features
- CLI orchestrator for single snippet repair
- Evaluation harness over a small broken-snippet dataset
- Minimal Streamlit demo UI
- Reproducible setup with `requirements.txt`

## Install
```bash
cd quantum-fix-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run full evaluation
```bash
python -m eval.runner
```
Expected: completes without error and reports aggregate metrics.

## Run agent on one file
```bash
python -m agent.orchestrator --file eval/cases/bell/broken_01_missing_import.py --task bell
```

## Run Streamlit app
```bash
streamlit run app/streamlit_app.py
```

## Input contract
Snippet should define at least one of:
- `circuit` (`QuantumCircuit`), or
- `counts` (`dict`), or
- `statevector` (`Statevector`)

If missing, agent treats it as failure and attempts minimal patching.

## Scope
- Qiskit only
- Tasks: Bell and GHZ(3)
- Minimal string-based patching for high-yield failures
