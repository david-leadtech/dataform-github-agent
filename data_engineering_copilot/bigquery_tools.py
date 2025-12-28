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

"""This module provides a set of tools for interacting with Google BigQuery.

It includes functionalities for checking dataset and table existence, retrieving
table schemas and data previews, validating dataset and table names, querying
information schema, finding relevant datasets, and validating data within tables
based on user-defined rules.
"""

import json
from typing import Any, Dict, List, Optional
from google.cloud import bigquery
from google.adk.tools import agent_tool
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

def get_bigquery_client() -> bigquery.Client:
  """Get a configured BigQuery client."""
  return bigquery.Client(project=config.project_id)

def bigquery_job_details_tool(job_id: str) -> Dict[str, Any]:
  """Retrieve details of a BigQuery job.

  Args:
      job_id (str): The ID of the BigQuery job.

  Returns:
      Dict[str, Any]: Job details including query and error information.
  """
  client = get_bigquery_client()
  try:
    job = client.get_job(job_id)
    query = job.query if isinstance(job, bigquery.QueryJob) else "N/A"
    errors = job.error_result

    return {
        "query": query,
        "status": job.state,
        "error": errors["message"] if errors else None,
        "created": job.created.isoformat(),
        "started": job.started.isoformat() if job.started else None,
        "ended": job.ended.isoformat() if job.ended else None,
    }
  except Exception as e:
    return {"error": f"Error getting job details: {e}"}

def get_udf_sp_tool(dataset_id: str, routine_type: Optional[str] = None) -> str:
  """Retrieve UDFs and Stored Procedures from a BigQuery dataset.

  Args:
      dataset_id (str): The dataset ID to search.
      routine_type (Optional[str]): Filter by routine type ('FUNCTION' or
        'PROCEDURE').

  Returns:
      str: JSON string containing routine information.
  """
  client = get_bigquery_client()

  query = f"""
        SELECT 
            routine_name,
            routine_type,
            routine_body,
            specific_name,
            ddl,
            routine_definition,
            created,
            last_modified
        FROM `{config.project_id}.{dataset_id}.INFORMATION_SCHEMA.ROUTINES`
        {f"WHERE routine_type = '{routine_type}'" if routine_type else ""}
        ORDER BY routine_type, routine_name
    """

  try:
    query_job = client.query(query)
    results = query_job.result()
    routine_info_list = [dict(row.items()) for row in results]

    if not routine_info_list:
      return json.dumps(
          {
              "message": (
                  f"No {'UDFs' if routine_type == 'FUNCTION' else 'Stored Procedures' if routine_type == 'PROCEDURE' else 'routines'} found"
                  f" in dataset '{dataset_id}'."
              )
          },
          indent=2,
      )

    return json.dumps(routine_info_list, indent=2, default=str)

  except Exception as e:
    return json.dumps(
        {
            "error": (
                f"Error retrieving routines from dataset '{dataset_id}': {e}"
            )
        },
        indent=2,
    )


def validate_table_data(
    dataset_id: str, table_id: str, rules: List[Dict[str, Any]]
) -> Dict[str, Any]:
  """Validate data in a BigQuery table against specified rules.

  Args:
      dataset_id (str): The dataset ID.
      table_id (str): The table ID.
      rules (List[Dict[str, Any]]): List of validation rules.

  Returns:
      Dict[str, Any]: Validation results.
  """
  client = get_bigquery_client()
  validation_results = []

  for rule in rules:
    try:
      column = rule["column"]
      rule_type = rule["type"]
      value = rule.get("value")

      if rule_type == "not_null":
        query = f"""
                    SELECT COUNT(*) as null_count
                    FROM `{config.project_id}.{dataset_id}.{table_id}`
                    WHERE {column} IS NULL
                """
      elif rule_type == "unique":
        query = f"""
                    SELECT {column}, COUNT(*) as count
                    FROM `{config.project_id}.{dataset_id}.{table_id}`
                    GROUP BY {column}
                    HAVING COUNT(*) > 1
                """
      elif rule_type == "value":
        query = f"""
                    SELECT COUNT(*) as invalid_count
                    FROM `{config.project_id}.{dataset_id}.{table_id}`
                    WHERE {column} != {value}
                """
      else:
        validation_results.append({
            "rule": rule,
            "status": "error",
            "message": f"Unknown rule type: {rule_type}",
        })
        continue

      query_job = client.query(query)
      results = query_job.result()
      row = next(iter(results))

      validation_results.append({
          "rule": rule,
          "status": "pass" if row[0] == 0 else "fail",
          "details": dict(row.items()),
      })

    except Exception as e:
      validation_results.append(
          {"rule": rule, "status": "error", "message": str(e)}
      )

  return {
      "dataset": dataset_id,
      "table": table_id,
      "validations": validation_results,
  }


