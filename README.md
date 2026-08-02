# Local AI Agent for CI/CD Log Analysis and Root Cause Recommendation

A local Streamlit-based troubleshooting assistant for analyzing CI/CD-style log files.
The application detects important error lines, classifies the failure type, explains the probable root cause, suggests fixes, inspects related project files for supporting evidence, and generates a downloadable troubleshooting report.

## Project Purpose

This project was created as a portfolio project to demonstrate the connection between:

- CI/CD pipeline troubleshooting
- Python-based log parsing
- Rule-based error classification
- Root cause recommendation
- Context-aware agent design
- Local LLM integration
- Streamlit application development
- Modular project structure

The project uses realistic sample CI/CD logs because no real company pipeline logs are included.

## Important Note

This is a local, rule-based troubleshooting tool with an optional local-LLM assist layer.
It does not use real company logs, paid cloud services, or external AI APIs — the only AI integration is [Ollama](https://ollama.com), which runs entirely on your own machine.

## Features

- Upload `.log` or `.txt` files, use a built-in sample log, or paste log text directly
- Extract important error lines containing keywords such as:
  - ERROR
  - FAILED
  - Exception
  - Traceback
  - Permission denied
  - ModuleNotFoundError
  - SyntaxError
  - Timeout
  - Build failed
  - Deployment failed
- Classify failures into categories:
  - Dependency Error
  - Test Failure
  - Docker Build Error
  - YAML Syntax Error
  - Permission Error
  - Timeout Error
  - Deployment Error
  - Unknown Error
- Detect multiple related failure categories from the same log, identify one primary/root category, and list secondary categories
- Assign a confidence level and a severity level (High, Medium, or Low) based on the primary failure category
- Generate a probable root cause, a rule-based suggested fix, and a final troubleshooting summary
- Inspect optional project context files (`requirements.txt`, `Dockerfile`, GitHub Actions workflow YAML) and produce evidence-based findings tied to the detected failure category
- Generate an AI-assisted root-cause explanation and fix steps using a local Ollama model
- Maintain an analysis history table during the current Streamlit session
- Download the full report as `.txt` or `.csv`

## Technologies Used

- **Programming Language:** Python 3.10+
- **Web App Framework:** Streamlit
- **Data Handling:** Pandas
- **Local AI Integration:** Ollama with qwen2.5:1.5b
- **API Communication:** Requests
- **Log Analysis:** Rule-based parsing and multi-category classification
- **Reporting:** TXT and CSV export
- **Version Control:** Git and GitHub
- **CI Check:** GitHub Actions
- **Environment Management:** Conda

## Getting Started

### Prerequisites

- Python 3.10 or later
- [Ollama](https://ollama.com) (optional, only needed for the local AI recommendation feature)

### Installation

```bash
git clone https://github.com/srinathlaka/ai-log-analyzer-agent.git
cd ai-log-analyzer-agent
pip install -r requirements.txt
```

### (Optional) Enable local AI recommendations

```bash
ollama pull qwen2.5:1.5b
ollama serve
```

The app checks Ollama's status automatically and enables the "Generate Local AI Recommendation" button only when Ollama is running and the model is available.

### Run the app

```bash
streamlit run app.py
```

Then open the URL Streamlit prints in your terminal (typically `http://localhost:8501`).

## Project Structure

```text
ai-log-analyzer-agent/
│
├── app.py
├── requirements.txt
├── README.md
│
├── sample_logs/
│   ├── python_dependency_error.log
│   ├── test_failure.log
│   ├── docker_build_error.log
│   ├── yaml_syntax_error.log
│   ├── permission_error.log
│   └── deployment_timeout.log
│
├── src/
│   ├── log_parser.py
│   ├── error_classifier.py
│   ├── report_generator.py
│   ├── sample_data.py
│   ├── context_inspector.py
│   ├── agent_engine.py
│   └── ai_recommender.py
│
├── screenshots/
│   ├── app_home.png
│   └── analysis_result.png
│
└── .github/
    └── workflows/
        └── test.yml
```

## Screenshots

### App Home
![App Home](screenshots/app_home.png)

### Analysis Result
![Analysis Result](screenshots/analysis_result.png)

## Context-Aware Troubleshooting Agent

The tool can optionally inspect related project context files such as:

- `requirements.txt`
- `Dockerfile`
- GitHub Actions workflow YAML

Based on the detected primary failure category, the local agent chooses which context file to inspect and generates evidence-based findings and recommendations.

Example — if the log contains:

```text
ERROR: ModuleNotFoundError: No module named 'numpy'
```

the primary category is classified as **Dependency Error**, so the agent inspects the uploaded `requirements.txt`:

- If `numpy` is missing from `requirements.txt`, the agent reports it as missing and recommends adding it before rerunning the pipeline.
- If `numpy` is listed, the agent reports that it's present and recommends checking whether the CI/CD pipeline actually installs `requirements.txt` before running the application or tests.
- If no `requirements.txt` was uploaded, the agent reports that dependency evidence couldn't be checked and recommends uploading the file.

## Local AI Recommendation

When Ollama is running locally with the `qwen2.5:1.5b` model available, the app can send the structured analysis result (detected categories, confidence, severity, rule-based root cause and fix) to the model and generate a professional, natural-language explanation plus 3–5 practical fix steps — entirely on your own machine, with no data leaving it.
