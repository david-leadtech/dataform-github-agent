# 🤖 Data Engineering Copilot

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/david-leadtech/data-engineering-copilot/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

**AI-powered data engineering copilot** that helps you build and manage data pipelines across multiple platforms.

## 📑 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
  - [Getting Started](#getting-started)
  - [Usage](#usage)
  - [Integration](#integration)
  - [Reference](#reference)
- [Usage Methods](#-usage-methods)
- [Available Tools](#%EF%B8%8F-available-tools)
- [Examples](#-examples)
- [API Features](#-api-features)
- [Releases](#-releases)
- [Installation](#-installation-methods)
- [External Resources](#-external-resources)

## ✨ Features

- ✅ **Dataform**: Create, modify, compile, and execute Dataform SQLX pipelines
- ✅ **dbt**: Full dbt project management (run, test, compile, docs, seed, snapshot, etc.)
- ✅ **PySpark/Dataproc**: Submit and manage PySpark jobs on Google Cloud Dataproc
- ✅ **Databricks**: Manage Databricks clusters, submit PySpark jobs, and execute notebooks
- ✅ **BigQuery**: Query, analyze, and optimize BigQuery workloads
- ✅ **GitHub**: Full GitHub integration (branches, PRs, file sync, branch cleanup)
- ✅ **REST API**: FastAPI server with Swagger UI, ReDoc, and OpenAPI schema
- ✅ **MCP Server**: Direct Cursor IDE integration via Model Context Protocol

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd data-engineering-copilot
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
DATAFORM_REPOSITORY_NAME=your-repo
DATAFORM_WORKSPACE_NAME=your-workspace
GOOGLE_GENAI_USE_VERTEXAI=1

# Optional
GITHUB_TOKEN=ghp_your_token
GITHUB_REPO_PATH=your-org/your-repo
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your_token
```

### 3. Authenticate

```bash
gcloud auth application-default login
```

### 4. Start the API Server

```bash
./scripts/start_api_server.sh
```

**Access:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## 📖 Documentation

> **💡 Tip:** All documentation files are linked below. Click any link to jump directly to that guide.

### Getting Started
- 📘 **[Quick Start Guide](QUICK_START.md)** → Step-by-step server setup in 5 minutes
- 📘 **[Installation Guide](docs/INSTALLATION.md)** → Detailed installation instructions with troubleshooting

### Usage
- 📘 **[Usage Examples](docs/examples/EXAMPLES.md)** → Practical examples for Dataform, dbt, PySpark, BigQuery, GitHub
- 📘 **[API Documentation](docs/api/API_DOCUMENTATION.md)** → Complete REST API reference with curl, Python, and Postman examples
- 📘 **[Tools Reference](docs/reference/TOOLS_REFERENCE.md)** → Detailed reference for all 65 tools organized by category
- 📘 **[Capabilities & Limitations](docs/reference/CAPABILITIES.md)** → What the copilot can and cannot do

### Integration
- 📘 **[Cursor Integration](docs/integration/CURSOR_INTEGRATION.md)** → Use the copilot in Cursor IDE (all methods: MCP, API, direct)
- 📘 **[MCP Documentation](docs/mcp/MCP_DOCUMENTATION.md)** → Complete MCP server setup guide for Cursor

### Reference
- 📘 **[Releases](docs/reference/RELEASES.md)** → Release management and semantic versioning
- 📘 **[Changelog](docs/reference/CHANGELOG.md)** → Version history and changes

## 🎯 Usage Methods

### 1. REST API (Recommended for Teams)

```bash
# Start server
./scripts/start_api_server.sh

# Use the API
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Check the health of the data pipeline"}'
```

**Features:**
- ✅ FastAPI with automatic OpenAPI schema generation
- ✅ Swagger UI for interactive testing (`/docs`)
- ✅ ReDoc for beautiful documentation (`/redoc`)
- ✅ 65+ tools organized by category
- ✅ Async task execution support

### 2. MCP Server (For Cursor)

Configure in Cursor settings and use directly:

```
Use the data engineering copilot to create a new Dataform source
```

See [MCP Documentation](docs/mcp/MCP_DOCUMENTATION.md) for setup.

### 3. Direct Python

```python
from data_engineering_copilot.agent import root_agent

response = root_agent.run("Create a new Dataform source")
print(response)
```

### 4. ADK Web Interface

```bash
adk web
```

## 🛠️ Available Tools

**65 tools** organized across 6 platforms:

- **Dataform** (16): File operations, compilation, execution, monitoring
- **GitHub** (11): Branches, PRs, file sync, repository management
- **BigQuery** (6): Performance analysis, cost estimation, error analysis
- **dbt** (14): Model execution, testing, documentation, freshness
- **Dataproc** (9): Cluster management, PySpark jobs, serverless batches
- **Databricks** (9): Cluster management, PySpark jobs, notebooks

See [Tools Reference](docs/reference/TOOLS_REFERENCE.md) for complete reference.

## 📚 Examples

See [Usage Examples](docs/examples/EXAMPLES.md) for practical examples:
- Creating Dataform sources and PRs
- Executing pipelines by tags
- Running dbt models and tests
- Submitting PySpark jobs
- Monitoring pipeline health
- Debugging BigQuery errors

## 🔧 API Features

### FastAPI Integration

The REST API server includes:

- ✅ **FastAPI**: Modern, fast web framework
- ✅ **Swagger UI**: Interactive API testing at `/docs`
- ✅ **ReDoc**: Beautiful documentation at `/redoc`
- ✅ **OpenAPI Schema**: Auto-generated at `/openapi.json`
- ✅ **Type Validation**: Automatic request/response validation
- ✅ **Async Support**: Async task execution
- ✅ **CORS**: Enabled for local development

### API Endpoints

- `POST /agent/run` - High-level agent execution
- `GET /tools/list` - List all tools by category
- `POST /tools/{category}/{tool_name}` - Execute specific tool
- `GET /tools/{category}/{tool_name}/info` - Get tool information
- `GET /health` - Health check

See [API Documentation](docs/api/API_DOCUMENTATION.md) for complete reference.

## 🚀 Releases

**Current Version:** `1.2.0`

**Latest Release:** [v1.2.0](https://github.com/david-leadtech/data-engineering-copilot/releases/tag/v1.2.0)

This project uses [Semantic Versioning](https://semver.org/). See [Releases](docs/reference/RELEASES.md) for release management.

## 📦 Installation Methods

### Quick Install

```bash
git clone https://github.com/david-leadtech/data-engineering-copilot.git
cd data-engineering-copilot
pip install -r requirements.txt
```

### Development Install

```bash
pip install -e .
```

## 🔗 External Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [Dataform Documentation](https://cloud.google.com/dataform/docs)
- [dbt Documentation](https://docs.getdbt.com/)
- [Dataproc Documentation](https://cloud.google.com/dataproc/docs)
- [Databricks Documentation](https://docs.databricks.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE) file for details.

---

**Need Help?** Check the [documentation](#-documentation) or open an issue on GitHub.
