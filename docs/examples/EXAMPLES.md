# Usage Examples

Practical examples of using the Data Engineering Copilot for common data engineering tasks.

> **← [Back to README](../../README.md)** | **[View All Documentation](../../README.md#-documentation)**

## Table of Contents

1. [Dataform Examples](#dataform-examples)
2. [dbt Examples](#dbt-examples)
3. [PySpark/Dataproc Examples](#pysparkdataproc-examples)
4. [Databricks Examples](#databricks-examples)
5. [BigQuery Examples](#bigquery-examples)
6. [GitHub Examples](#github-examples)
7. [Monitoring & Debugging Examples](#monitoring--debugging-examples)

---

## Dataform Examples

### Example 1: Create a new Dataform source and make a PR

```
User: "Create a new source for Apple Ads and make a PR"

Agent:
1. Creates branch: feature/add-apple-ads-source
2. Reads existing file from GitHub
3. Creates/modifies file in Dataform
4. Syncs to GitHub with commit
5. Creates PR automatically
```

### Example 2: Execute Dataform pipeline by tags

The agent can execute actions filtered by **any combination of tags from your Dataform project**. Tags are defined in each SQLX file's `config` block and are **project-specific**. Actions must have **ALL** specified tags to be included.

```
User: "Execute all staging tables"

Agent:
1. execute_dataform_by_tags(['staging', 'silver'])
   - Executes only actions with BOTH 'staging' AND 'silver' tags
```

**Tag Filtering Logic:**
- Actions must have **ALL** specified tags to be included (AND logic)
- **Tags are project-specific** - they must exist in your Dataform SQLX files
- Each project defines its own tags in the `config { tags: [...] }` block
- `['staging', 'silver']` → Only actions with both 'staging' AND 'silver' tags
- `['gold']` → All actions with 'gold' tag
- **Any combination of tags from your specific Dataform project files**

### Example 3: Monitor pipeline health

```
User: "Check the health of the data pipeline"

Agent:
1. check_pipeline_health(tags=['staging'])
   - Analyzes recent workflow executions
   - Calculates success rate, average duration
   - Identifies failure patterns
   - Provides recommendations
```

### Example 4: Generate pipeline documentation

```
User: "Generate documentation for the pipeline"

Agent:
1. generate_pipeline_documentation()
   - Parses all SQLX files
   - Extracts dependencies, tags, descriptions
   - Generates markdown with dependency graph
   - Creates comprehensive documentation
```

---

## dbt Examples

### Example 1: Run dbt models and tests

```
User: "Run all staging models in the dbt project and run tests"

Agent:
1. dbt_run(project_dir='./dbt_project', select=['tag:staging'])
   - Executes all models with 'staging' tag
2. dbt_test(project_dir='./dbt_project', select=['tag:staging'])
   - Runs tests for staging models
```

### Example 2: Generate dbt documentation

```
User: "Generate documentation for the dbt project"

Agent:
1. dbt_docs_generate(project_dir='./dbt_project')
   - Generates manifest.json and catalog.json
   - Creates documentation artifacts
```

---

## PySpark/Dataproc Examples

### Example 1: Submit PySpark job to Dataproc

```
User: "Run the PySpark script on Dataproc"

Agent:
1. submit_pyspark_job(
     cluster_name='my-cluster',
     main_python_file_uri='gs://bucket/scripts/process_data.py',
     args=['--input', 'gs://bucket/input/', '--output', 'gs://bucket/output/']
   )
   - Submits PySpark job to cluster
2. check_dataproc_job_status(job_id='...')
   - Monitors job execution
```

### Example 2: Create serverless PySpark batch

```
User: "Run PySpark without managing a cluster"

Agent:
1. create_dataproc_serverless_batch(
     batch_id='process-data-20250101',
     main_python_file_uri='gs://bucket/scripts/process.py'
   )
   - Creates serverless batch (no cluster management)
2. check_dataproc_serverless_batch_status(batch_id='process-data-20250101')
   - Monitors batch execution
```

---

## Databricks Examples

### Example 1: Submit PySpark job to Databricks

```
User: "Run the PySpark script on Databricks"

Agent:
1. submit_databricks_pyspark_job(
     job_name='process-data',
     python_file='/Workspace/scripts/process.py',
     cluster_id='1234-567890-abcd1234'
   )
   - Submits PySpark job to Databricks cluster
2. check_databricks_job_status(run_id='...')
   - Monitors job execution
```

### Example 2: Execute Databricks notebook

```
User: "Run the Databricks notebook"

Agent:
1. submit_databricks_notebook_job(
     job_name='notebook-job',
     notebook_path='/Workspace/notebooks/process',
     cluster_id='1234-567890-abcd1234',
     base_parameters={'input_path': 'dbfs:/data/input', 'output_path': 'dbfs:/data/output'}
   )
   - Executes Databricks notebook with parameters
2. check_databricks_job_status(run_id='...')
   - Monitors execution
```

---

## BigQuery Examples

### Example 1: Analyze query performance

```
User: "Analyze the performance of job abc123"

Agent:
1. analyze_query_performance('abc123')
   - Extracts bytes processed, slot usage, duration
   - Calculates cost estimate
   - Identifies optimization opportunities
   - Suggests improvements
```

### Example 2: Debug BigQuery memory error

```
User: "The data pipeline failed with a memory error, job ID abc123"

Agent:
1. analyze_bigquery_error('abc123')
   - Identifies error type: "memory_exhaustion"
   - Explains root cause: "Query consumed 100% of available memory"
   - Suggests fixes:
     * Break query into smaller stages (use Dataform incremental tables)
     * Add date filters to reduce data volume
     * Optimize JOINs
     * Split complex CTEs into separate materialized tables
2. suggest_query_optimization(query='...', error_message='Resources exceeded...')
   - Provides specific optimization recommendations
   - Categorizes by priority (high/medium/low)
```

### Example 3: Find and analyze failed jobs

```
User: "Find all failed jobs for ltv_dimensions table in the last 7 days"

Agent:
1. find_failed_bigquery_jobs(
     table_name='ltv_dimensions',
     days=7
   )
   - Searches job history for failed jobs
   - Filters by table name and time period
   - Returns job IDs and error details
2. analyze_bigquery_error(job_id='...')
   - Analyzes each failed job
   - Provides fix suggestions
```

---

## GitHub Examples

### Example 1: Create branch and PR

```
User: "Create a branch for new staging table and make a PR"

Agent:
1. create_github_branch('feature/new-staging-table')
2. write_file_to_github(...)
3. create_github_pull_request(...)
```

### Example 2: Clean up merged branches

```
User: "Clean up all merged branches"

Agent:
1. cleanup_merged_branches(dry_run=False)
   - Lists merged PRs
   - Deletes associated branches
   - Returns summary of deleted branches
```

---

## Monitoring & Debugging Examples

### Example 1: Check data freshness

```
User: "Is the staging data fresh?"

Agent:
1. check_data_freshness(
     dataset_id='my_dataset',
     table_id='staging_table',
     stale_threshold_hours=24
   )
   - Checks last update timestamp
   - Compares with threshold
   - Reports if data is stale
```

### Example 2: Monitor workflow health

```
User: "Check workflow health for the last 7 days"

Agent:
1. monitor_workflow_health(days=7)
   - Analyzes workflow execution history
   - Calculates success rates
   - Identifies trends and patterns
   - Provides health score
```

### Example 3: Analyze assertion results

```
User: "Check data quality assertions from last run"

Agent:
1. analyze_assertion_results(workflow_invocation_id='...')
   - Retrieves assertion results
   - Identifies failed assertions
   - Provides data quality report
```

---

## Complete Workflow Examples

### Example: End-to-End Pipeline Development

```
User: "Create a new staging table for user events, test it, and deploy"

Agent:
1. create_github_branch('feature/user-events-staging')
2. write_file_to_dataform('definitions/silver/staging/user_events.sqlx', ...)
3. compile_dataform() - Validates syntax
4. execute_dataform_by_tags(['staging'], compile_only=True) - Dry run
5. sync_dataform_to_github(...)
6. create_github_pull_request(...)
7. (After PR merge) execute_dataform_by_tags(['staging'])
8. check_pipeline_health(tags=['staging'])
```

---

For more examples, see:
- [API Documentation](../api/API_DOCUMENTATION.md) - API usage examples
- [Tools Reference](../reference/TOOLS_REFERENCE.md) - Detailed tool examples

