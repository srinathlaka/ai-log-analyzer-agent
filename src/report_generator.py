# src/report_generator.py

"""
This file generates root-cause explanations, recommended fixes,
and troubleshooting reports for CI/CD log analysis.
"""


def get_root_cause_and_fix(category):
    """
    Generate probable root cause and suggested fix based on failure category.

    Parameters:
        category (str): Primary failure category detected by the classifier.

    Returns:
        dict: Root cause and suggested fix.
    """

    if category == "Dependency Error":
        return {
            "root_cause": "The pipeline failed because a required Python package is missing or not installed in the environment.",
            "suggested_fix": "Check the requirements.txt file and install the missing package using pip. Also make sure the CI/CD pipeline installs dependencies before running the application or tests."
        }

    elif category == "Test Failure":
        return {
            "root_cause": "The pipeline failed because one or more automated tests did not pass.",
            "suggested_fix": "Review the failed test case, check the assertion logic, and fix the related application code or test data."
        }

    elif category == "Docker Build Error":
        return {
            "root_cause": "The Docker image build failed, possibly due to an incorrect Dockerfile instruction, missing file, or dependency installation issue.",
            "suggested_fix": "Check the Dockerfile step mentioned in the log. Verify file paths, package installation commands, and build context."
        }

    elif category == "YAML Syntax Error":
        return {
            "root_cause": "The pipeline configuration file has a syntax or formatting issue.",
            "suggested_fix": "Validate the YAML file indentation and syntax. Use a YAML validator and check for missing colons, spaces, or incorrect nesting."
        }

    elif category == "Permission Error":
        return {
            "root_cause": "The pipeline does not have enough permission to access a file, folder, command, or deployment resource.",
            "suggested_fix": "Check file permissions, access tokens, service connections, and execution rights for the pipeline user or agent."
        }

    elif category == "Timeout Error":
        return {
            "root_cause": "The pipeline step took too long and exceeded the allowed execution time.",
            "suggested_fix": "Check network calls, deployment health, long-running commands, and timeout settings. Increase timeout only if the operation is expected to take longer."
        }

    elif category == "Deployment Error":
        return {
            "root_cause": "The deployment stage failed while releasing the application to the target environment.",
            "suggested_fix": "Check deployment configuration, environment variables, credentials, target server availability, and previous build artifacts."
        }

    else:
        return {
            "root_cause": "The exact root cause could not be identified from the known error patterns.",
            "suggested_fix": "Review the full log manually and search for detailed error messages near the failed pipeline step."
        }


def generate_report(file_name, error_lines, classification):
    """
    Generate a complete troubleshooting report.

    Parameters:
        file_name (str): Name of the analyzed log file.
        error_lines (list): Extracted important error lines.
        classification (dict): Classification result.

    Returns:
        dict: Complete troubleshooting report.
    """

    primary_category = classification["primary_category"]
    secondary_categories = classification["secondary_categories"]
    all_detected_categories = classification["all_detected_categories"]
    confidence = classification["confidence"]

    explanation = get_root_cause_and_fix(primary_category)

    if secondary_categories:
        secondary_text = ", ".join(secondary_categories)
        final_summary = (
            f"The log analysis detected {primary_category} as the primary failure category. "
            f"Additional related categories were also found: {secondary_text}. "
            f"The confidence level is {confidence}. Review the suggested fix and verify the related pipeline step."
        )
    else:
        final_summary = (
            f"The log analysis detected {primary_category} as the primary failure category. "
            f"The confidence level is {confidence}. Review the suggested fix and verify the related pipeline step."
        )

    report = {
        "file_name": file_name,
        "detected_error_lines": error_lines,
        "failure_category": primary_category,
        "primary_category": primary_category,
        "secondary_categories": secondary_categories,
        "all_detected_categories": all_detected_categories,
        "probable_root_cause": explanation["root_cause"],
        "suggested_fix": explanation["suggested_fix"],
        "confidence_level": confidence,
        "final_summary": final_summary
    }

    return report