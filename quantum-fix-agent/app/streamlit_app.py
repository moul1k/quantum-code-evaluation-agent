import streamlit as st

from agent.orchestrator import evaluate_once, run_agent_loop
from tools.diff import make_unified_diff


st.set_page_config(page_title="Quantum Fix Agent", layout="wide")
st.title("Quantum Code Evaluation + Fixing Agent (MVP)")

default_code = """from qiskit import QuantumCircuit
circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0,1)
"""

code = st.text_area("Paste Python snippet", value=default_code, height=260)
task = st.selectbox("Task", ["bell", "ghz"])

col1, col2 = st.columns(2)

if col1.button("Evaluate"):
    res = evaluate_once(code, task)
    st.subheader("Evaluation")
    st.json(res)

if col2.button("Fix"):
    result = run_agent_loop(code, task)
    st.subheader("Result")
    st.write({"success": result.success, "iterations": result.iterations})

    st.subheader("Diff")
    st.code(result.diff or "(no diff)", language="diff")

    st.subheader("Patched code")
    st.code(result.patched_code, language="python")

    st.subheader("Counts")
    st.json(result.quantum.get("counts", {}))

    st.subheader("Trace")
    for step in result.trace:
        st.write({
            "tool": step.tool,
            "status": step.status,
            "summary": step.summary,
            "key_outputs": step.key_outputs,
        })
