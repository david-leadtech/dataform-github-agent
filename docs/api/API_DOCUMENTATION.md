# Data Engineering Copilot - API Documentation

Complete API documentation with examples for curl, Python, and Postman.

> **← [Back to README](../../README.md)** | **[View All Documentation](../../README.md#-documentation)**

## Base URL

**Local Development:**
```
http://localhost:8000
```

**To start the server:**
```bash
cd analytics/adk-agents-reference/data-engineering-copilot
./scripts/start_api_server.sh
# Or: python api_server.py
```

**Verify it's running:**
```bash
curl http://localhost:8000/health
```

**Production:**
```
https://your-api-domain.com
```

## Authentication

Currently, the API runs locally without authentication. For production, add authentication middleware.

---

## 📋 Table of Contents

1. [High-Level Agent Endpoints](#high-level-agent-endpoints)
2. [Direct Tool Execution Endpoints](#direct-tool-execution-endpoints)
3. [Response Codes](#response-codes)
4. [Error Handling](#error-handling)
5. [Examples by Tool Category](#examples-by-tool-category)

---

## High-Level Agent Endpoints

### POST /agent/run

Execute a data engineering task using the AI agent. The agent intelligently decides which tools to use.

**Request:**
```json
{
  "prompt": "Create a new Dataform source for Apple Ads",
  "async_execution": false
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "response": "Created new Dataform source file: definitions/sources/apple_ads.sqlx",
  "error": null,
  "task_id": null,
  "timestamp": "2025-01-28T10:30:00.000Z"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Check the health of the data pipeline",
    "async_execution": false
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/agent/run",
    json={
        "prompt": "Check the health of the data pipeline",
        "async_execution": False
    }
)

print(response.json())
```

**Postman:**
- Method: `POST`
- URL: `http://localhost:8000/agent/run`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "prompt": "Create a new Dataform source for Apple Ads",
  "async_execution": false
}
```

**Async Execution:**
```json
{
  "prompt": "Run the staging pipeline",
  "async_execution": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "response": null,
  "error": null,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-28T10:30:00.000Z"
}
```

### GET /agent/status/{task_id}

Get the status of an async agent task.

**Response (200 OK - Completed):**
```json
{
  "success": true,
  "response": "Pipeline executed successfully. 5 tables created.",
  "error": null,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-28T10:35:00.000Z"
}
```

**Response (200 OK - Running):**
```json
{
  "success": true,
  "response": "Task is running",
  "error": null,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-28T10:32:00.000Z"
}
```

**Response (200 OK - Failed):**
```json
{
  "success": false,
  "response": null,
  "error": "BigQuery error: Table not found",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-28T10:33:00.000Z"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

**cURL:**
```bash
curl http://localhost:8000/agent/status/550e8400-e29b-41d4-a716-446655440000
```

---

## Direct Tool Execution Endpoints

### GET /tools/list

List all available tools organized by category.

**Response (200 OK):**
```json
{
  "dataform": [
    "compile_dataform",
    "read_file_from_dataform",
    "write_file_to_dataform",
    ...
  ],
  "github": [
    "read_file_from_github",
    "create_github_branch",
    ...
  ],
  "bigquery": [...],
  "dbt": [...],
  "dataproc": [...],
  "databricks": [...]
}
```

**cURL:**
```bash
curl http://localhost:8000/tools/list
```

### GET /tools/list/{category}

List all tools in a specific category.

**Response (200 OK):**
```json
[
  "compile_dataform",
  "read_file_from_dataform",
  "write_file_to_dataform",
  "delete_file_from_dataform",
  "search_files_in_dataform",
  "execute_dataform_workflow",
  "execute_dataform_by_tags",
  "get_dataform_execution_logs",
  "get_dataform_repo_link",
  "read_workflow_settings",
  "get_workflow_status",
  "monitor_workflow_health",
  "get_failed_workflows",
  "check_pipeline_health",
  "generate_pipeline_documentation",
  "analyze_assertion_results",
  "check_data_quality_anomalies"
]
```

**Response (404 Not Found):**
```json
{
  "detail": "Category 'invalid' not found. Available categories: ['dataform', 'github', 'bigquery', 'dbt', 'dataproc', 'databricks']"
}
```

**cURL:**
```bash
curl http://localhost:8000/tools/list/dataform
```

### GET /tools/{category}/{tool_name}/info

Get detailed information about a specific tool.

**Response (200 OK):**
```json
{
  "name": "compile_dataform",
  "category": "dataform",
  "description": "Compile the Dataform project and return the dependency graph.",
  "parameters": {
    "project_dir": {
      "type": "str",
      "default": null,
      "required": false
    }
  }
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Tool 'invalid_tool' not found in category 'dataform'"
}
```

**cURL:**
```bash
curl http://localhost:8000/tools/dataform/compile_dataform/info
```

### POST /tools/{category}/{tool_name}

Execute a specific tool directly.

**Request:**
```json
{
  "args": {
    "file_path": "definitions/sources/apple_ads.sqlx"
  }
}
```

**Response (200 OK - Success):**
```json
{
  "success": true,
  "result": {
    "content": "config {\n  type: \"source\",\n  ...\n}",
    "file_path": "definitions/sources/apple_ads.sqlx"
  },
  "error": null,
  "tool_name": "read_file_from_dataform",
  "category": "dataform",
  "timestamp": "2025-01-28T10:30:00.000Z"
}
```

**Response (200 OK - Error):**
```json
{
  "success": false,
  "result": null,
  "error": "File not found: definitions/sources/invalid.sqlx",
  "tool_name": "read_file_from_dataform",
  "category": "dataform",
  "timestamp": "2025-01-28T10:30:00.000Z"
}
```

**Response (404 Not Found - Category):**
```json
{
  "detail": "Category 'invalid' not found. Available: ['dataform', 'github', 'bigquery', 'dbt', 'dataproc', 'databricks']"
}
```

**Response (404 Not Found - Tool):**
```json
{
  "detail": "Tool 'invalid_tool' not found in category 'dataform'. Available tools: ['compile_dataform', 'read_file_from_dataform', ...]"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/tools/dataform/read_file_from_dataform \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "file_path": "definitions/sources/apple_ads.sqlx"
    }
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/tools/dataform/read_file_from_dataform",
    json={
        "args": {
            "file_path": "definitions/sources/apple_ads.sqlx"
        }
    }
)

print(response.json())
```

---

## Response Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| `200 OK` | Success | Request completed successfully |
| `400 Bad Request` | Client Error | Invalid request body or parameters |
| `404 Not Found` | Not Found | Tool/category/task not found |
| `422 Unprocessable Entity` | Validation Error | Request body doesn't match schema |
| `500 Internal Server Error` | Server Error | Unexpected error during execution |

---

## Error Handling

All errors follow this format:

**Error Response:**
```json
{
  "detail": "Error message here"
}
```

Or for tool execution errors:
```json
{
  "success": false,
  "result": null,
  "error": "Detailed error message",
  "tool_name": "tool_name",
  "category": "category"
}
```

**Common Errors:**

1. **Missing Required Parameter:**
```json
{
  "success": false,
  "error": "Invalid arguments: read_file_from_dataform() missing 1 required positional argument: 'file_path'. Check /tools/dataform/read_file_from_dataform/info for required parameters."
}
```

2. **Invalid Tool:**
```json
{
  "detail": "Tool 'invalid' not found in category 'dataform'"
}
```

3. **Tool Execution Error:**
```json
{
  "success": false,
  "error": "BigQuery error: Table 'project.dataset.table' not found"
}
```

---

## Examples by Tool Category

### Dataform Tools

#### Compile Dataform
```bash
curl -X POST http://localhost:8000/tools/dataform/compile_dataform \
  -H "Content-Type: application/json" \
  -d '{"args": {}}'
```

#### Read File
```bash
curl -X POST http://localhost:8000/tools/dataform/read_file_from_dataform \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "file_path": "definitions/sources/apple_ads.sqlx"
    }
  }'
```

#### Execute by Tags
```bash
curl -X POST http://localhost:8000/tools/dataform/execute_dataform_by_tags \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "tags": ["staging", "silver"],
      "compile_only": false
    }
  }'
```

### GitHub Tools

#### Create Branch
```bash
curl -X POST http://localhost:8000/tools/github/create_github_branch \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "branch_name": "feature/new-table",
      "base_branch": "main"
    }
  }'
```

#### Create Pull Request
```bash
curl -X POST http://localhost:8000/tools/github/create_github_pull_request \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "title": "Add new staging table",
      "body": "This PR adds a new staging table for user events",
      "head_branch": "feature/new-table",
      "base_branch": "main"
    }
  }'
```

### BigQuery Tools

#### Analyze Query Performance
```bash
curl -X POST http://localhost:8000/tools/bigquery/analyze_query_performance \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "job_id": "bqjob_abc123"
    }
  }'
```

#### Estimate Query Cost
```bash
curl -X POST http://localhost:8000/tools/bigquery/estimate_query_cost \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "query": "SELECT * FROM \`project.dataset.table\` LIMIT 1000"
    }
  }'
```

### dbt Tools

#### Run dbt Models
```bash
curl -X POST http://localhost:8000/tools/dbt/dbt_run \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "project_dir": "/path/to/dbt/project",
      "select": ["models.staging.*"],
      "full_refresh": false
    }
  }'
```

#### Run dbt Tests
```bash
curl -X POST http://localhost:8000/tools/dbt/dbt_test \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "project_dir": "/path/to/dbt/project",
      "select": ["models.staging.*"]
    }
  }'
```

### Dataproc Tools

#### Submit PySpark Job
```bash
curl -X POST http://localhost:8000/tools/dataproc/submit_pyspark_job \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "project_id": "my-project",
      "region": "us-central1",
      "cluster_name": "my-cluster",
      "main_python_file_uri": "gs://bucket/script.py",
      "args": ["arg1", "arg2"]
    }
  }'
```

### Databricks Tools

#### Submit PySpark Job
```bash
curl -X POST http://localhost:8000/tools/databricks/submit_databricks_pyspark_job \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "job_name": "process-data",
      "python_file": "/Workspace/scripts/process.py",
      "cluster_id": "1234-567890-abcd1234"
    }
  }'
```

---

## Python Client Example

```python
import requests
from typing import Optional, Dict, Any

class DataEngineeringCopilotClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def run_agent(self, prompt: str, async_execution: bool = False) -> Dict[str, Any]:
        """Run the agent with a prompt."""
        response = requests.post(
            f"{self.base_url}/agent/run",
            json={"prompt": prompt, "async_execution": async_execution}
        )
        response.raise_for_status()
        return response.json()
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of an async task."""
        response = requests.get(f"{self.base_url}/agent/status/{task_id}")
        response.raise_for_status()
        return response.json()
    
    def list_tools(self) -> Dict[str, list]:
        """List all available tools."""
        response = requests.get(f"{self.base_url}/tools/list")
        response.raise_for_status()
        return response.json()
    
    def get_tool_info(self, category: str, tool_name: str) -> Dict[str, Any]:
        """Get information about a tool."""
        response = requests.get(
            f"{self.base_url}/tools/{category}/{tool_name}/info"
        )
        response.raise_for_status()
        return response.json()
    
    def execute_tool(
        self, 
        category: str, 
        tool_name: str, 
        args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool directly."""
        response = requests.post(
            f"{self.base_url}/tools/{category}/{tool_name}",
            json={"args": args}
        )
        response.raise_for_status()
        return response.json()


# Usage
client = DataEngineeringCopilotClient()

# Use the agent
result = client.run_agent("Check the health of the data pipeline")
print(result)

# Execute a tool directly
result = client.execute_tool(
    "dataform",
    "read_file_from_dataform",
    {"file_path": "definitions/sources/apple_ads.sqlx"}
)
print(result)
```

---

## Postman Collection

You can import this collection into Postman:

1. **Create a new collection**: "Data Engineering Copilot"
2. **Set base URL variable**: `{{base_url}}` = `http://localhost:8000`
3. **Add requests** for each endpoint above

Or use the interactive API docs at: `http://localhost:8000/docs`

---

## Health Check

### GET /health

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "timestamp": "2025-01-28T10:30:00.000Z"
}
```

**cURL:**
```bash
curl http://localhost:8000/health
```

---

## Interactive API Documentation

FastAPI automatically generates interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive API testing
- Request/response schemas
- Example payloads
- Try it out functionality

