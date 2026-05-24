# src/context_inspector.py

"""
This file inspects optional project context files.

Main purpose:
- Read uploaded project files such as requirements.txt, Dockerfile, or workflow YAML
- Check whether the detected log error is supported by evidence in project files
- Generate context-aware findings for the troubleshooting agent
"""


def extract_missing_python_package(error_lines):
    """
    Extract missing Python package name from ModuleNotFoundError lines.

    Example:
        ModuleNotFoundError: No module named 'numpy'

    Returns:
        str or None
    """

    for line in error_lines:
        lower_line = line.lower()

        if "no module named" in lower_line:
            parts = line.split("No module named")

            if len(parts) > 1:
                package_name = parts[1].strip()
                package_name = package_name.replace("'", "").replace('"', "")
                package_name = package_name.strip()

                return package_name

    return None


def inspect_requirements_file(requirements_text, missing_package):
    """
    Check whether a missing Python package is present in requirements.txt.

    Parameters:
        requirements_text (str): Content of requirements.txt.
        missing_package (str): Package name detected from log.

    Returns:
        dict: Inspection result.
    """

    if not requirements_text:
        return {
            "status": "not_checked",
            "finding": "requirements.txt was not provided, so dependency evidence could not be checked.",
            "recommendation": "Upload requirements.txt to verify whether the missing package is listed."
        }

    if not missing_package:
        return {
            "status": "not_applicable",
            "finding": "No missing Python package name was detected from the log.",
            "recommendation": "No requirements.txt-specific recommendation is available."
        }

    requirements_lower = requirements_text.lower()
    package_lower = missing_package.lower()

    if package_lower in requirements_lower:
        return {
            "status": "found",
            "finding": f"The package '{missing_package}' appears to be listed in requirements.txt.",
            "recommendation": (
                "Check whether the CI/CD pipeline installs requirements.txt correctly "
                "before running the application or tests."
            )
        }

    return {
        "status": "missing",
        "finding": f"The package '{missing_package}' is missing from requirements.txt.",
        "recommendation": f"Add '{missing_package}' to requirements.txt and rerun the pipeline."
    }


def inspect_dockerfile(dockerfile_text):
    """
    Inspect Dockerfile content for simple common issues.

    Parameters:
        dockerfile_text (str): Content of Dockerfile.

    Returns:
        dict: Inspection result.
    """

    if not dockerfile_text:
        return {
            "status": "not_checked",
            "finding": "Dockerfile was not provided, so Docker build context could not be checked.",
            "recommendation": "Upload Dockerfile to inspect Docker-related build issues."
        }

    dockerfile_lower = dockerfile_text.lower()

    findings = []
    recommendations = []

    if "copy requirements.txt" not in dockerfile_lower and "pip install" in dockerfile_lower:
        findings.append("Dockerfile uses pip install but does not clearly copy requirements.txt.")
        recommendations.append("Check whether requirements.txt is copied before running pip install.")

    if "workdir" not in dockerfile_lower:
        findings.append("Dockerfile does not define a WORKDIR instruction.")
        recommendations.append("Add a WORKDIR instruction to make file paths more predictable.")

    if not findings:
        return {
            "status": "checked",
            "finding": "No obvious Dockerfile issue was detected using the current simple checks.",
            "recommendation": "Review the Docker build step and verify file paths, COPY commands, and build context."
        }

    return {
        "status": "issue_found",
        "finding": " ".join(findings),
        "recommendation": " ".join(recommendations)
    }


def inspect_workflow_file(workflow_text):
    """
    Inspect GitHub Actions workflow YAML content for simple common issues.

    Parameters:
        workflow_text (str): Content of workflow YAML file.

    Returns:
        dict: Inspection result.
    """

    if not workflow_text:
        return {
            "status": "not_checked",
            "finding": "Workflow YAML file was not provided, so CI configuration could not be checked.",
            "recommendation": "Upload the GitHub Actions workflow YAML file to inspect CI configuration issues."
        }

    workflow_lower = workflow_text.lower()

    findings = []
    recommendations = []

    if "actions/checkout" not in workflow_lower:
        findings.append("Workflow file may be missing the actions/checkout step.")
        recommendations.append("Add actions/checkout before installing dependencies or running tests.")

    if "setup-python" not in workflow_lower and "python" in workflow_lower:
        findings.append("Workflow mentions Python but may not configure Python using setup-python.")
        recommendations.append("Use actions/setup-python to configure the required Python version.")

    if "pip install" not in workflow_lower and "pytest" in workflow_lower:
        findings.append("Workflow runs tests but no dependency installation step was found.")
        recommendations.append("Install dependencies before running pytest.")

    if not findings:
        return {
            "status": "checked",
            "finding": "No obvious GitHub Actions workflow issue was detected using the current simple checks.",
            "recommendation": "Review indentation, job steps, dependency installation, and test commands if the pipeline still fails."
        }

    return {
        "status": "issue_found",
        "finding": " ".join(findings),
        "recommendation": " ".join(recommendations)
    }