# Changelog

All notable changes to the Data Engineering Copilot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-01-28

### Added
- **REST API Server** (`api_server.py`)
  - FastAPI-based REST API with full tool access
  - 65+ tools organized by category (dataform, github, bigquery, dbt, dataproc, databricks)
  - High-level agent endpoint (`/agent/run`) for intelligent task execution
  - Direct tool execution endpoints (`/tools/{category}/{tool_name}`)
  - Async task execution support
  - Interactive API documentation (Swagger UI and ReDoc)
  - Health check and status endpoints
  - Complete request/response documentation

- **MCP Server** (`mcp_server.py`)
  - Model Context Protocol server for Cursor integration
  - Direct integration with Cursor's AI
  - Natural language interface via `run_agent_task` tool
  - Async execution support

- **Comprehensive Documentation**
  - `API_DOCUMENTATION.md`: Complete API reference with curl, Python, and Postman examples
  - `MCP_DOCUMENTATION.md`: Full MCP setup guide with troubleshooting
  - `TOOLS_REFERENCE.md`: Detailed reference for all 65 tools with parameters and examples
  - `QUICK_START.md`: Step-by-step server startup guide
  - `PLTV_CAPABILITIES_ANALYSIS.md`: Analysis of copilot capabilities for PLTV pipeline
  - `PLTV_MIGRATION_GUIDE.md`: Guide for using copilot with PLTV pipeline

- **Startup Scripts**
  - `scripts/start_api_server.sh`: Start REST API server
  - `scripts/start_mcp_server.sh`: Start MCP server with setup instructions
  - `scripts/update_remote_after_rename.sh`: Update git remote after repository rename

### Changed
- Updated README.md to feature REST API server as first option
- Enhanced CURSOR_INTEGRATION.md with MCP and API details
- Updated all repository name references from `dataform-github-agent` to `data-engineering-copilot`
- Improved documentation structure and cross-references

### Dependencies
- Added `fastapi>=0.104.0` for REST API server
- Added `uvicorn[standard]>=0.24.0` for ASGI server
- Added `mcp>=0.9.0` for MCP server support

## [1.1.0] - 2025-01-28

### Changed
- **Project renamed**: Dataform GitHub Agent → Data Engineering Copilot (better reflects multi-platform capabilities)

### Added
- **Databricks Integration (9 tools)**
  - `create_databricks_cluster`: Create a new Databricks cluster with configurable workers, node types, and Spark version
  - `list_databricks_clusters`: List all clusters (with option to include/exclude terminated clusters)
  - `get_databricks_cluster_status`: Get detailed cluster status, configuration, and runtime information
  - `delete_databricks_cluster`: Delete a cluster
  - `submit_databricks_pyspark_job`: Submit PySpark job to a cluster (files must be in Databricks workspace or DBFS)
  - `submit_databricks_notebook_job`: Execute a Databricks notebook as a job with parameter support
  - `check_databricks_job_status`: Check job run status, execution duration, and result state
  - `list_databricks_jobs`: List all jobs in the workspace
  - `get_databricks_job_runs`: Get recent job runs (optionally filtered by job ID)
  - Full support for Databricks workspace paths (`/Workspace/...`) and DBFS paths (`dbfs:/...`)
  - Automatic cluster management with auto-termination support
  - Library dependency management for PySpark jobs

