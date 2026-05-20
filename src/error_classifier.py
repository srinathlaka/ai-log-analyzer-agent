# src/error_classifier.py

"""
This file classifies CI/CD log errors into failure categories.

Main purpose:
- Take extracted error lines
- Check for known error patterns
- Detect multiple possible categories
- Select one primary failure category
- Return primary category, secondary categories, and confidence level
"""


def classify_error(error_lines):
    """
    Classify the failure type based on extracted error lines.

    Parameters:
        error_lines (list): List of important error lines from the log file.

    Returns:
        dict: Classification result with primary category,
              secondary categories, all detected categories,
              and confidence level.
    """

    # Combine all error lines into one lowercase text block
    error_text = " ".join(error_lines).lower()

    detected_categories = []

    # Check dependency-related errors
    if "modulenotfounderror" in error_text or "no module named" in error_text:
        detected_categories.append("Dependency Error")

    # Check test-related errors
    if "failed" in error_text and ("test" in error_text or "assert" in error_text):
        detected_categories.append("Test Failure")

    # Check Docker-related errors
    if "docker" in error_text or "dockerfile" in error_text:
        detected_categories.append("Docker Build Error")

    # Check YAML-related errors
    if "yaml" in error_text or "syntaxerror" in error_text:
        detected_categories.append("YAML Syntax Error")

    # Check permission-related errors
    if "permission denied" in error_text or "access denied" in error_text:
        detected_categories.append("Permission Error")

    # Check timeout-related errors
    if "timeout" in error_text or "timed out" in error_text:
        detected_categories.append("Timeout Error")

    # Check deployment-related errors
    if "deployment failed" in error_text:
        detected_categories.append("Deployment Error")

    # If nothing matched, return Unknown Error
    if not detected_categories:
        return {
            "category": "Unknown Error",
            "primary_category": "Unknown Error",
            "secondary_categories": [],
            "all_detected_categories": ["Unknown Error"],
            "confidence": "Low"
        }

    # Priority order decides the primary/root category
    priority_order = [
        "Dependency Error",
        "YAML Syntax Error",
        "Docker Build Error",
        "Permission Error",
        "Timeout Error",
        "Test Failure",
        "Deployment Error",
    ]

    primary_category = "Unknown Error"

    for category in priority_order:
        if category in detected_categories:
            primary_category = category
            break

    secondary_categories = []

    for category in detected_categories:
        if category != primary_category:
            secondary_categories.append(category)

    # Confidence logic
    if len(detected_categories) == 1:
        confidence = "High"
    elif len(detected_categories) == 2:
        confidence = "Medium"
    else:
        confidence = "Medium"

    return {
        "category": primary_category,
        "primary_category": primary_category,
        "secondary_categories": secondary_categories,
        "all_detected_categories": detected_categories,
        "confidence": confidence
    }