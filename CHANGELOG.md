# Changelog

All notable changes to the Dataform GitHub Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-28

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

### Changed
- Updated total tool count from 62 to 71 tools
- Added Databricks configuration variables (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`) to `config.py`
- Updated agent instructions to include Databricks operations and best practices
- Enhanced README with Databricks examples and configuration instructions

### Dependencies
- Added `databricks-sdk>=0.20.0` to `requirements.txt`

## [1.0.0] - 2024-12-26

### Added
- Initial release of Dataform GitHub Agent

- **Dataform Integration (15 tools)**
  - `read_file_from_dataform`: Read files from Dataform workspace
  - `write_file_to_dataform`: Write/modify SQLX files
  - `compile_dataform`: Compile pipeline and view DAG
  - `get_dataform_execution_logs`: Get execution logs
  - `search_files_in_dataform`: Search files in workspace
  - `delete_file_from_dataform`: Delete files from workspace
  - `get_dataform_repo_link`: Get repository link
  - `execute_dataform_workflow`: Execute workflow by name
  - `execute_dataform_by_tags`: Execute actions filtered by tags
  - `read_workflow_settings`: Read workflow configuration
  - `get_workflow_status`: Check workflow execution status
  - `monitor_workflow_health`: Monitor workflow execution health over time
  - `get_failed_workflows`: Get list of failed workflows with error details
  - `check_pipeline_health`: Check overall pipeline health status
  - `generate_pipeline_documentation`: Automatically generate comprehensive pipeline documentation
  - `analyze_assertion_results`: Analyze data quality assertion results
  - `check_data_quality_anomalies`: Detect data quality issues and trends

- **dbt Integration (14 tools)**
  - `dbt_run`: Execute dbt models (with selectors, tags, or specific models)
  - `dbt_test`: Run data quality tests
  - `dbt_compile`: Compile dbt project without executing (validation)
  - `dbt_build`: Run models and tests in a single operation
  - `dbt_docs_generate`: Generate dbt documentation (manifest.json, catalog.json)
  - `dbt_docs_serve`: Serve dbt documentation locally
  - `dbt_seed`: Load seed data from CSV files
  - `dbt_snapshot`: Run snapshots for SCD Type 2 tracking
  - `dbt_ls`: List dbt resources (models, tests, seeds, etc.)
  - `dbt_show`: Preview compiled SQL without executing
  - `dbt_debug`: Debug dbt project and profile configuration
  - `dbt_deps`: Install dbt package dependencies
  - `dbt_run_operation`: Execute custom dbt macros
  - `dbt_source_freshness`: Check when source data was last updated
  - `dbt_parse`: Parse and validate dbt project syntax

- **PySpark/Dataproc Integration (9 tools)**
  - `create_dataproc_cluster`: Create a new Dataproc cluster
  - `list_dataproc_clusters`: List all clusters in a region
  - `get_dataproc_cluster_details`: Get detailed cluster information
  - `delete_dataproc_cluster`: Delete a cluster
  - `submit_pyspark_job`: Submit PySpark job to a cluster (file must be in GCS)
  - `check_dataproc_job_status`: Check job execution status
  - `list_dataproc_jobs`: List jobs (optionally filtered by type or cluster)
  - `create_dataproc_serverless_batch`: Create serverless PySpark batch (no cluster needed)
  - `check_dataproc_serverless_batch_status`: Check serverless batch status

- **BigQuery Tools (9 tools)**
  - `sample_table_data_tool`: View table data
  - `bigquery_toolset`: SQL queries (via ADK BigQuery toolset)
  - `analyze_query_performance`: Analyze BigQuery job performance metrics (bytes, slots, cost, duration)
  - `get_query_execution_plan`: Get detailed query execution plan with bottleneck identification
  - `estimate_query_cost`: Estimate query cost before execution using dry-run
  - `check_data_freshness`: Check when tables were last updated and detect stale data
  - `analyze_bigquery_error`: AI-powered error analysis - Analyze failed BigQuery jobs and get fix suggestions
  - `find_failed_bigquery_jobs`: Find failed jobs by table, error type, or time period
  - `suggest_query_optimization`: AI-powered optimization - Get specific optimization suggestions

- **GitHub Integration (11 tools)**
  - `read_file_from_github`: Read files from GitHub
  - `write_file_to_github`: Write files with commit
  - `create_github_branch`: Create branches
  - `create_github_pull_request`: Create PRs
  - `create_github_repository`: Create new GitHub repositories
  - `delete_github_branch`: Delete branches (useful after merging PRs)
  - `get_merged_pull_requests`: List merged PRs
  - `cleanup_merged_branches`: Automatically clean up merged branches
  - `sync_dataform_to_github`: Sync Dataform → GitHub
  - `list_github_files`: List files in directories
  - `get_github_file_history`: View commit history for files

- **GCS Tools (4 tools)**
  - `list_bucket_files_tool`: List files in GCS bucket
  - `read_gcs_file_tool`: Read files from GCS
  - `validate_bucket_exists_tool`: Check if bucket exists
  - `validate_file_exists_tool`: Check if file exists in bucket

### Total: 62 tools across all platforms

[1.1.0]: https://github.com/david-leadtech/dataform-github-agent/releases/tag/v1.1.0
[1.0.0]: https://github.com/david-leadtech/dataform-github-agent/releases/tag/v1.0.0

