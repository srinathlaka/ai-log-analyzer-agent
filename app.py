# app.py

import streamlit as st
import pandas as pd

from src.log_parser import extract_error_lines
from src.error_classifier import classify_error
from src.report_generator import generate_report
from src.sample_data import get_sample_logs
from src.ai_recommender import generate_ai_recommendation, check_ollama_status
from src.agent_engine import run_context_agent


def read_log_file(file_path):
    """
    Read a log file from the local project folder.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def read_uploaded_text_file(uploaded_file):
    """
    Read uploaded text file safely.
    """

    if uploaded_file is None:
        return None

    try:
        return uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        st.error(
            f"Could not read {uploaded_file.name}. "
            "Please upload a UTF-8 encoded text file."
        )
        return None


def convert_report_to_text(report, agent_result=None, ai_recommendation=None):
    """
    Convert report dictionary into readable text format.
    """

    error_lines_text = "\n".join(report["detected_error_lines"])

    agent_text = ""
    if agent_result:
        agent_steps = "\n".join(f"- {step}" for step in agent_result["agent_steps"])
        findings = "\n".join(f"- {finding}" for finding in agent_result["context_findings"])
        recommendations = "\n".join(
            f"- {recommendation}"
            for recommendation in agent_result["context_recommendations"]
        )

        agent_text = f"""

Context-Aware Agent Findings
============================

Agent Steps:
{agent_steps}

Context Findings:
{findings}

Context-Aware Recommendations:
{recommendations}

Agent Summary:
{agent_result["final_agent_summary"]}
"""

    ai_text = ""
    if ai_recommendation:
        ai_text = f"""

Local AI Recommendation
=======================

{ai_recommendation}
"""

    report_text = f"""
CI/CD Log Troubleshooting Report
================================

Log File Name:
{report["file_name"]}

Primary Failure Category:
{report["primary_category"]}

Secondary Categories:
{", ".join(report["secondary_categories"]) if report["secondary_categories"] else "None"}

All Detected Categories:
{", ".join(report["all_detected_categories"])}

Confidence Level:
{report["confidence_level"]}

Severity Level:
{report["severity_level"]}

Detected Error Lines:
{error_lines_text}

Rule-Based Root Cause:
{report["probable_root_cause"]}

Rule-Based Suggested Fix:
{report["suggested_fix"]}

