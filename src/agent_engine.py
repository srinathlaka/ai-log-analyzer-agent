# src/agent_engine.py

"""
This file acts as the simple local troubleshooting agent engine.

Main purpose:
- Look at the report generated from the log
- Decide which project context file should be inspected
- Use context inspection tools
- Return evidence-based findings and recommendations
"""

from src.context_inspector import (
    extract_missing_python_package,
    inspect_requirements_file,
    inspect_dockerfile,
    inspect_workflow_file,
)


def run_context_agent(report, context_files):
    """
    Run a simple context-aware troubleshooting agent.

    Parameters:
        report (dict): Troubleshooting report from the log analyzer.
        context_files (dict): Uploaded project context files.

    Returns:
        dict: Agent decision, findings, and context-aware recommendation.
    """

    primary_category = report["primary_category"]
    error_lines = report["detected_error_lines"]

    agent_steps = []
    findings = []
    recommendations = []

    requirements_text = context_files.get("requirements.txt")
    dockerfile_text = context_files.get("Dockerfile")
    workflow_text = context_files.get("workflow.yml")

    if primary_category == "Dependency Error":
        agent_steps.append("Detected Dependency Error. Inspecting requirements.txt.")

        missing_package = extract_missing_python_package(error_lines)

        result = inspect_requirements_file(
            requirements_text=requirements_text,
            missing_package=missing_package
        )

        findings.append(result["finding"])
        recommendations.append(result["recommendation"])

    elif primary_category == "Docker Build Error":
        agent_steps.append("Detected Docker Build Error. Inspecting Dockerfile.")

        result = inspect_dockerfile(dockerfile_text)

        findings.append(result["finding"])
        recommendations.append(result["recommendation"])

    elif primary_category == "YAML Syntax Error":
        agent_steps.append("Detected YAML Syntax Error. Inspecting workflow YAML file.")

        result = inspect_workflow_file(workflow_text)

        findings.append(result["finding"])
        recommendations.append(result["recommendation"])

    elif primary_category == "Test Failure":
        agent_steps.append("Detected Test Failure. Checking workflow configuration if provided.")

        result = inspect_workflow_file(workflow_text)

        findings.append(result["finding"])
        recommendations.append(result["recommendation"])

    elif primary_category == "Deployment Error":
        agent_steps.append("Detected Deployment Error. Checking workflow configuration if provided.")

        result = inspect_workflow_file(workflow_text)

        findings.append(result["finding"])
        recommendations.append(result["recommendation"])

    else:
        agent_steps.append(
            f"Detected {primary_category}. No specific context inspection tool is available yet."
        )

        findings.append(
            "The agent could not perform a specific project file inspection for this category."
        )

        recommendations.append(
            "Review the detected error lines and upload related project files if available."
        )

    final_agent_summary = (
        "The context-aware agent inspected available project files based on the primary "
        "failure category and generated evidence-based findings."
    )

    return {
        "agent_steps": agent_steps,
        "context_findings": findings,
        "context_recommendations": recommendations,
        "final_agent_summary": final_agent_summary
    }