# src/sample_data.py

"""
This file stores information about built-in sample log files.

Main purpose:
- Keep sample log names and file paths in one place
- Make it easier for app.py to load demo logs
"""


SAMPLE_LOGS = {
    "Python Dependency Error": "sample_logs/python_dependency_error.log",
    "Test Failure": "sample_logs/test_failure.log",
    "Docker Build Error": "sample_logs/docker_build_error.log",
    "YAML Syntax Error": "sample_logs/yaml_syntax_error.log",
    "Permission Error": "sample_logs/permission_error.log",
    "Deployment Timeout": "sample_logs/deployment_timeout.log",
}


def get_sample_logs():
    """
    Return the dictionary of available sample logs.

    Returns:
        dict: Sample log display names and file paths.
    """

    return SAMPLE_LOGS