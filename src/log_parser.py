# src/log_parser.py

"""
This file contains functions for reading and parsing CI/CD log files.

Main purpose:
- Take raw log text
- Search for important error keywords
- Return only the important error lines
"""


ERROR_KEYWORDS = [
    "ERROR",
    "FAILED",
    "Exception",
    "Traceback",
    "Permission denied",
    "ModuleNotFoundError",
    "SyntaxError",
    "Timeout",
    "Build failed",
    "Deployment failed",
]


def extract_error_lines(log_text):
    """
    Extract important error-related lines from the given log text.

    Parameters:
        log_text (str): Complete content of a log file.

    Returns:
        list: A list of lines that contain important error keywords.
    """

    error_lines = []

    # Split the full log text into individual lines
    lines = log_text.splitlines()

    # Check each line one by one
    for line in lines:
        for keyword in ERROR_KEYWORDS:
            if keyword.lower() in line.lower():
                error_lines.append(line.strip())
                break

    return error_lines