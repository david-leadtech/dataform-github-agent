# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk import Agent
from google.adk.tools import agent_tool
from google.adk.tools import VertexAiSearchTool
from google.adk.tools.bigquery import BigQueryCredentialsConfig
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
import google.auth
from .config import config
from .dataform_github_agent.bigquery_tools import (
    get_udf_sp_tool,
    sample_table_data_tool,
    analyze_query_performance,
    get_query_execution_plan,
    estimate_query_cost,
    check_data_freshness,
    analyze_bigquery_error,
    find_failed_bigquery_jobs,
    suggest_query_optimization,
)
from .dataform_github_agent.dataform_tools import (
    compile_dataform,
    delete_file_from_dataform,
    execute_dataform_workflow,
    execute_dataform_by_tags,
    get_dataform_execution_logs,
    get_dataform_repo_link,
    read_file_from_dataform,
    search_files_in_dataform,
    write_file_to_dataform,
    read_workflow_settings,
    get_workflow_status,
    monitor_workflow_health,
    get_failed_workflows,
    check_pipeline_health,
    generate_pipeline_documentation,
    analyze_assertion_results,
    check_data_quality_anomalies,
)
from .dataform_github_agent.gcs_tools import (
    list_bucket_files_tool,
    read_gcs_file_tool,
    validate_bucket_exists_tool,
    validate_file_exists_tool,
)
from .dataform_github_agent.github_tools import (
    read_file_from_github,
    write_file_to_github,
    create_github_branch,
    create_github_pull_request,
    list_github_files,
    get_github_file_history,
    sync_dataform_to_github,
    delete_github_branch,
    get_merged_pull_requests,
    cleanup_merged_branches,
    create_github_repository,
)
from .dataform_github_agent.dbt_tools import (
    dbt_run,
    dbt_test,
    dbt_compile,
    dbt_build,
    dbt_docs_generate,
    dbt_docs_serve,
    dbt_seed,
    dbt_snapshot,
    dbt_ls,
    dbt_show,
    dbt_debug,
    dbt_deps,
    dbt_run_operation,
    dbt_source_freshness,
    dbt_parse,
)
from .dataform_github_agent.dataproc_tools import (
    create_dataproc_cluster,
    list_dataproc_clusters,
    get_dataproc_cluster_details,
    delete_dataproc_cluster,
    submit_pyspark_job,
    check_dataproc_job_status,
    list_dataproc_jobs,
    create_dataproc_serverless_batch,
    check_dataproc_serverless_batch_status,
)
from .dataform_github_agent.databricks_tools import (
    create_databricks_cluster,
    list_databricks_clusters,
    get_databricks_cluster_status,
    delete_databricks_cluster,
    submit_databricks_pyspark_job,
    submit_databricks_notebook_job,
    check_databricks_job_status,
    list_databricks_jobs,
    get_databricks_job_runs,
)

# Define a tool configuration to block any write operations
tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

application_default_credentials, _ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(
    credentials=application_default_credentials
)

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, bigquery_tool_config=tool_config
)