Final Summary:
{report["final_summary"]}
{agent_text}
{ai_text}
"""

    return report_text


def convert_report_to_dataframe(report, agent_result=None, ai_recommendation=None):
    """
    Convert report dictionary into a pandas DataFrame for CSV export.
    """

    agent_findings = "None"
    agent_recommendations = "None"

    if agent_result:
        agent_findings = " | ".join(agent_result["context_findings"])
        agent_recommendations = " | ".join(agent_result["context_recommendations"])

    data = {
        "File Name": [report["file_name"]],
        "Primary Category": [report["primary_category"]],
        "Secondary Categories": [
            ", ".join(report["secondary_categories"])
            if report["secondary_categories"]
            else "None"
        ],
        "All Detected Categories": [", ".join(report["all_detected_categories"])],
        "Confidence Level": [report["confidence_level"]],
        "Severity Level": [report["severity_level"]],
        "Detected Error Lines": [" | ".join(report["detected_error_lines"])],
        "Rule-Based Root Cause": [report["probable_root_cause"]],
        "Rule-Based Suggested Fix": [report["suggested_fix"]],
        "Context Agent Findings": [agent_findings],
        "Context Agent Recommendations": [agent_recommendations],
        "Local AI Recommendation": [ai_recommendation if ai_recommendation else "Not generated"],
        "Final Summary": [report["final_summary"]],
    }

    return pd.DataFrame(data)


def analyze_log(file_name, log_text):
    """
    Run the full log analysis pipeline.
    """

    error_lines = extract_error_lines(log_text)
    classification = classify_error(error_lines)
    report = generate_report(file_name, error_lines, classification)

    return report


st.set_page_config(
    page_title="Local AI Agent for CI/CD Log Analysis",
    page_icon="🛠️",
    layout="wide"
)

st.title("Local AI Agent for CI/CD Log Analysis")

st.write(
    "Upload, paste, or select a CI/CD-style log file to detect errors, classify the failure type, "
    "identify probable root cause, inspect optional project context files, and generate a troubleshooting report."
)

# Initialize session state
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

if "latest_report" not in st.session_state:
    st.session_state.latest_report = None

if "latest_ai_recommendation" not in st.session_state:
    st.session_state.latest_ai_recommendation = None

if "latest_agent_result" not in st.session_state:
    st.session_state.latest_agent_result = None


# Sidebar: Local AI status
st.sidebar.header("Local AI Status")

ollama_status = check_ollama_status()

ai_ready = (
    ollama_status["ollama_running"]
    and ollama_status["model_available"]
)

if ai_ready:
    st.sidebar.success("Local AI: Available")
    st.sidebar.write("Model: qwen2.5:1.5b")

elif ollama_status["ollama_running"] and not ollama_status["model_available"]:
    st.sidebar.warning("Ollama is running, but the required model is missing.")
    st.sidebar.write("Run this command:")
    st.sidebar.code("ollama pull qwen2.5:1.5b")

else:
    st.sidebar.error("Local AI: Not running")
    st.sidebar.write("Start Ollama and try again.")


# Sidebar: Input options
st.sidebar.header("Input Options")

input_option = st.sidebar.radio(
    "Choose log input method",
    ["Use built-in sample log", "Upload log file", "Paste log text"]
)

log_text = None
file_name = None

if input_option == "Use built-in sample log":
    sample_logs = get_sample_logs()

    selected_sample = st.sidebar.selectbox(
        "Choose a sample log",
        list(sample_logs.keys())
    )

    file_path = sample_logs[selected_sample]
    file_name = file_path
    log_text = read_log_file(file_path)

elif input_option == "Upload log file":
    uploaded_file = st.sidebar.file_uploader(
        "Upload a .log or .txt file",
        type=["log", "txt"]
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name
        log_text = read_uploaded_text_file(uploaded_file)

else:
    file_name = "pasted_log_text.txt"

    log_text = st.text_area(
        "Paste your CI/CD log text here",
        height=250,
        placeholder=(
            "Paste error logs here, for example:\n"
            "ERROR: ModuleNotFoundError: No module named 'numpy'\n"
            "FAILED tests/test_app.py::test_login\n"
            "Deployment failed"
        )
    )


# Sidebar: Optional project context files
st.sidebar.header("Optional Project Context")

st.sidebar.write(
    "Upload related project files so the local agent can inspect them "
    "and generate context-aware findings."
)

requirements_file = st.sidebar.file_uploader(
    "Upload requirements.txt",
    type=["txt"],
    key="requirements_upload"
)

dockerfile_upload = st.sidebar.file_uploader(
    "Upload Dockerfile",
    key="dockerfile_upload"
)

workflow_file = st.sidebar.file_uploader(
    "Upload workflow YAML",
    type=["yml", "yaml", "txt"],
    key="workflow_upload"
)

context_files = {
    "requirements.txt": read_uploaded_text_file(requirements_file),
    "Dockerfile": read_uploaded_text_file(dockerfile_upload),
    "workflow.yml": read_uploaded_text_file(workflow_file),
}


if log_text:
    st.subheader("Log Preview")

    st.text_area(
        "Raw Log Content",
        log_text,
        height=220
    )

    if st.button("Analyze Log"):
        report = analyze_log(file_name, log_text)

        # Run context-aware local agent
        agent_result = run_context_agent(report, context_files)

        # Store latest outputs
        st.session_state.latest_report = report
        st.session_state.latest_agent_result = agent_result
        st.session_state.latest_ai_recommendation = None

        history_item = {
            "File Name": report["file_name"],
            "Primary Category": report["primary_category"],
            "Secondary Categories": (
                ", ".join(report["secondary_categories"])
                if report["secondary_categories"]
                else "None"
            ),
            "Severity": report["severity_level"],
            "Confidence": report["confidence_level"],
            "Detected Lines": len(report["detected_error_lines"]),
        }

        st.session_state.analysis_history.append(history_item)

    if st.session_state.latest_report is not None:
        report = st.session_state.latest_report
        agent_result = st.session_state.latest_agent_result

        st.subheader("Analysis Result")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Primary Category", report["primary_category"])

        with col2:
            st.metric("Confidence", report["confidence_level"])

        with col3:
            st.metric("Severity", report["severity_level"])

        with col4:
            st.metric("Detected Lines", len(report["detected_error_lines"]))

        st.subheader("Detected Categories")

        st.write("**Primary Category:**", report["primary_category"])

        if report["secondary_categories"]:
            st.write(
                "**Secondary Categories:**",
                ", ".join(report["secondary_categories"])
            )
        else:
            st.write("**Secondary Categories:** None")

        st.write(
            "**All Detected Categories:**",
            ", ".join(report["all_detected_categories"])
        )

        st.subheader("Detected Error Lines")

        if report["detected_error_lines"]:
            for line in report["detected_error_lines"]:
                st.code(line)
        else:
            st.info("No important error lines were detected.")

        st.subheader("Rule-Based Root Cause")
        st.write(report["probable_root_cause"])

        st.subheader("Rule-Based Suggested Fix")
        st.write(report["suggested_fix"])

        st.subheader("Context-Aware Agent Findings")

        if agent_result:
            st.write("**Agent Steps:**")
            for step in agent_result["agent_steps"]:
                st.write("-", step)

            st.write("**Context Findings:**")
            for finding in agent_result["context_findings"]:
                st.info(finding)

            st.write("**Context-Aware Recommendations:**")
            for recommendation in agent_result["context_recommendations"]:
                st.success(recommendation)

            st.write("**Agent Summary:**")
            st.write(agent_result["final_agent_summary"])
        else:
            st.info("No context-aware agent result is available yet.")

        st.subheader("Final Summary")
        st.success(report["final_summary"])

        st.subheader("Local AI Recommendation")

        st.write(
            "Generate an AI-assisted explanation using the local Ollama model. "
            "The button is enabled only when Ollama is running and the required model is available."
        )

        if st.button("Generate Local AI Recommendation", disabled=not ai_ready):
            with st.spinner("Generating recommendation using local Ollama model..."):
                ai_recommendation = generate_ai_recommendation(report)

            st.session_state.latest_ai_recommendation = ai_recommendation

        if not ai_ready:
            st.warning(
                "Local AI recommendation is disabled because Ollama or the required model is not available."
            )

        if st.session_state.latest_ai_recommendation:
            st.markdown(st.session_state.latest_ai_recommendation)

        report_text = convert_report_to_text(
            report,
            agent_result=agent_result,
            ai_recommendation=st.session_state.latest_ai_recommendation
        )

        report_df = convert_report_to_dataframe(
            report,
            agent_result=agent_result,
            ai_recommendation=st.session_state.latest_ai_recommendation
        )

        st.subheader("Download Report")

        st.download_button(
            label="Download TXT Report",
            data=report_text,
            file_name="troubleshooting_report.txt",
            mime="text/plain"
        )

        csv_data = report_df.to_csv(index=False)

        st.download_button(
            label="Download CSV Report",
            data=csv_data,
            file_name="troubleshooting_report.csv",
            mime="text/csv"
        )

    if st.session_state.analysis_history:
        st.subheader("Analysis History")

        history_df = pd.DataFrame(st.session_state.analysis_history)

        st.dataframe(
            history_df,
            use_container_width=True
        )

        if st.button("Clear History"):
            st.session_state.analysis_history = []
            st.session_state.latest_report = None
            st.session_state.latest_agent_result = None
            st.session_state.latest_ai_recommendation = None
            st.rerun()

else:
    st.info(
        "Please select a sample log, upload a log file, or paste log text to start analysis."
    )