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