def sample_table_data_tool(
    dataset_id: str,
    table_id: str,
    sample_size: int = 10,
    random_seed: Optional[int] = None,
) -> str:
  """Sample data from a BigQuery table using RAND() function.

  Args:
      dataset_id (str): The dataset ID.
      table_id (str): The table ID.
      sample_size (int): Number of rows to sample. Defaults to 10.
      random_seed (Optional[int]): Seed for random sampling. If provided,
        ensures reproducible results.

  Returns:
      str: JSON string containing sampled data.
  """
  try:
    client = get_bigquery_client()

    # Build the query with optional random seed
    seed_clause = (
        f"SET @seed = {random_seed};" if random_seed is not None else ""
    )
    query = f"""
            {seed_clause}
            SELECT *
            FROM `{config.project_id}.{dataset_id}.{table_id}`
            ORDER BY {'RAND(@seed)' if random_seed is not None else 'RAND()'}
            LIMIT {sample_size}
        """

    query_job = client.query(query)
    results = query_job.result()

    # Convert results to list of dictionaries
    sample_data = [dict(row.items()) for row in results]

    return json.dumps(
        {
            "status": "success",
            "dataset": dataset_id,
            "table": table_id,
            "sample_size": sample_size,
            "random_seed": random_seed,
            "data": sample_data,
        },
        indent=2,
        default=str,
    )

  except Exception as e:
    return json.dumps({"status": "error", "error": str(e)}, indent=2)