### Changed (continued)
- Updated total tool count from 62 to 71 tools
- Added Databricks configuration variables (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`) to `config.py`
- Updated agent instructions to include Databricks operations and best practices
- Enhanced README with Databricks examples and configuration instructions

### Dependencies
- Added `databricks-sdk>=0.20.0` to `requirements.txt`

## [1.0.0] - 2024-12-26

### Added
- Initial release of Data Engineering Copilot (formerly Dataform GitHub Agent)

#### Complete Tool Inventory (62 tools)

##### Dataform Integration (15 tools)

| Tool | Description |
|------|-------------|
| `read_file_from_dataform` | Read files from Dataform workspace |
| `write_file_to_dataform` | Write/modify SQLX files in Dataform workspace |
| `compile_dataform` | Compile pipeline and view DAG structure |
| `get_dataform_execution_logs` | Get execution logs from workflow runs |
| `search_files_in_dataform` | Search files in Dataform workspace |
| `delete_file_from_dataform` | Delete files from Dataform workspace |
| `get_dataform_repo_link` | Get repository link for Dataform workspace |
| `execute_dataform_workflow` | Execute workflow by name |
| `execute_dataform_by_tags` | Execute actions filtered by tags (AND logic) |
| `read_workflow_settings` | Read workflow configuration and settings |
| `get_workflow_status` | Check workflow execution status and details |
| `monitor_workflow_health` | Monitor workflow execution health over time (success rate, duration, trends) |
| `get_failed_workflows` | Get list of failed workflows with error details |
| `check_pipeline_health` | Check overall pipeline health status and get recommendations |
| `generate_pipeline_documentation` | Automatically generate comprehensive pipeline documentation |
| `analyze_assertion_results` | Analyze data quality assertion results from workflow executions |
| `check_data_quality_anomalies` | Detect data quality issues and trends over time |

##### dbt Integration (14 tools)

| Tool | Description |
|------|-------------|
| `dbt_run` | Execute dbt models (with selectors, tags, or specific models) |
| `dbt_test` | Run data quality tests on dbt models |
| `dbt_compile` | Compile dbt project without executing (validation) |
| `dbt_build` | Run models and tests in a single operation |
| `dbt_docs_generate` | Generate dbt documentation (manifest.json, catalog.json) |
| `dbt_docs_serve` | Serve dbt documentation locally on a web server |
| `dbt_seed` | Load seed data from CSV files into the warehouse |
| `dbt_snapshot` | Run snapshots for SCD Type 2 tracking |
| `dbt_ls` | List dbt resources (models, tests, seeds, etc.) |
| `dbt_show` | Preview compiled SQL without executing |
| `dbt_debug` | Debug dbt project and profile configuration |
| `dbt_deps` | Install dbt package dependencies |
| `dbt_run_operation` | Execute custom dbt macros |
| `dbt_source_freshness` | Check when source data was last updated |
| `dbt_parse` | Parse and validate dbt project syntax |

##### PySpark/Dataproc Integration (9 tools)

| Tool | Description |
|------|-------------|
| `create_dataproc_cluster` | Create a new Dataproc cluster with configurable settings |
| `list_dataproc_clusters` | List all clusters in a region |
| `get_dataproc_cluster_details` | Get detailed cluster information (status, config, nodes) |
| `delete_dataproc_cluster` | Delete a Dataproc cluster |
| `submit_pyspark_job` | Submit PySpark job to a cluster (file must be in GCS) |
| `check_dataproc_job_status` | Check job execution status and details |
| `list_dataproc_jobs` | List jobs (optionally filtered by type or cluster) |
| `create_dataproc_serverless_batch` | Create serverless PySpark batch (no cluster management needed) |
| `check_dataproc_serverless_batch_status` | Check serverless batch execution status |

##### BigQuery Tools (9 tools)

| Tool | Description |
|------|-------------|
| `sample_table_data_tool` | View sample data from BigQuery tables |
| `bigquery_toolset` | SQL queries via ADK BigQuery toolset (read/write operations) |
| `analyze_query_performance` | Analyze BigQuery job performance metrics (bytes, slots, cost, duration) |
| `get_query_execution_plan` | Get detailed query execution plan with bottleneck identification |
| `estimate_query_cost` | Estimate query cost before execution using dry-run |
| `check_data_freshness` | Check when tables were last updated and detect stale data |
| `analyze_bigquery_error` | **AI-powered error analysis** - Analyze failed BigQuery jobs and get fix suggestions |
| `find_failed_bigquery_jobs` | Find failed jobs by table, error type, or time period |
| `suggest_query_optimization` | **AI-powered optimization** - Get specific optimization suggestions based on query structure |

##### GitHub Integration (11 tools)

| Tool | Description |
|------|-------------|
| `read_file_from_github` | Read files from GitHub repository |
| `write_file_to_github` | Write files to GitHub with commit message |
| `create_github_branch` | Create new branches in GitHub repository |
| `create_github_pull_request` | Create pull requests for code review |
| `create_github_repository` | Create new GitHub repositories |
| `delete_github_branch` | Delete branches (useful after merging PRs) |
| `get_merged_pull_requests` | List merged pull requests |
| `cleanup_merged_branches` | Automatically clean up merged feature branches |
| `sync_dataform_to_github` | Sync Dataform workspace files to GitHub |
| `list_github_files` | List files in GitHub repository directories |
| `get_github_file_history` | View commit history for specific files |

##### GCS Tools (4 tools)

| Tool | Description |
|------|-------------|
| `list_bucket_files_tool` | List files in GCS bucket |
| `read_gcs_file_tool` | Read files from GCS bucket |
| `validate_bucket_exists_tool` | Check if GCS bucket exists |
| `validate_file_exists_tool` | Check if file exists in GCS bucket |

**Total: 62 tools across 6 platforms** (Dataform, dbt, Dataproc, BigQuery, GitHub, GCS)

[1.1.0]: https://github.com/david-leadtech/data-engineering-copilot/releases/tag/v1.1.0
[1.0.0]: https://github.com/david-leadtech/data-engineering-copilot/releases/tag/v1.0.0

