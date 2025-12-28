# Installation Guide

Detailed installation instructions for the Data Engineering Copilot.

> **← [Back to README](../README.md)** | **[View All Documentation](../README.md#-documentation)**

## Prerequisites

- Python 3.10 or higher
- Google Cloud SDK installed and authenticated
- Access to a Google Cloud project with Dataform, BigQuery, and Dataproc APIs enabled
- (Optional) GitHub token for GitHub integration
- (Optional) Databricks credentials for Databricks integration

## Step-by-Step Installation

### 1. Install Python Dependencies

#### Option A: Using pip (recommended)

```bash
cd data-engineering-copilot
pip install -r requirements.txt
```

#### Option B: Using pip with pyproject.toml

```bash
cd data-engineering-copilot
pip install -e .
```

This allows you to modify the code and have changes reflected immediately.

### 2. Authenticate with Google Cloud

```bash
# Authenticate with Google Cloud
gcloud auth login --update-adc
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable dataform.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable dataproc.googleapis.com
gcloud services enable aiplatform.googleapis.com  # For Vertex AI
```

### 3. Configure Environment Variables

Create a `.env` file in the `data-engineering-copilot` directory:

```bash
# Google Cloud (Required)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1  # or EU, etc.

# Vertex AI (Required if using Vertex AI models)
GOOGLE_GENAI_USE_VERTEXAI=1

# Model Configuration (Optional, defaults to gemini-2.5-pro)
ROOT_AGENT_MODEL=gemini-2.5-pro

# Dataform (Required)
DATAFORM_REPOSITORY_NAME=your-dataform-repository
DATAFORM_WORKSPACE_NAME=your-workspace

# GitHub (Optional but recommended)
# Create a token at: https://github.com/settings/tokens
# Required scope: repo
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO_PATH=your-org/your-repo
GITHUB_DEFAULT_BRANCH=main

# Databricks (Optional)
# Get token from: https://your-workspace.cloud.databricks.com/#setting/account
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your_databricks_token_here
```

### 4. Verify Installation

Test that everything is working:

```bash
# Check if ADK is installed
adk --version

# List available agents
adk list

# You should see 'data_engineering_copilot' in the list
```

## Installation Methods

### Method 1: Direct Installation (Quick Start)

```bash
git clone https://github.com/david-leadtech/data-engineering-copilot.git
cd data-engineering-copilot
pip install -r requirements.txt
```

### Method 2: Editable Installation (Development)

```bash
git clone https://github.com/david-leadtech/data-engineering-copilot.git
cd data-engineering-copilot
pip install -e .
```

This allows you to modify the code and have changes reflected immediately.

### Method 3: From PyPI (Future)

Once published:
```bash
pip install data-engineering-copilot
```

## Dependencies

The following Python libraries are required:

- `google-adk`: Google's Agent Development Kit framework
- `PyGithub`: To interact with GitHub API
- `google-cloud-dataform`: To work with Dataform pipelines
- `google-cloud-bigquery`: To query and analyze BigQuery
- `google-cloud-dataproc`: To manage Dataproc clusters and PySpark jobs
- `databricks-sdk`: To manage Databricks clusters and jobs
- `dbt-core`: To work with dbt projects
- `python-dotenv`: To load environment variables from `.env` file
- `fastapi`: REST API server framework
- `uvicorn`: ASGI server for FastAPI
- `mcp`: Model Context Protocol SDK

They are automatically installed with `pip install -r requirements.txt` or `pip install -e .`.

## What is the .env file?

The `.env` file is a **local** file (not uploaded to GitHub) where you store your **secrets and configurations**:

- **API Tokens** (GitHub, Google Cloud)
- **Project IDs**
- **Environment-specific configurations**

**Example:**
```bash
# .env (only on your machine, never in GitHub)
GITHUB_TOKEN=ghp_abc123xyz  # Your secret token
GOOGLE_CLOUD_PROJECT=your-project-id
```

## Troubleshooting

### Import Errors

If you get import errors:
```bash
pip install -e .
```

### Authentication Issues

```bash
gcloud auth application-default login
```

### Port Already in Use

If port 8000 is in use:
```bash
export API_PORT=8001
python api_server.py
```

### Missing Dependencies

```bash
pip install -r requirements.txt
```

---

See [QUICK_START.md](../QUICK_START.md) for quick setup guide.