@agent_tool
def analyze_query_performance(job_id: str) -> Dict[str, Any]:
  """Analyze BigQuery job performance metrics.

  Args:
      job_id (str): The BigQuery job ID to analyze (format: project:location.job_id or just job_id).

  Returns:
      Dict[str, Any]: Performance metrics including bytes processed, slot usage, duration,
      cost estimate, and optimization suggestions.
  """
  client = get_bigquery_client()
  try:
    # Handle different job_id formats
    if ':' in job_id and '.' in job_id:
      # Full format: project:location.job_id
      job = client.get_job(job_id)
    else:
      # Just job_id, need to construct full path
      job = client.get_job(job_id, location=config.location)

    if not isinstance(job, bigquery.QueryJob):
      return {
          "status": "error",
          "error_message": f"Job {job_id} is not a query job",
      }

    # Extract performance metrics
    total_bytes = job.total_bytes_processed or 0
    total_slot_ms = job.total_slot_ms or 0
    creation_time = job.created
    start_time = job.started
    end_time = job.ended

    # Calculate duration
    duration_seconds = None
    if start_time and end_time:
      duration_seconds = (end_time - start_time).total_seconds()

    # Calculate cost (on-demand pricing: $5 per TB)
    cost_usd = (total_bytes / (1024 ** 4)) * 5.0  # Convert bytes to TB, then multiply by $5

    # Calculate slot efficiency
    slot_minutes = total_slot_ms / (1000 * 60) if total_slot_ms else 0
    slot_efficiency = None
    if duration_seconds and slot_minutes:
      # Average slots used = total_slot_ms / (duration_ms)
      avg_slots = total_slot_ms / (duration_seconds * 1000) if duration_seconds > 0 else 0
      slot_efficiency = {
          "avg_slots_used": round(avg_slots, 2),
          "total_slot_minutes": round(slot_minutes, 2),
      }

    # Get error information if any
    error_info = None
    if job.error_result:
      error_info = {
          "message": job.error_result.get("message"),
          "reason": job.error_result.get("reason"),
          "location": job.error_result.get("location"),
      }

    # Generate optimization suggestions
    suggestions = []
    if total_bytes > 100 * (1024 ** 3):  # > 100 GB
      suggestions.append("Consider using partitioned tables to reduce bytes scanned")
    if total_slot_ms > 3600000:  # > 1 hour of slot time
      suggestions.append("Query may benefit from optimization - high slot usage detected")
    if error_info and "memory" in error_info.get("message", "").lower():
      suggestions.append("Memory error detected - consider breaking query into smaller stages")
    if duration_seconds and duration_seconds > 300:  # > 5 minutes
      suggestions.append("Long-running query - consider optimizing JOINs or aggregations")

    return {
        "status": "success",
        "job_id": job_id,
        "state": job.state,
        "performance_metrics": {
            "total_bytes_processed": total_bytes,
            "total_bytes_processed_tb": round(total_bytes / (1024 ** 4), 4),
            "total_slot_ms": total_slot_ms,
            "duration_seconds": round(duration_seconds, 2) if duration_seconds else None,
            "creation_time": creation_time.isoformat() if creation_time else None,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
        },
        "cost_estimate": {
            "estimated_cost_usd": round(cost_usd, 4),
            "bytes_processed_tb": round(total_bytes / (1024 ** 4), 4),
            "pricing_model": "on-demand ($5 per TB)",
        },
        "slot_efficiency": slot_efficiency,
        "error": error_info,
        "optimization_suggestions": suggestions,
    }

  except Exception as e:
    return {
        "status": "error",
        "error_message": f"Error analyzing query performance: {e}",
    }


@agent_tool
def get_query_execution_plan(job_id: str) -> Dict[str, Any]:
  """Get detailed execution plan from a BigQuery job.

  Args:
      job_id (str): The BigQuery job ID (format: project:location.job_id or just job_id).

  Returns:
      Dict[str, Any]: Detailed execution plan including stages, operations, shuffle info,
      and bottleneck identification.
  """
  client = get_bigquery_client()
  try:
    # Handle different job_id formats
    if ':' in job_id and '.' in job_id:
      job = client.get_job(job_id)
    else:
      job = client.get_job(job_id, location=config.location)

    if not isinstance(job, bigquery.QueryJob):
      return {
          "status": "error",
          "error_message": f"Job {job_id} is not a query job",
      }

    # Get query plan
    query_plan = job.query_plan
    if not query_plan:
      return {
          "status": "error",
          "error_message": "Query plan not available for this job",
      }

    # Extract stage information
    stages = []
    bottlenecks = []
    total_slot_ms = 0
    max_shuffle_output = 0

    for stage in query_plan:
      stage_info = {
          "name": stage.name,
          "id": stage.id,
          "steps": len(stage.steps) if stage.steps else 0,
          "input_stages": stage.input_stages if stage.input_stages else [],
          "parallel_inputs": stage.parallel_inputs if hasattr(stage, 'parallel_inputs') else None,
          "completed_parallel_inputs": stage.completed_parallel_inputs if hasattr(stage, 'completed_parallel_inputs') else None,
      }

      # Extract step details
      step_details = []
      if stage.steps:
        for step in stage.steps:
          step_info = {
              "kind": step.kind if hasattr(step, 'kind') else "unknown",
          }
          if hasattr(step, 'substeps') and step.substeps:
            step_info["substeps"] = [str(sub) for sub in step.substeps]
          step_details.append(step_info)
          stage_info["steps_detail"] = step_details

      # Check for shuffle operations (potential bottlenecks)
      if stage_info.get("parallel_inputs", 0) > 10:
        bottlenecks.append({
            "stage": stage.name,
            "issue": "High parallel inputs - may cause shuffle overhead",
            "parallel_inputs": stage_info["parallel_inputs"],
        })

      # Track shuffle output
      if hasattr(stage, 'shuffle_output_bytes') and stage.shuffle_output_bytes:
        shuffle_bytes = stage.shuffle_output_bytes
        if shuffle_bytes > max_shuffle_output:
          max_shuffle_output = shuffle_bytes
          bottlenecks.append({
              "stage": stage.name,
              "issue": "Large shuffle output detected",
              "shuffle_output_bytes": shuffle_bytes,
          })

      stages.append(stage_info)

    # Calculate total slot time
    if hasattr(job, 'total_slot_ms'):
      total_slot_ms = job.total_slot_ms or 0

    # Identify optimization opportunities
    optimization_opportunities = []
    if max_shuffle_output > 10 * (1024 ** 3):  # > 10 GB shuffle
      optimization_opportunities.append("Large shuffle detected - consider optimizing JOINs or aggregations")
    if len(stages) > 20:
      optimization_opportunities.append("Many stages detected - query may benefit from simplification")

    return {
        "status": "success",
        "job_id": job_id,
        "execution_plan": {
            "total_stages": len(stages),
            "stages": stages,
            "total_slot_ms": total_slot_ms,
        },
        "bottlenecks": bottlenecks if bottlenecks else None,
        "optimization_opportunities": optimization_opportunities if optimization_opportunities else None,
    }

  except Exception as e:
    return {
        "status": "error",
        "error_message": f"Error getting execution plan: {e}",
    }