root_agent = Agent(
    model=config.root_agent_model,
    name="data_engineering_agent",
    instruction=f"""
      You are a comprehensive data engineering expert supporting BigQuery, Dataform, dbt, PySpark/Dataproc, and Databricks.

      You can work with multiple data engineering tools:
      - Dataform: Generate SQLX code for BigQuery pipelines
      - dbt: Manage dbt projects, run models, tests, and generate documentation
      - PySpark/Dataproc: Submit PySpark jobs to Dataproc clusters or serverless batches
      - Databricks: Manage Databricks clusters, submit PySpark jobs, and execute notebooks
      - BigQuery: Query, analyze, and optimize BigQuery workloads

      Plan the user task by breaking it into smaller steps.

      - Get an overview of the Dataform pipeline DAG from the compilation result.
      - If needed, sample the tables or resolved SQLX actions from the pipeline DAG.
      - Per user request, make changes to the Dataform files.
      - Compile the pipeline and fix any errors.
      - Validate the resolved queries for the changed nodes and fix any errors.
      - Repeat these steps iteratively until the user task is completed.
      - You can execute workflows by name or by tags (e.g., execute all actions with tags ['pltv', 'staging']).

      Performance & Monitoring:
      - Use analyze_query_performance to analyze BigQuery job performance and identify optimization opportunities.
      - Use get_query_execution_plan to get detailed execution plans and identify bottlenecks.
      - Use estimate_query_cost to estimate query costs before execution.
      - Use check_data_freshness to verify when tables were last updated.
      - Use analyze_bigquery_error to debug failed BigQuery jobs and get fix suggestions.
      - Use find_failed_bigquery_jobs to find and analyze failed jobs by table, error type, or time period.
      - Use suggest_query_optimization to get AI-powered optimization suggestions for queries.
      - Use monitor_workflow_health to track workflow execution health over time.
      - Use get_failed_workflows to identify and troubleshoot failed workflows.
      - Use check_pipeline_health to get overall pipeline health status and recommendations.
      - Use generate_pipeline_documentation to automatically generate comprehensive pipeline documentation.
      - Use analyze_assertion_results to analyze data quality assertion results from workflow executions.
      - Use check_data_quality_anomalies to detect data quality issues and trends.

      dbt Operations:
      - Use dbt_run to execute dbt models (with selectors, tags, or specific models).
      - Use dbt_test to run data quality tests.
      - Use dbt_compile to validate dbt project without executing.
      - Use dbt_build to run models and tests in a single operation.
      - Use dbt_docs_generate to create documentation.
      - Use dbt_seed to load seed data from CSV files.
      - Use dbt_snapshot for SCD Type 2 tracking.
      - Use dbt_ls to list resources in the project.
      - Use dbt_show to preview compiled SQL.
      - Use dbt_debug to troubleshoot connection issues.
      - Use dbt_source_freshness to check when source data was last updated.
      - Use dbt_run_operation to execute custom macros.

      PySpark/Dataproc Operations:
      - Use create_dataproc_cluster to create a new Dataproc cluster for running Spark jobs.
      - Use list_dataproc_clusters to see available clusters.
      - Use submit_pyspark_job to submit PySpark jobs to a cluster (main file must be in GCS).
      - Use check_dataproc_job_status to monitor job execution.
      - Use create_dataproc_serverless_batch for serverless PySpark execution (no cluster management).
      - Use check_dataproc_serverless_batch_status to monitor serverless batch jobs.
      - PySpark files must be uploaded to GCS before submission.

      Databricks Operations:
      - Use create_databricks_cluster to create a new Databricks cluster.
      - Use list_databricks_clusters to see available clusters.
      - Use submit_databricks_pyspark_job to submit PySpark jobs to a cluster (files must be in Databricks workspace or DBFS).
      - Use submit_databricks_notebook_job to execute Databricks notebooks.
      - Use check_databricks_job_status to monitor job execution.
      - Use list_databricks_jobs to list all jobs.
      - Use get_databricks_job_runs to see recent job runs.
      - Databricks requires DATABRICKS_HOST and DATABRICKS_TOKEN environment variables.

      Configuration:
      Default Project ID is {config.project_id} use this project ID for all BigQuery queries unless otherwise specified.

      Dataform
        Source files
        BigQuery Source Tables**: For each BigQuery source table, always add/generate a declarations file. Use the following format for declarations in SQLX files:
        config {{
          type: "declaration",
          database: "PROJECT_ID",
          schema: "DATASET_ID",
          name: "TABLE_NAME",
        }}

      Always verify your changes and ensure they meet the requirements.
      Make reasonable assumptions and do not ask so many questions.
      Compile the pipeline and fix any issues.
      Do not run destructive SQL operations (i.e: drop)

      GitHub Integration:
      - When making changes to Dataform files, you can optionally sync them to GitHub.
      - Use create_github_branch to create a feature branch before making changes.
      - Use write_file_to_github to commit changes directly to GitHub.
      - Use sync_dataform_to_github to keep Dataform and GitHub in sync.
      - Use create_github_pull_request to create a PR for review.
      - After a PR is merged, use delete_github_branch to clean up the feature branch.
      - Use cleanup_merged_branches to automatically delete all merged feature branches.
      - Always use meaningful commit messages that describe what was changed and why.
    """,
    tools=[
        write_file_to_dataform,
        compile_dataform,
        get_dataform_execution_logs,
        search_files_in_dataform,
        read_file_from_dataform,
        delete_file_from_dataform,
        get_dataform_repo_link,
        execute_dataform_workflow,
        execute_dataform_by_tags,
        read_workflow_settings,
        get_workflow_status,
        get_udf_sp_tool,
        bigquery_toolset,
        sample_table_data_tool,
        analyze_query_performance,
        get_query_execution_plan,
        estimate_query_cost,
        check_data_freshness,
        analyze_bigquery_error,
        find_failed_bigquery_jobs,
        suggest_query_optimization,
        validate_bucket_exists_tool,
        validate_file_exists_tool,
        list_bucket_files_tool,
        read_gcs_file_tool,
        read_file_from_github,
        write_file_to_github,
        create_github_branch,
        create_github_pull_request,
        list_github_files,
        get_github_file_history,
        sync_dataform_to_github,
        delete_github_branch,
        get_merged_pull_requests,
        cleanup_merged_branches,
        create_github_repository,
        monitor_workflow_health,
        get_failed_workflows,
        check_pipeline_health,
        generate_pipeline_documentation,
        analyze_assertion_results,
        check_data_quality_anomalies,
        # dbt tools
        dbt_run,
        dbt_test,
        dbt_compile,
        dbt_build,
        dbt_docs_generate,
        dbt_docs_serve,
        dbt_seed,
        dbt_snapshot,
        dbt_ls,
        dbt_show,
        dbt_debug,
        dbt_deps,
        dbt_run_operation,
        dbt_source_freshness,
        dbt_parse,
        # Dataproc/PySpark tools
        create_dataproc_cluster,
        list_dataproc_clusters,
        get_dataproc_cluster_details,
        delete_dataproc_cluster,
        submit_pyspark_job,
        check_dataproc_job_status,
        list_dataproc_jobs,
        create_dataproc_serverless_batch,
        check_dataproc_serverless_batch_status,
        # Databricks tools
        create_databricks_cluster,
        list_databricks_clusters,
        get_databricks_cluster_status,
        delete_databricks_cluster,
        submit_databricks_pyspark_job,
        submit_databricks_notebook_job,
        check_databricks_job_status,
        list_databricks_jobs,
        get_databricks_job_runs,
    ],
)
