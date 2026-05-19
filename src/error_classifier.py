# src/error_classifier.py

"""
This file classifies CI/CD log errors into simple failure categories.

Main purpose:
- Take extracted error lines
- Check for known error patterns
- Return a failure category and confidence level
"""


def classify_error(error_lines):
    """
    Classify the failure type based on extracted error lines.

    Parameters:
        error_lines (list): List of important error lines from the log file.

    Returns:
        dict: Classification result with category and confidence.
    """

    # Combine all error lines into one text block for easier searching
    error_text = " ".join(error_lines).lower()

    if "modulenotfounderror" in error_text or "no module named" in error_text:
        return {
            "category": "Dependency Error",
            "confidence": "High"
        }

    elif "failed" in error_text and ("test" in error_text or "assert" in error_text):
        return {
            "category": "Test Failure",
            "confidence": "High"
        }

    elif "docker" in error_text or "dockerfile" in error_text:
        return {
            "category": "Docker Build Error",
            "confidence": "Medium"
        }

    elif "yaml" in error_text or "syntaxerror" in error_text:
        return {
            "category": "YAML Syntax Error",
            "confidence": "Medium"
        }

    elif "permission denied" in error_text or "access denied" in error_text:
        return {
            "category": "Permission Error",
            "confidence": "High"
        }

    elif "timeout" in error_text or "timed out" in error_text:
        return {
            "category": "Timeout Error",
            "confidence": "High"
        }

    elif "deployment failed" in error_text:
        return {
            "category": "Deployment Error",
            "confidence": "Medium"
        }

    else:
        return {
            "category": "Unknown Error",
            "confidence": "Low"
        }