@agent_tool
def estimate_query_cost(query: str, dry_run: bool = True) -> Dict[str, Any]:
  """Estimate BigQuery query cost before execution.

  Args:
      query (str): The SQL query to estimate cost for.
      dry_run (bool): If True, only estimate without executing (default: True).

  Returns:
      Dict[str, Any]: Cost estimate, bytes that would be processed, and optimization suggestions.
  """
  client = get_bigquery_client()
  try:
    # Create a query job config with dry_run enabled
    job_config = bigquery.QueryJobConfig(dry_run=dry_run, use_query_cache=False)

    # Create the query job
    query_job = client.query(query, job_config=job_config)

    # Get statistics from dry run
    total_bytes = query_job.total_bytes_processed or 0
    total_bytes_tb = total_bytes / (1024 ** 4)

    # Calculate cost (on-demand pricing: $5 per TB)
    estimated_cost_usd = total_bytes_tb * 5.0

    # Generate optimization suggestions
    suggestions = []
    if total_bytes > 100 * (1024 ** 3):  # > 100 GB
      suggestions.append("Large query detected - consider using partitioned/clustered tables")
      suggestions.append("Add WHERE clauses to filter data before processing")
    if total_bytes > 1000 * (1024 ** 3):  # > 1 TB
      suggestions.append("Very large query - consider incremental processing or data sampling")
    if "SELECT *" in query.upper():
      suggestions.append("Avoid SELECT * - specify only needed columns to reduce bytes scanned")

    # Check for common optimization opportunities
    query_upper = query.upper()
    if "JOIN" in query_upper and query_upper.count("JOIN") > 5:
      suggestions.append("Multiple JOINs detected - ensure proper indexing and filtering")
    if "GROUP BY" in query_upper and "ORDER BY" in query_upper:
      suggestions.append("Consider using window functions instead of GROUP BY + ORDER BY for better performance")

    return {
        "status": "success",
        "dry_run": dry_run,
        "cost_estimate": {
            "estimated_cost_usd": round(estimated_cost_usd, 4),
            "bytes_to_process": total_bytes,
            "bytes_to_process_tb": round(total_bytes_tb, 4),
            "pricing_model": "on-demand ($5 per TB)",
        },
        "optimization_suggestions": suggestions,
        "note": "This is an estimate. Actual cost may vary based on query execution and caching.",
    }

  except Exception as e:
    return {
        "status": "error",
        "error_message": f"Error estimating query cost: {e}",
    }


