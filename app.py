# app.py

import streamlit as st
import pandas as pd

from src.log_parser import extract_error_lines
from src.error_classifier import classify_error
from src.report_generator import generate_report
from src.sample_data import get_sample_logs


def read_log_file(file_path):
    """
    Read a log file from the local project folder.

    Parameters:
        file_path (str): Path of the log file.

    Returns:
        str: Full log file content.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def convert_report_to_text(report):
    """
    Convert report dictionary into readable text format.

    Parameters:
        report (dict): Troubleshooting report.

    Returns:
        str: Text version of the report.
    """

    error_lines_text = "\n".join(report["detected_error_lines"])

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

Probable Root Cause:
{report["probable_root_cause"]}

Suggested Fix:
{report["suggested_fix"]}

Final Summary:
{report["final_summary"]}
"""

    return report_text


def convert_report_to_dataframe(report):
    """
    Convert report dictionary into a pandas DataFrame for CSV export.

    Parameters:
        report (dict): Troubleshooting report.

    Returns:
        DataFrame: Report data in table format.
    """

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
        "Probable Root Cause": [report["probable_root_cause"]],
        "Suggested Fix": [report["suggested_fix"]],
        "Final Summary": [report["final_summary"]],
    }

    return pd.DataFrame(data)


def analyze_log(file_name, log_text):
    """
    Run the full log analysis pipeline.

    Parameters:
        file_name (str): Name of the log file.
        log_text (str): Full log content.

    Returns:
        dict: Troubleshooting report.
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
    "identify probable root cause, and generate a troubleshooting report."
)

# Initialize analysis history
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

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

        try:
            log_text = uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError:
            st.error(
                "Could not read the uploaded file. "
                "Please upload a UTF-8 encoded .log or .txt file."
            )
            log_text = None

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


if log_text:
    st.subheader("Log Preview")

    st.text_area(
        "Raw Log Content",
        log_text,
        height=220
    )

    if st.button("Analyze Log"):
        report = analyze_log(file_name, log_text)

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

        st.subheader("Probable Root Cause")
        st.write(report["probable_root_cause"])

        st.subheader("Suggested Fix")
        st.write(report["suggested_fix"])

        st.subheader("Final Summary")
        st.success(report["final_summary"])

        report_text = convert_report_to_text(report)
        report_df = convert_report_to_dataframe(report)

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
            st.rerun()

else:
    st.info("Please select a sample log, upload a log file, or paste log text to start analysis.")