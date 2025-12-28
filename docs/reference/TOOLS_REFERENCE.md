# Data Engineering Copilot - Tools Reference

Complete reference for all available tools, organized by category.

> **← [Back to README](../../README.md)** | **[View All Documentation](../../README.md#-documentation)**

## 📋 Table of Contents

1. [Dataform Tools](#dataform-tools)
2. [GitHub Tools](#github-tools)
3. [BigQuery Tools](#bigquery-tools)
4. [dbt Tools](#dbt-tools)
5. [Dataproc Tools](#dataproc-tools)
6. [Databricks Tools](#databricks-tools)

---

## Dataform Tools

### `compile_dataform`

Compile the Dataform project and return the dependency graph.

**Parameters:**
- `project_dir` (str, optional): Path to Dataform project directory

**Example:**
```python
result = compile_dataform(project_dir="/path/to/dataform")
```

**API:**
```bash
POST /tools/dataform/compile_dataform
Body: {"args": {"project_dir": "/path/to/dataform"}}
```

---

### `read_file_from_dataform`

Read a file from the Dataform repository.

**Parameters:**
- `file_path` (str, required): Path to file in Dataform repository

**Example:**
```python
content = read_file_from_dataform(file_path="definitions/sources/apple_ads.sqlx")
```

**API:**
```bash
POST /tools/dataform/read_file_from_dataform
Body: {"args": {"file_path": "definitions/sources/apple_ads.sqlx"}}
```

---

### `write_file_to_dataform`

Write content to a file in the Dataform repository.

**Parameters:**
- `file_path` (str, required): Path to file in Dataform repository
- `content` (str, required): File content to write

**Example:**
```python
write_file_to_dataform(
    file_path="definitions/sources/apple_ads.sqlx",
    content="config { type: 'source', ... }"
)
```

**API:**
```bash
POST /tools/dataform/write_file_to_dataform
Body: {
  "args": {
    "file_path": "definitions/sources/apple_ads.sqlx",
    "content": "config { type: 'source', ... }"
  }
}
```

---

### `delete_file_from_dataform`

Delete a file from the Dataform repository.

**Parameters:**
- `file_path` (str, required): Path to file to delete

**Example:**
```python
delete_file_from_dataform(file_path="definitions/sources/old_source.sqlx")
```

---

### `search_files_in_dataform`

Search for files in the Dataform repository.

**Parameters:**
- `query` (str, required): Search query
- `file_type` (str, optional): Filter by file type (e.g., "sqlx")

**Example:**
```python
files = search_files_in_dataform(query="staging", file_type="sqlx")
```

---

### `execute_dataform_workflow`

Execute a Dataform workflow by name.

**Parameters:**
- `workflow_name` (str, required): Name of the workflow to execute

**Example:**
```python
result = execute_dataform_workflow(workflow_name="staging-pipeline-daily")
```

---

### `execute_dataform_by_tags`

Execute Dataform actions filtered by tags.

**Parameters:**
- `tags` (List[str], required): List of tags (actions must have ALL tags)
- `compile_only` (bool, optional): If True, only compile without executing

**Example:**
```python
# Execute all actions with tags ['staging', 'silver']
result = execute_dataform_by_tags(tags=["staging", "silver"])

# Compile only
result = execute_dataform_by_tags(tags=["staging"], compile_only=True)
```

**API:**
```bash
POST /tools/dataform/execute_dataform_by_tags
Body: {
  "args": {
    "tags": ["staging", "silver"],
    "compile_only": false
  }
}
```

---

### `get_dataform_execution_logs`

Get execution logs for a Dataform workflow.

**Parameters:**
- `workflow_invocation_id` (str, required): Workflow invocation ID

**Example:**
```python
logs = get_dataform_execution_logs(workflow_invocation_id="abc123")
```

---

### `read_workflow_settings`

Read Dataform workflow settings.

**Parameters:** None

**Example:**
```python
settings = read_workflow_settings()
```

---

### `get_workflow_status`

Get the status of a Dataform workflow execution.

**Parameters:**
- `workflow_invocation_id` (str, required): Workflow invocation ID

**Example:**
```python
status = get_workflow_status(workflow_invocation_id="abc123")
```

---

### `monitor_workflow_health`

Monitor workflow health over a time period.

**Parameters:**
- `days` (int, optional): Number of days to analyze (default: 7)

**Example:**
```python
health = monitor_workflow_health(days=7)
```

---

### `get_failed_workflows`

Get list of failed workflows.

**Parameters:**
- `days` (int, optional): Number of days to look back (default: 7)

**Example:**
```python
failed = get_failed_workflows(days=7)
```

---

### `check_pipeline_health`

Check the health of a pipeline.

**Parameters:**
- `tags` (List[str], optional): Filter by tags
- `days` (int, optional): Number of days to analyze (default: 7)

**Example:**
```python
health = check_pipeline_health(tags=["staging"], days=7)
```

---

### `generate_pipeline_documentation`

Generate comprehensive pipeline documentation.

**Parameters:** None

**Example:**
```python
docs = generate_pipeline_documentation()
```

---

### `analyze_assertion_results`

Analyze Dataform assertion results.

**Parameters:**
- `workflow_invocation_id` (str, required): Workflow invocation ID

**Example:**
```python
results = analyze_assertion_results(workflow_invocation_id="abc123")
```

---

### `check_data_quality_anomalies`

Check for data quality anomalies in a table.

**Parameters:**
- `table_name` (str, required): Name of the table to check
- `days` (int, optional): Number of days to analyze (default: 30)

**Example:**
```python
anomalies = check_data_quality_anomalies(table_name="ltv_dimensions", days=30)
```

---

## GitHub Tools

### `read_file_from_github`

Read a file from a GitHub repository.

**Parameters:**
- `file_path` (str, required): Path to file in repository
- `branch` (str, optional): Branch name (default: main)

**Example:**
```python
content = read_file_from_github(
    file_path="definitions/sources/apple_ads.sqlx",
    branch="main"
)
```

---

### `write_file_to_github`

Write content to a file in GitHub.

**Parameters:**
- `file_path` (str, required): Path to file
- `content` (str, required): File content
- `commit_message` (str, required): Commit message
- `branch` (str, optional): Branch name (default: main)

**Example:**
```python
write_file_to_github(
    file_path="definitions/sources/apple_ads.sqlx",
    content="config { type: 'source', ... }",
    commit_message="Add Apple Ads source",
    branch="main"
)
```

---

### `create_github_branch`

Create a new branch in GitHub.

**Parameters:**
- `branch_name` (str, required): Name of the new branch
- `base_branch` (str, optional): Base branch (default: main)

**Example:**
```python
create_github_branch(
    branch_name="feature/new-table",
    base_branch="main"
)
```

**API:**
```bash
POST /tools/github/create_github_branch
Body: {
  "args": {
    "branch_name": "feature/new-table",
    "base_branch": "main"
  }
}
```

---

### `create_github_pull_request`

Create a pull request in GitHub.

**Parameters:**
- `title` (str, required): PR title
- `body` (str, required): PR description
- `head_branch` (str, required): Source branch
- `base_branch` (str, optional): Target branch (default: main)

**Example:**
```python
pr = create_github_pull_request(
    title="Add new staging table",
    body="This PR adds a new staging table for user events",
    head_branch="feature/new-table",
    base_branch="main"
)
```

---

### `list_github_files`

List files in a GitHub directory.

**Parameters:**
- `path` (str, required): Directory path
- `branch` (str, optional): Branch name

**Example:**
```python
files = list_github_files(path="definitions/sources", branch="main")
```

---

### `get_github_file_history`

Get commit history for a file.

**Parameters:**
- `file_path` (str, required): Path to file
- `branch` (str, optional): Branch name

**Example:**
```python
history = get_github_file_history(
    file_path="definitions/sources/apple_ads.sqlx",
    branch="main"
)
```

---

### `sync_dataform_to_github`

Sync a Dataform file to GitHub.

**Parameters:**
- `dataform_file_path` (str, required): Path in Dataform
- `github_file_path` (str, required): Path in GitHub
- `commit_message` (str, required): Commit message
- `branch` (str, optional): Branch name

**Example:**
```python
sync_dataform_to_github(
    dataform_file_path="definitions/sources/apple_ads.sqlx",
    github_file_path="definitions/sources/apple_ads.sqlx",
    commit_message="Sync Apple Ads source",
    branch="main"
)
```

---

### `delete_github_branch`

Delete a branch in GitHub.

**Parameters:**
- `branch_name` (str, required): Name of branch to delete

**Example:**
```python
delete_github_branch(branch_name="feature/old-feature")
```

---

### `get_merged_pull_requests`

Get list of merged pull requests.

**Parameters:**
- `base_branch` (str, optional): Base branch (default: main)
- `limit` (int, optional): Maximum number of PRs (default: 10)

**Example:**
```python
prs = get_merged_pull_requests(base_branch="main", limit=10)
```

---

### `cleanup_merged_branches`

Clean up merged branches.

**Parameters:**
- `base_branch` (str, optional): Base branch (default: main)
- `dry_run` (bool, optional): If True, only list branches (default: True)

**Example:**
```python
# Dry run (safe)
result = cleanup_merged_branches(base_branch="main", dry_run=True)

# Actually delete
result = cleanup_merged_branches(base_branch="main", dry_run=False)
```

---

### `create_github_repository`

Create a new GitHub repository.

**Parameters:**
- `owner` (str, required): Repository owner (org or user)
- `repo_name` (str, required): Repository name
- `description` (str, optional): Repository description
- `public` (bool, optional): If True, public repo (default: True)
- `gitignore_template` (str, optional): Gitignore template
- `license_template` (str, optional): License template

**Example:**
```python
repo = create_github_repository(
    owner="david-leadtech",
    repo_name="my-dataform-project",
    description="Dataform project for analytics",
    public=True
)
```

---

## BigQuery Tools

### `analyze_query_performance`

Analyze BigQuery job performance.

**Parameters:**
- `job_id` (str, required): BigQuery job ID

**Example:**
```python
analysis = analyze_query_performance(job_id="bqjob_abc123")
```

**Returns:**
- Bytes processed
- Slot usage
- Duration
- Cost estimate
- Optimization suggestions

---

### `get_query_execution_plan`

Get the execution plan for a query.

**Parameters:**
- `query` (str, required): SQL query

**Example:**
```python
plan = get_query_execution_plan(query="SELECT * FROM `project.dataset.table`")
```

---

### `estimate_query_cost`

Estimate the cost of a query before execution.

**Parameters:**
- `query` (str, required): SQL query

**Example:**
```python
cost = estimate_query_cost(query="SELECT * FROM `project.dataset.table`")
```

---

### `check_data_freshness`

Check when a table was last updated.

**Parameters:**
- `dataset_id` (str, required): Dataset ID
- `table_id` (str, required): Table ID
- `stale_threshold_hours` (int, optional): Hours before considered stale (default: 24)

**Example:**
```python
freshness = check_data_freshness(
    dataset_id="rosseca_apps_data",
    table_id="ltv_dimensions",
    stale_threshold_hours=24
)
```

---

### `analyze_bigquery_error`

Analyze a BigQuery error and provide suggestions.

**Parameters:**
- `job_id` (str, required): Failed job ID

**Example:**
```python
analysis = analyze_bigquery_error(job_id="bqjob_abc123")
```

**Returns:**
- Error type
- Root cause
- Suggested fixes

---

### `find_failed_bigquery_jobs`

Find failed BigQuery jobs.

**Parameters:**
- `table_name` (str, optional): Filter by table name
- `error_type` (str, optional): Filter by error type
- `days` (int, optional): Number of days to look back (default: 7)

**Example:**
```python
failed_jobs = find_failed_bigquery_jobs(
    table_name="ltv_dimensions",
    days=7
)
```

---

### `suggest_query_optimization`

Get optimization suggestions for a query.

**Parameters:**
- `query` (str, required): SQL query
- `error_message` (str, optional): Error message if query failed

**Example:**
```python
suggestions = suggest_query_optimization(
    query="SELECT * FROM `project.dataset.table`",
    error_message="Resources exceeded"
)
```

---

## dbt Tools

### `dbt_run`

Run dbt models.

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `select` (List[str], optional): Select models (e.g., ["models.staging.*"])
- `exclude` (List[str], optional): Exclude models
- `full_refresh` (bool, optional): Full refresh (default: False)

**Example:**
```python
result = dbt_run(
    project_dir="/path/to/dbt",
    select=["models.staging.*"],
    full_refresh=False
)
```

---

### `dbt_test`

Run dbt tests.

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `select` (List[str], optional): Select models
- `exclude` (List[str], optional): Exclude models

**Example:**
```python
result = dbt_test(
    project_dir="/path/to/dbt",
    select=["models.staging.*"]
)
```

---

### `dbt_compile`

Compile dbt project.

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `select` (List[str], optional): Select models
- `exclude` (List[str], optional): Exclude models

**Example:**
```python
result = dbt_compile(project_dir="/path/to/dbt")
```

---

### `dbt_build`

Build dbt models (run + test).

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `select` (List[str], optional): Select models
- `exclude` (List[str], optional): Exclude models
- `full_refresh` (bool, optional): Full refresh

**Example:**
```python
result = dbt_build(project_dir="/path/to/dbt")
```

---

### `dbt_docs_generate`

Generate dbt documentation.

**Parameters:**
- `project_dir` (str, required): Path to dbt project

**Example:**
```python
result = dbt_docs_generate(project_dir="/path/to/dbt")
```

---

### `dbt_docs_serve`

Serve dbt documentation.

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `port` (int, optional): Port number (default: 8080)

**Example:**
```python
dbt_docs_serve(project_dir="/path/to/dbt", port=8080)
```

---

### `dbt_seed`

Run dbt seed.

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `select` (List[str], optional): Select seeds
- `full_refresh` (bool, optional): Full refresh

**Example:**
```python
result = dbt_seed(project_dir="/path/to/dbt")
```

---

### `dbt_snapshot`

Run dbt snapshots.

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `select` (List[str], optional): Select snapshots

**Example:**
```python
result = dbt_snapshot(project_dir="/path/to/dbt")
```

---

### `dbt_ls`

List dbt resources.

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `select` (List[str], optional): Select resources
- `resource_type` (str, optional): Filter by resource type

**Example:**
```python
resources = dbt_ls(project_dir="/path/to/dbt", resource_type="model")
```

---

### `dbt_show`

Show compiled SQL for a model.

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `select` (str, required): Model to show
- `count` (int, optional): Number of rows to show (default: 5)

**Example:**
```python
result = dbt_show(
    project_dir="/path/to/dbt",
    select="models.staging.users"
)
```

---

### `dbt_debug`

Debug dbt project configuration.

**Parameters:**
- `project_dir` (str, required): Path to dbt project

**Example:**
```python
result = dbt_debug(project_dir="/path/to/dbt")
```

---

### `dbt_deps`

Install dbt dependencies.

**Parameters:**
- `project_dir` (str, required): Path to dbt project

**Example:**
```python
result = dbt_deps(project_dir="/path/to/dbt")
```

---

### `dbt_run_operation`

Run a dbt macro.

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `macro_name` (str, required): Macro name
- `args` (Dict[str, Any], optional): Macro arguments

**Example:**
```python
result = dbt_run_operation(
    project_dir="/path/to/dbt",
    macro_name="my_macro",
    args={"param1": "value1"}
)
```

---

### `dbt_source_freshness`

Check source freshness.

**Parameters:**
- `project_dir` (str, required): Path to dbt project
- `select` (List[str], optional): Select sources

**Example:**
```python
result = dbt_source_freshness(project_dir="/path/to/dbt")
```

---

### `dbt_parse`

Parse dbt project.

**Parameters:**
- `project_dir` (str, required): Path to dbt project

**Example:**
```python
result = dbt_parse(project_dir="/path/to/dbt")
```

---

## Dataproc Tools

### `create_dataproc_cluster`

Create a Dataproc cluster.

**Parameters:**
- `project_id` (str, required): GCP project ID
- `region` (str, required): GCP region
- `cluster_name` (str, required): Cluster name
- `config` (Dict[str, Any], required): Cluster configuration

**Example:**
```python
cluster = create_dataproc_cluster(
    project_id="my-project",
    region="us-central1",
    cluster_name="my-cluster",
    config={
        "num_workers": 2,
        "worker_machine_type": "n1-standard-4"
    }
)
```

---

### `list_dataproc_clusters`

List Dataproc clusters.

**Parameters:**
- `project_id` (str, required): GCP project ID
- `region` (str, required): GCP region

**Example:**
```python
clusters = list_dataproc_clusters(
    project_id="my-project",
    region="us-central1"
)
```

---

### `get_dataproc_cluster_details`

Get details of a Dataproc cluster.

**Parameters:**
- `project_id` (str, required): GCP project ID
- `region` (str, required): GCP region
- `cluster_name` (str, required): Cluster name

**Example:**
```python
details = get_dataproc_cluster_details(
    project_id="my-project",
    region="us-central1",
    cluster_name="my-cluster"
)
```

---

### `delete_dataproc_cluster`

Delete a Dataproc cluster.

**Parameters:**
- `project_id` (str, required): GCP project ID
- `region` (str, required): GCP region
- `cluster_name` (str, required): Cluster name

**Example:**
```python
delete_dataproc_cluster(
    project_id="my-project",
    region="us-central1",
    cluster_name="my-cluster"
)
```

---

### `submit_pyspark_job`

Submit a PySpark job to Dataproc.

**Parameters:**
- `project_id` (str, required): GCP project ID
- `region` (str, required): GCP region
- `cluster_name` (str, required): Cluster name
- `main_python_file_uri` (str, required): GCS path to Python file
- `args` (List[str], optional): Job arguments

**Example:**
```python
job = submit_pyspark_job(
    project_id="my-project",
    region="us-central1",
    cluster_name="my-cluster",
    main_python_file_uri="gs://bucket/script.py",
    args=["arg1", "arg2"]
)
```

---

### `check_dataproc_job_status`

Check the status of a Dataproc job.

**Parameters:**
- `project_id` (str, required): GCP project ID
- `region` (str, required): GCP region
- `job_id` (str, required): Job ID

**Example:**
```python
status = check_dataproc_job_status(
    project_id="my-project",
    region="us-central1",
    job_id="job_abc123"
)
```

---

### `list_dataproc_jobs`

List Dataproc jobs.

**Parameters:**
- `project_id` (str, required): GCP project ID
- `region` (str, required): GCP region
- `cluster_name` (str, optional): Filter by cluster
- `job_state` (str, optional): Filter by state

**Example:**
```python
jobs = list_dataproc_jobs(
    project_id="my-project",
    region="us-central1",
    cluster_name="my-cluster"
)
```

---

### `create_dataproc_serverless_batch`

Create a Dataproc Serverless batch.

**Parameters:**
- `project_id` (str, required): GCP project ID
- `region` (str, required): GCP region
- `batch_id` (str, required): Batch ID
- `main_python_file_uri` (str, required): GCS path to Python file
- `args` (List[str], optional): Job arguments
- `service_account` (str, optional): Service account email
- `subnet_uri` (str, optional): Subnet URI

**Example:**
```python
batch = create_dataproc_serverless_batch(
    project_id="my-project",
    region="us-central1",
    batch_id="my-batch",
    main_python_file_uri="gs://bucket/script.py"
)
```

---

### `check_dataproc_serverless_batch_status`

Check the status of a Dataproc Serverless batch.

**Parameters:**
- `project_id` (str, required): GCP project ID
- `region` (str, required): GCP region
- `batch_id` (str, required): Batch ID

**Example:**
```python
status = check_dataproc_serverless_batch_status(
    project_id="my-project",
    region="us-central1",
    batch_id="my-batch"
)
```

---

## Databricks Tools

### `create_databricks_cluster`

Create a Databricks cluster.

**Parameters:**
- `cluster_name` (str, required): Cluster name
- `spark_version` (str, required): Spark version
- `node_type_id` (str, required): Node type ID
- `num_workers` (int, required): Number of worker nodes
- `autotermination_minutes` (int, optional): Auto-termination time (default: 60)
- `region` (str, optional): Databricks region

**Example:**
```python
cluster = create_databricks_cluster(
    cluster_name="my-cluster",
    spark_version="13.3.x-scala2.12",
    node_type_id="i3.xlarge",
    num_workers=2
)
```

---

### `list_databricks_clusters`

List Databricks clusters.

**Parameters:**
- `region` (str, optional): Databricks region
- `include_terminated` (bool, optional): Include terminated clusters (default: False)

**Example:**
```python
clusters = list_databricks_clusters(include_terminated=False)
```

---

### `get_databricks_cluster_status`

Get the status of a Databricks cluster.

**Parameters:**
- `cluster_id` (str, required): Cluster ID
- `region` (str, optional): Databricks region

**Example:**
```python
status = get_databricks_cluster_status(cluster_id="1234-567890-abcd1234")
```

---

### `delete_databricks_cluster`

Delete a Databricks cluster.

**Parameters:**
- `cluster_id` (str, required): Cluster ID
- `region` (str, optional): Databricks region

**Example:**
```python
delete_databricks_cluster(cluster_id="1234-567890-abcd1234")
```

---

### `submit_databricks_pyspark_job`

Submit a PySpark job to Databricks.

**Parameters:**
- `job_name` (str, required): Job name
- `python_file` (str, required): Path to Python file
- `cluster_id` (str, optional): Existing cluster ID
- `new_cluster_config` (Dict[str, Any], optional): New cluster configuration
- `libraries` (List[Dict[str, Any]], optional): Libraries to install
- `parameters` (List[str], optional): Job parameters
- `timeout_seconds` (int, optional): Timeout in seconds (default: 3600)
- `region` (str, optional): Databricks region

**Example:**
```python
job = submit_databricks_pyspark_job(
    job_name="process-data",
    python_file="/Workspace/scripts/process.py",
    cluster_id="1234-567890-abcd1234"
)
```

---

### `submit_databricks_notebook_job`

Submit a Databricks notebook job.

**Parameters:**
- `job_name` (str, required): Job name
- `notebook_path` (str, required): Path to notebook
- `cluster_id` (str, optional): Existing cluster ID
- `new_cluster_config` (Dict[str, Any], optional): New cluster configuration
- `base_parameters` (Dict[str, Any], optional): Notebook parameters
- `timeout_seconds` (int, optional): Timeout in seconds (default: 3600)
- `region` (str, optional): Databricks region

**Example:**
```python
job = submit_databricks_notebook_job(
    job_name="notebook-job",
    notebook_path="/Workspace/notebooks/process",
    cluster_id="1234-567890-abcd1234",
    base_parameters={"input_path": "dbfs:/data/input"}
)
```

---

### `check_databricks_job_status`

Check the status of a Databricks job.

**Parameters:**
- `run_id` (int, required): Job run ID
- `region` (str, optional): Databricks region

**Example:**
```python
status = check_databricks_job_status(run_id=12345)
```

---

### `list_databricks_jobs`

List Databricks jobs.

**Parameters:**
- `region` (str, optional): Databricks region

**Example:**
```python
jobs = list_databricks_jobs()
```

---

### `get_databricks_job_runs`

Get runs for a Databricks job.

**Parameters:**
- `job_id` (int, optional): Job ID (if None, returns all runs)
- `region` (str, optional): Databricks region
- `limit` (int, optional): Maximum number of runs (default: 10)

**Example:**
```python
runs = get_databricks_job_runs(job_id=123, limit=10)
```

---

## Quick Reference

### Total Tools: 65

- **Dataform**: 16 tools
- **GitHub**: 11 tools
- **BigQuery**: 6 tools
- **dbt**: 14 tools
- **Dataproc**: 9 tools
- **Databricks**: 9 tools

### API Endpoints

- `GET /tools/list` - List all tools
- `GET /tools/list/{category}` - List tools by category
- `GET /tools/{category}/{tool_name}/info` - Get tool info
- `POST /tools/{category}/{tool_name}` - Execute tool

### Interactive Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