@agent_tool
def analyze_bigquery_error(
    job_id: str,
    include_suggestions: bool = True,
) -> Dict[str, Any]:
  """Analyze a failed BigQuery job and provide debugging insights and fix suggestions.

  This tool is specifically designed for troubleshooting complex pipeline failures,
  like memory errors, timeout issues, and other BigQuery execution problems.

  Args:
      job_id (str): The BigQuery job ID to analyze (format: project:location.job_id or just job_id).
      include_suggestions (bool): Whether to include AI-powered fix suggestions (default: True).

  Returns:
      Dict[str, Any]: Error analysis including error type, root cause, and suggested fixes.
  """
  client = get_bigquery_client()
  try:
    # Handle different job_id formats
    if ':' in job_id and '.' in job_id:
      job = client.get_job(job_id)
    else:
      job = client.get_job(job_id, location=config.location)

    if not job.error_result:
      return {
          "status": "error",
          "error_message": f"Job {job_id} did not fail or has no error information",
      }

    error_result = job.error_result
    error_message = error_result.get("message", "")
    error_reason = error_result.get("reason", "")
    error_location = error_result.get("location", "")

    # Extract performance metrics if available
    total_bytes = job.total_bytes_processed or 0
    total_slot_ms = job.total_slot_ms or 0
    duration_seconds = None
    if job.started and job.ended:
      duration_seconds = (job.ended - job.started).total_seconds()

    # Classify error type
    error_type = "unknown"
    root_cause = None
    suggestions = []

    # Memory errors
    if "Resources exceeded" in error_message or "memory" in error_message.lower() or "100% of limit" in error_message:
      error_type = "memory_exhaustion"
      root_cause = "Query consumed 100% of available memory. Common causes: large JOINs, complex aggregations, window functions, or processing too much data at once."
      suggestions = [
          "Break the query into smaller stages (use Dataform incremental tables)",
          "Add date filters to reduce data volume (e.g., last 3 days instead of full history)",
          "Optimize JOINs: ensure proper indexes, use smaller tables first",
          "Consider using incremental processing instead of full refresh",
          "Review query execution plan to identify memory-intensive operations",
          "Split complex CTEs into separate materialized tables",
      ]

    # Timeout errors
    elif "timeout" in error_message.lower() or "deadline" in error_message.lower():
      error_type = "timeout"
      root_cause = "Query exceeded maximum execution time."
      suggestions = [
          "Break query into smaller chunks",
          "Add more aggressive filters to reduce data volume",
          "Use incremental processing",
          "Consider using scheduled queries with longer timeout",
      ]

    # Permission errors
    elif "Access Denied" in error_message or "permission" in error_message.lower():
      error_type = "permission_error"
      root_cause = "Insufficient permissions to access resources."
      suggestions = [
          "Check IAM permissions for the service account",
          "Verify dataset and table access permissions",
          "Ensure the service account has BigQuery Data Editor role",
      ]

    # Table not found
    elif "Not found" in error_message or "does not exist" in error_message.lower():
      error_type = "table_not_found"
      root_cause = "Referenced table or dataset does not exist."
      suggestions = [
          "Verify table name and dataset are correct",
          "Check if table exists: SELECT * FROM `project.dataset.table` LIMIT 1",
          "Ensure table was created before this query runs",
          "Check for typos in table names",
      ]

    # Syntax errors
    elif "Syntax error" in error_message or "Invalid" in error_message:
      error_type = "syntax_error"
      root_cause = "SQL syntax error in the query."
      suggestions = [
          f"Check SQL syntax at location: {error_location}",
          "Review the query for missing commas, parentheses, or quotes",
          "Validate SQL using BigQuery's query validator",
      ]

    # Slot exhaustion
    elif "slot" in error_message.lower() and ("exceeded" in error_message.lower() or "unavailable" in error_message.lower()):
      error_type = "slot_exhaustion"
      root_cause = "Insufficient BigQuery slots available."
      suggestions = [
          "Wait for other queries to complete",
          "Use reservation with more slots",
          "Optimize query to use fewer slots",
          "Schedule query during off-peak hours",
      ]

    # Generic error - provide general suggestions
    else:
      error_type = "other_error"
      root_cause = "Unknown error type. Review error message for details."
      suggestions = [
          "Review the full error message for specific details",
          "Check BigQuery job logs in Cloud Logging",
          "Verify query syntax and table references",
          "Check if related tables have recent data",
      ]

    # Get query preview if available
    query_preview = None
    if isinstance(job, bigquery.QueryJob) and job.query:
      query_preview = job.query[:500]  # First 500 chars

    # Build response
    result = {
        "status": "success",
        "job_id": job_id,
        "error_analysis": {
            "error_type": error_type,
            "error_reason": error_reason,
            "error_message": error_message,
            "error_location": error_location,
            "root_cause": root_cause,
        },
        "job_metrics": {
            "total_bytes_processed": total_bytes,
            "total_bytes_processed_tb": round(total_bytes / (1024 ** 4), 4),
            "total_slot_ms": total_slot_ms,
            "duration_seconds": round(duration_seconds, 2) if duration_seconds else None,
            "job_state": job.state,
        },
        "query_preview": query_preview,
    }

    if include_suggestions and suggestions:
      result["suggested_fixes"] = suggestions
      result["next_steps"] = [
          "Review the error analysis above",
          "Apply the most relevant suggested fix",
          "Test the fix with a small data sample first",
          "Monitor the next execution to verify the fix worked",
      ]

    return result

  except Exception as e:
    return {
        "status": "error",
        "error_message": f"Error analyzing BigQuery error: {e}",
    }


@agent_tool
def find_failed_bigquery_jobs(
    table_name: Optional[str] = None,
    error_type: Optional[str] = None,
    days: int = 7,
    limit: int = 20,
) -> Dict[str, Any]:
  """Find failed BigQuery jobs matching specific criteria.

  Useful for troubleshooting pipeline failures and identifying patterns.

  Args:
      table_name (Optional[str]): Filter by table name (e.g., 'ltv_dimensions_e2e_calculation_looker').
      error_type (Optional[str]): Filter by error type ('memory', 'timeout', 'permission', etc.).
      days (int): Number of days to look back (default: 7).
      limit (int): Maximum number of jobs to return (default: 20).

  Returns:
      Dict[str, Any]: List of failed jobs with error details.
  """
  client = get_bigquery_client()
  try:
    from datetime import datetime, timedelta

    time_threshold = datetime.utcnow() - timedelta(days=days)

    # Build query to find failed jobs
    query = f"""
    SELECT
        job_id,
        creation_time,
        state,
        job_type,
        error_result.message as error_message,
        error_result.reason as error_reason,
        error_result.location as error_location,
        total_bytes_processed,
        total_slot_ms,
        TIMESTAMP_DIFF(end_time, start_time, MINUTE) as duration_minutes,
        destination_table.table_id as destination_table,
        destination_table.dataset_id as destination_dataset,
        LEFT(query, 500) as query_preview
    FROM `{config.project_id}.region-{config.location}.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
    WHERE state = 'DONE'
      AND error_result IS NOT NULL
      AND creation_time >= TIMESTAMP('{time_threshold.strftime("%Y-%m-%d %H:%M:%S")}')
    """

    # Add filters
    conditions = []
    if table_name:
      conditions.append(f"(destination_table.table_id LIKE '%{table_name}%' OR query LIKE '%{table_name}%')")

    if error_type:
      error_patterns = {
          "memory": "error_result.message LIKE '%Resources exceeded%' OR error_result.message LIKE '%memory%'",
          "timeout": "error_result.message LIKE '%timeout%' OR error_result.message LIKE '%deadline%'",
          "permission": "error_result.message LIKE '%Access Denied%' OR error_result.message LIKE '%permission%'",
          "not_found": "error_result.message LIKE '%Not found%' OR error_result.message LIKE '%does not exist%'",
      }
      if error_type.lower() in error_patterns:
        conditions.append(f"({error_patterns[error_type.lower()]})")

    if conditions:
      query += " AND " + " AND ".join(conditions)

    query += f" ORDER BY creation_time DESC LIMIT {limit}"

    query_job = client.query(query)
    results = query_job.result()

    failed_jobs = []
    for row in results:
      job_info = {
          "job_id": row.job_id,
          "creation_time": row.creation_time.isoformat() if row.creation_time else None,
          "state": row.state,
          "job_type": row.job_type,
          "error_message": row.error_message,
          "error_reason": row.error_reason,
          "error_location": row.error_location,
          "destination_table": f"{row.destination_dataset}.{row.destination_table}" if row.destination_table else None,
          "duration_minutes": row.duration_minutes,
          "total_bytes_processed": row.total_bytes_processed,
          "query_preview": row.query_preview,
      }
      failed_jobs.append(job_info)

    return {
        "status": "success",
        "failed_jobs": failed_jobs,
        "count": len(failed_jobs),
        "filters": {
            "table_name": table_name,
            "error_type": error_type,
            "days": days,
        },
    }

  except Exception as e:
    return {
        "status": "error",
        "error_message": f"Error finding failed jobs: {e}",
        "failed_jobs": [],
    }


@agent_tool
def suggest_query_optimization(
    query: str,
    error_message: Optional[str] = None,
) -> Dict[str, Any]:
  """Analyze a BigQuery query and suggest optimizations based on the query structure and optional error context.

  Uses AI-powered analysis to provide specific optimization recommendations.

  Args:
      query (str): The SQL query to analyze.
      error_message (Optional[str]): Optional error message from a failed execution to provide context-aware suggestions.

  Returns:
      Dict[str, Any]: Optimization suggestions categorized by type and priority.
  """
  try:
    # First, do a dry run to get query metrics
    client = get_bigquery_client()
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    query_job = client.query(query, job_config=job_config)

    total_bytes = query_job.total_bytes_processed or 0
    total_bytes_tb = total_bytes / (1024 ** 4)

    # Analyze query structure
    query_upper = query.upper()
    suggestions = []
    high_priority = []
    medium_priority = []
    low_priority = []

    # Check for common issues
    if "SELECT *" in query_upper:
      high_priority.append({
          "issue": "SELECT * usage",
          "impact": "High - scans all columns unnecessarily",
          "suggestion": "Specify only needed columns to reduce bytes scanned",
      })

    # Check for missing WHERE clauses on large tables
    if total_bytes_tb > 0.1:  # > 100 GB
      if "WHERE" not in query_upper or ("WHERE" in query_upper and "DATE(" not in query_upper and "TIMESTAMP(" not in query_upper):
        high_priority.append({
            "issue": "Large data scan without date filters",
            "impact": "High - processing too much data",
            "suggestion": "Add date filters to limit data volume (e.g., WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY))",
        })

    # Check for complex JOINs
    join_count = query_upper.count("JOIN")
    if join_count > 5:
      high_priority.append({
          "issue": f"Multiple JOINs ({join_count} JOINs detected)",
          "impact": "High - complex JOINs can cause memory issues",
          "suggestion": "Consider breaking into multiple stages with materialized intermediate tables",
      })

    # Check for window functions
    if "OVER (" in query_upper or "ROW_NUMBER()" in query_upper or "RANK()" in query_upper:
      medium_priority.append({
          "issue": "Window functions detected",
          "impact": "Medium - window functions can be memory-intensive",
          "suggestion": "Ensure window functions are properly partitioned. Consider materializing intermediate results.",
      })

    # Check for GROUP BY with many columns
    if "GROUP BY" in query_upper:
      group_by_match = query_upper.find("GROUP BY")
      if group_by_match != -1:
        group_by_section = query_upper[group_by_match:group_by_match + 200]
        if group_by_section.count(",") > 5:
          medium_priority.append({
              "issue": "GROUP BY with many columns",
              "impact": "Medium - high cardinality can increase memory usage",
              "suggestion": "Review if all GROUP BY columns are necessary. Consider pre-aggregating some dimensions.",
          })

    # Error-specific suggestions
    if error_message:
      if "Resources exceeded" in error_message or "memory" in error_message.lower():
        high_priority.append({
            "issue": "Memory error detected",
            "impact": "Critical - query failed due to memory",
            "suggestion": "Break query into smaller stages. Use Dataform incremental tables to materialize intermediate results.",
        })

    # Build response
    all_suggestions = high_priority + medium_priority + low_priority

    return {
        "status": "success",
        "query_analysis": {
            "estimated_bytes_tb": round(total_bytes_tb, 4),
            "estimated_cost_usd": round(total_bytes_tb * 5.0, 4),
            "join_count": join_count,
            "has_window_functions": "OVER (" in query_upper or "ROW_NUMBER()" in query_upper,
            "has_group_by": "GROUP BY" in query_upper,
        },
        "optimization_suggestions": {
            "high_priority": high_priority if high_priority else None,
            "medium_priority": medium_priority if medium_priority else None,
            "low_priority": low_priority if low_priority else None,
        },
        "total_suggestions": len(all_suggestions),
        "error_context": error_message if error_message else None,
    }

  except Exception as e:
    return {
        "status": "error",
        "error_message": f"Error analyzing query: {e}",
    }


@agent_tool
def check_data_freshness(dataset_id: str, table_id: str, freshness_threshold_hours: Optional[int] = 24) -> Dict[str, Any]:
  """Check data freshness for a BigQuery table.

  Args:
      dataset_id (str): The dataset ID.
      table_id (str): The table ID.
      freshness_threshold_hours (Optional[int]): Expected freshness threshold in hours (default: 24).

  Returns:
      Dict[str, Any]: Freshness status, last update time, and alerts if data is stale.
  """
  client = get_bigquery_client()
  try:
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)

    # Get last modified time
    last_modified = table.modified
    if not last_modified:
      return {
          "status": "error",
          "error_message": f"Could not determine last modified time for {dataset_id}.{table_id}",
      }

    # Calculate time since last update
    now = datetime.utcnow()
    if isinstance(last_modified, datetime):
      time_since_update = now - last_modified
    else:
      # Handle timestamp format
      time_since_update = now - last_modified

    hours_since_update = time_since_update.total_seconds() / 3600
    days_since_update = hours_since_update / 24

    # Determine freshness status
    is_fresh = hours_since_update <= freshness_threshold_hours
    status = "fresh" if is_fresh else "stale"

    # Generate alerts if stale
    alerts = []
    if not is_fresh:
      alerts.append({
          "severity": "warning" if hours_since_update <= freshness_threshold_hours * 2 else "error",
          "message": f"Data is {round(days_since_update, 1)} days old (threshold: {freshness_threshold_hours} hours)",
          "hours_over_threshold": round(hours_since_update - freshness_threshold_hours, 1),
      })

    return {
        "status": "success",
        "dataset": dataset_id,
        "table": table_id,
        "freshness": {
            "status": status,
            "last_modified": last_modified.isoformat() if isinstance(last_modified, datetime) else str(last_modified),
            "hours_since_update": round(hours_since_update, 2),
            "days_since_update": round(days_since_update, 2),
            "threshold_hours": freshness_threshold_hours,
        },
        "alerts": alerts if alerts else None,
    }

  except Exception as e:
    return {
        "status": "error",
        "error_message": f"Error checking data freshness: {e}",
    }
