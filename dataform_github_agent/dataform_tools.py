# Copyright 2025 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module provides a set of tools for interacting with Google Cloud Dataform.

It includes functionality for generating Dataform SQLX code, identifying files
within LLM-generated output, uploading and compiling those files in Dataform,
and attempting to automatically fix compilation errors using an LLM.
"""

from typing import Any, Dict, List, Optional
from google.api_core.exceptions import GoogleAPIError
from google.cloud import dataform_v1
from google.adk.tools import agent_tool
from datetime import datetime, timedelta
import re
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

DATAFORM_CLIENT = dataform_v1.DataformClient()

def get_workspace_path() -> str:
  """Get the workspace path using configuration."""
  return DATAFORM_CLIENT.workspace_path(
      config.project_id,
      config.location,
      config.repository_name,
      config.workspace_name,
  )

@agent_tool
def write_file_to_dataform(file_content: str, file_path: str) -> str:
  """Upload a file to Dataform.

  Args:
      file_content (str): The content of the file to upload.
      file_path (str): The fully qualified path of the file to upload.

  Returns:
      str: Result of the upload operation.
  """
  workspace_path = get_workspace_path()
  print(f"Uploading file: {file_path}")
  try:
    request = dataform_v1.WriteFileRequest(
        workspace=workspace_path,
        path=file_path,
        contents=file_content.encode("utf-8"),
    )
    DATAFORM_CLIENT.write_file(request=request)
    print(f"File Uploaded: {file_path}")
    return f"File Uploaded: {file_path}"
  except GoogleAPIError as e:
    error_msg = f"Error uploading file '{file_path}': {e}"
    print(error_msg)
    return error_msg


@agent_tool
def delete_file_from_dataform(file_path: str) -> str:
  """Delete a file from Dataform.

  Args:
      file_path (str): The fully qualified path of the file to delete.

  Returns:
      str: Result of the deletion operation.
  """
  workspace_path = get_workspace_path()
  request = dataform_v1.RemoveFileRequest(
      workspace=workspace_path,
      path=file_path,
  )
  try:
    DATAFORM_CLIENT.remove_file(request=request)
    print(f"File Deleted: {file_path}")
    return f"File Deleted: {file_path}"
  except GoogleAPIError as e:
    error_msg = f"Error deleting file '{file_path}': {e}"
    print(error_msg)
    return error_msg


@agent_tool
def compile_dataform(compile_only: bool = False) -> Dict[str, Any]:
  """Compile Dataform pipeline and get overview of the pipeline DAG.

  Args:
      compile_only (bool): If True, only compile without execution.

  Returns:
      Dict[str, Any]: Compilation results including status and pipeline DAG.
  """
  try:
    repository_path = DATAFORM_CLIENT.repository_path(
        config.project_id, config.location, config.repository_name
    )
    workspace_path = get_workspace_path()

    print("Compiling...")
    compilation_result = dataform_v1.CompilationResult()
    compilation_result.git_commitish = "main"
    compilation_result.workspace = workspace_path

    request = dataform_v1.CreateCompilationResultRequest(
        parent=repository_path, compilation_result=compilation_result
    )

    compilation_results = DATAFORM_CLIENT.create_compilation_result(
        request=request
    )

    if compilation_results.compilation_errors:
      print("Compilation errors found!")
      return {
          "status": "error",
          "error_message": str(compilation_results.compilation_errors),
      }

    request = dataform_v1.QueryCompilationResultActionsRequest(
        name=compilation_results.name,
    )

    actions = DATAFORM_CLIENT.query_compilation_result_actions(
        request=request
    ).compilation_result_actions

    if compile_only:
      return {
          "status": "success",
          "message": "Compilation successful (compile-only mode)",
          "pipeline_dag": str(actions),
      }

    # Execute the workflow if not in compile-only mode
    workflow_invocation = dataform_v1.WorkflowInvocation()
    workflow_invocation.compilation_result = compilation_results.name

    request = dataform_v1.CreateWorkflowInvocationRequest(
        parent=repository_path, workflow_invocation=workflow_invocation
    )

    workflow_invocation = DATAFORM_CLIENT.create_workflow_invocation(
        request=request
    )

    return {
        "status": "success",
        "message": "Compilation and execution successful",
        "pipeline_dag": str(actions),
        "workflow_invocation_id": workflow_invocation.name,
    }

  except GoogleAPIError as e:
    error_msg = f"Error in Dataform operation: {e}"
    print(error_msg)
    return {"status": "error", "error_message": error_msg}

@agent_tool
def read_file_from_dataform(file_path: str) -> str:
  """Read a file from Dataform.

  Args:
      file_path (str): The fully qualified path of the file to read.

  Returns:
      str: The content of the file.
  """
  workspace_path = get_workspace_path()
  print(f"Reading file: {file_path}")
  try:
    request = dataform_v1.ReadFileRequest(
        workspace=workspace_path,
        path=file_path,
    )
    response = DATAFORM_CLIENT.read_file(request=request)
    print(f"File Read: {file_path}")
    return response.file_contents.decode("utf-8")
  except GoogleAPIError as e:
    error_msg = f"Error reading file '{file_path}': {e}"
    print(error_msg)
    return error_msg

@agent_tool
def search_files_in_dataform(pattern: Optional[str] = None) -> List[str]:
  """Search for files in Dataform.

  Args:
      pattern (Optional[str]): Optional pattern to filter files.

  Returns:
      List[str]: A list of file names matching the pattern.
  """
  workspace_path = get_workspace_path()
  try:
    request = dataform_v1.SearchFilesRequest(
        workspace=workspace_path,
    )
    response = DATAFORM_CLIENT.search_files(request=request)
    all_files = [page.file.path for page in response if page.file]

    if pattern:
      all_files = [f for f in all_files if pattern in f]

    print(f"Files found: {all_files}")
    return all_files
  except GoogleAPIError as e:
    print(f"Error searching files: {e}")
    return []


@agent_tool
def get_dataform_execution_logs(workflow_invocation_id: str) -> Dict[str, Any]:
  """Use this function to get execution logs for a Dataform workflow invocation.

  Args:
      workflow_invocation_id (str): The full ID of the workflow invocation.
        (e.g.,
        projects/PROJECT_ID/locations/LOCATION/repositories/REPOSITORY_NAME/workflowInvocations/WORKFLOW_INVOCATION_ID)

  Returns:
      Dict[str, Any]: A dictionary containing the status and actions of the
      workflow invocation.
                      "status": "success" or "error"
                      "actions": A list of actions with their details (name,
                      status, logs/errors).
                      "error_message": Present if the overall status is "error".
  """
  try:
    request = dataform_v1.QueryWorkflowInvocationActionsRequest(
        name=workflow_invocation_id,
    )
    actions_response = DATAFORM_CLIENT.query_workflow_invocation_actions(
        request=request
    )

    actions_details = []
    for action in actions_response.workflow_invocation_actions:
      action_detail = {
          "name": action.target.name,
          "status": (
              dataform_v1.WorkflowInvocationAction.State(action.state).name
          ),
      }
      if action.state == dataform_v1.WorkflowInvocationAction.State.FAILED:
        action_detail["error_message"] = action.failure_reason
      if action.canonical_target.name:  # Check if canonical_target has name
        action_detail["canonical_target_name"] = action.canonical_target.name
      if action.bigquery_action:  # Check if bigquery_action exists
        action_detail["job_id"] = action.bigquery_action.job_id

      # Potentially, logs could be found in different fields depending on the action type
      # For now, focusing on BigQuery action job ID, which can be used to fetch logs from BigQuery directly.
      # Also, failure_reason provides some error information.
      actions_details.append(action_detail)

    # Determine overall status
    # The WorkflowInvocation itself has a state. We might need to fetch the WorkflowInvocation object
    # using get_workflow_invocation to get the overall status.
    # For now, let's assume if any action failed, the invocation is considered failed for logging purposes.
    overall_status = "success"
    for ad in actions_details:
      if ad["status"] == "FAILED":
        overall_status = "error"
        break

    if overall_status == "error":
      return {
          "status": "error",
          "error_message": (
              "One or more actions failed in workflow invocation"
              f" {workflow_invocation_id}. See actions for details."
          ),
          "actions": actions_details,
      }

    return {"status": "success", "actions": actions_details}

  except GoogleAPIError as e:
    print(f"Error getting execution logs for '{workflow_invocation_id}': {e}")
    return {
        "status": "error",
        "error_message": (
            f"Error getting execution logs for '{workflow_invocation_id}': {e}"
        ),
    }


@agent_tool
def execute_dataform_workflow(
    workflow_name: str, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
  """Execute a Dataform workflow with optional parameters.

  Args:
      workflow_name (str): The name of the workflow to execute.
      params (Optional[Dict[str, Any]]): Optional parameters for the workflow
        execution.

  Returns:
      Dict[str, Any]: Execution results including status and workflow invocation
      ID.
  """
  try:
    repository_path = DATAFORM_CLIENT.repository_path(
        config.project_id, config.location, config.repository_name
    )

    # Create workflow invocation
    workflow_invocation = dataform_v1.WorkflowInvocation()
    workflow_invocation.workflow_config = workflow_name

    # Add parameters if provided
    if params:
      workflow_invocation.invocation_config = dataform_v1.InvocationConfig(
          parameters=params
      )

    request = dataform_v1.CreateWorkflowInvocationRequest(
        parent=repository_path, workflow_invocation=workflow_invocation
    )

    # Execute the workflow
    workflow_invocation = DATAFORM_CLIENT.create_workflow_invocation(
        request=request
    )

    return {
        "status": "success",
        "message": "Workflow execution started",
        "workflow_invocation_id": workflow_invocation.name,
        "workflow_name": workflow_name,
        "parameters": params,
    }

  except GoogleAPIError as e:
    error_msg = f"Error executing workflow '{workflow_name}': {e}"
    print(error_msg)
    return {"status": "error", "error_message": error_msg}


@agent_tool
def execute_dataform_by_tags(
    tags: List[str], compile_only: bool = False
) -> Dict[str, Any]:
  """Execute Dataform actions filtered by specific tags.

  This is useful when you want to run specific parts of a pipeline without needing
  a pre-configured workflow. You can use any combination of tags from your Dataform
  files (e.g., ['silver', 'staging'], ['gold', 'looker'], ['cost', 'pltv']).

  Args:
      tags (List[str]): List of tags to filter actions. Actions must have ALL
        specified tags to be included (AND logic).
        Examples:
        - ['pltv', 'staging'] → Only actions with both 'pltv' AND 'staging' tags
        - ['silver'] → All actions with 'silver' tag
        - ['cost', 'extract'] → Only actions with both 'cost' AND 'extract' tags
        - ['gold', 'pltv', 'looker'] → Only actions with all three tags
      compile_only (bool): If True, only compile without execution (default: False).

  Returns:
      Dict[str, Any]: Execution results including status, workflow invocation ID,
      and list of actions that will be executed.
  """
  try:
    repository_path = DATAFORM_CLIENT.repository_path(
        config.project_id, config.location, config.repository_name
    )
    workspace_path = get_workspace_path()

    # First, compile to get all actions
    print("Compiling to get actions with tags...")
    compilation_result = dataform_v1.CompilationResult()
    compilation_result.git_commitish = "main"
    compilation_result.workspace = workspace_path

    request = dataform_v1.CreateCompilationResultRequest(
        parent=repository_path, compilation_result=compilation_result
    )

    compilation_results = DATAFORM_CLIENT.create_compilation_result(
        request=request
    )

    if compilation_results.compilation_errors:
      return {
          "status": "error",
          "error_message": f"Compilation errors: {compilation_results.compilation_errors}",
      }

    # Get all actions
    request = dataform_v1.QueryCompilationResultActionsRequest(
        name=compilation_results.name,
    )

    all_actions = DATAFORM_CLIENT.query_compilation_result_actions(
        request=request
    ).compilation_result_actions

    # Filter actions by tags
    # Tags are stored in action.target.database_target.tags
    filtered_actions = []
    for action in all_actions:
      action_tags = []
      if action.target.database_target:
        action_tags = list(action.target.database_target.tags) if action.target.database_target.tags else []
      
      # Check if action has all required tags
      if all(tag in action_tags for tag in tags):
        filtered_actions.append(action.target)

    if not filtered_actions:
      return {
          "status": "error",
          "error_message": f"No actions found with all tags: {tags}",
          "available_tags": _get_available_tags(all_actions),
      }

    if compile_only:
      return {
          "status": "success",
          "message": f"Found {len(filtered_actions)} actions with tags {tags}",
          "actions": [str(action) for action in filtered_actions],
          "mode": "compile_only",
      }

    # Create workflow invocation with filtered actions
    workflow_invocation = dataform_v1.WorkflowInvocation()
    workflow_invocation.compilation_result = compilation_results.name
    
    # Set target actions
    invocation_config = dataform_v1.InvocationConfig()
    invocation_config.included_targets = filtered_actions
    workflow_invocation.invocation_config = invocation_config

    request = dataform_v1.CreateWorkflowInvocationRequest(
        parent=repository_path, workflow_invocation=workflow_invocation
    )

    workflow_invocation = DATAFORM_CLIENT.create_workflow_invocation(
        request=request
    )

    return {
        "status": "success",
        "message": f"Workflow execution started for {len(filtered_actions)} actions with tags {tags}",
        "workflow_invocation_id": workflow_invocation.name,
        "tags": tags,
        "actions_count": len(filtered_actions),
    }

  except GoogleAPIError as e:
    error_msg = f"Error executing Dataform by tags: {e}"
    print(error_msg)
    return {"status": "error", "error_message": error_msg}


def _get_available_tags(actions: List[Any]) -> List[str]:
  """Extract all unique tags from actions."""
  all_tags = set()
  for action in actions:
    if action.target.database_target and action.target.database_target.tags:
      all_tags.update(action.target.database_target.tags)
  return sorted(list(all_tags))


@agent_tool
def read_workflow_settings() -> str:
  """Read the workflow_settings.yaml file from Dataform.

  Returns:
      str: The content of workflow_settings.yaml file.
  """
  workspace_path = get_workspace_path()
  try:
    file_content = read_file_from_dataform("workflow_settings.yaml")
    return file_content
  except Exception as e:
    error_msg = f"Error reading workflow_settings.yaml: {e}"
    print(error_msg)
    return error_msg


@agent_tool
def get_workflow_status(workflow_invocation_id: str) -> Dict[str, Any]:
  """Get the current status of a Dataform workflow invocation.

  Args:
      workflow_invocation_id (str): The full ID of the workflow invocation.

  Returns:
      Dict[str, Any]: Current status of the workflow including state and progress.
  """
  try:
    workflow_invocation = DATAFORM_CLIENT.get_workflow_invocation(
        name=workflow_invocation_id
    )

    return {
        "status": "success",
        "workflow_invocation_id": workflow_invocation_id,
        "state": dataform_v1.WorkflowInvocation.State(workflow_invocation.state).name,
        "create_time": workflow_invocation.create_time.isoformat() if workflow_invocation.create_time else None,
        "update_time": workflow_invocation.update_time.isoformat() if workflow_invocation.update_time else None,
    }

  except GoogleAPIError as e:
    error_msg = f"Error getting workflow status: {e}"
    print(error_msg)
    return {"status": "error", "error_message": error_msg}


@agent_tool
def get_dataform_repo_link() -> Dict[str, str]:
  """Generate the GCP console link for the Dataform repository.

  Returns:
      Dict[str, str]: Dictionary containing the repository link and additional
      information.
  """
  try:
    # Construct the GCP console URL for the Dataform repository
    base_url = "https://console.cloud.google.com"
    repo_path = f"/bigquery/dataform/locations/{config.location}/repositories/{config.repository_name}/workspaces/{config.workspace_name}"

    repo_url = f"{base_url}{repo_path}"

    return {
        "status": "success",
        "repository_url": repo_url,
        "repository_name": config.repository_name,
        "project_id": config.project_id,
        "location": config.location,
        "workspace_name": config.workspace_name,
    }
  except Exception as e:
    error_msg = f"Error generating repository link: {e}"
    print(error_msg)
    return {"status": "error", "error_message": error_msg}


@agent_tool
def monitor_workflow_health(
    workflow_name: Optional[str] = None, days: int = 7
) -> Dict[str, Any]:
  """Monitor workflow execution health over a time period.

  Args:
      workflow_name (Optional[str]): Specific workflow name to monitor. If None, monitors all workflows.
      days (int): Number of days to look back (default: 7).

  Returns:
      Dict[str, Any]: Health metrics including success rate, average duration, failure patterns, and trends.
  """
  try:
    repository_path = DATAFORM_CLIENT.repository_path(
        config.project_id, config.location, config.repository_name
    )

    # Calculate time threshold
    time_threshold = datetime.utcnow() - timedelta(days=days)
    time_threshold_str = time_threshold.strftime("%Y-%m-%dT%H:%M:%SZ")

    # List workflow invocations
    request = dataform_v1.ListWorkflowInvocationsRequest(
        parent=repository_path,
    )

    all_invocations = []
    page = DATAFORM_CLIENT.list_workflow_invocations(request=request)
    for invocation in page:
      # Filter by workflow name if specified
      if workflow_name and invocation.workflow_config != workflow_name:
        continue

      # Filter by time
      if invocation.create_time:
        if invocation.create_time < time_threshold:
          continue

      all_invocations.append(invocation)

    if not all_invocations:
      return {
          "status": "success",
          "message": f"No workflow invocations found in the last {days} days",
          "workflow_name": workflow_name,
          "days": days,
      }

    # Calculate metrics
    total_invocations = len(all_invocations)
    successful = sum(1 for inv in all_invocations if inv.state == dataform_v1.WorkflowInvocation.State.SUCCEEDED)
    failed = sum(1 for inv in all_invocations if inv.state == dataform_v1.WorkflowInvocation.State.FAILED)
    success_rate = (successful / total_invocations * 100) if total_invocations > 0 else 0

    # Calculate average duration (if available)
    durations = []
    for inv in all_invocations:
      if inv.create_time and inv.update_time:
        duration = (inv.update_time - inv.create_time).total_seconds()
        durations.append(duration)

    avg_duration_seconds = sum(durations) / len(durations) if durations else None

    # Identify failure patterns
    failure_patterns = []
    if failed > 0:
      failure_reasons = {}
      for inv in all_invocations:
        if inv.state == dataform_v1.WorkflowInvocation.State.FAILED:
          # Try to get error from invocation
          error_key = "unknown_error"
          if hasattr(inv, 'compilation_result') and inv.compilation_result:
            error_key = "compilation_error"
          failure_reasons[error_key] = failure_reasons.get(error_key, 0) + 1

      failure_patterns = [
          {"reason": reason, "count": count}
          for reason, count in failure_reasons.items()
      ]

    # Identify trends (compare first half vs second half)
    trend = None
    if total_invocations >= 4:
      first_half = all_invocations[:total_invocations // 2]
      second_half = all_invocations[total_invocations // 2:]

      first_success_rate = (
          sum(1 for inv in first_half if inv.state == dataform_v1.WorkflowInvocation.State.SUCCEEDED)
          / len(first_half) * 100
      )
      second_success_rate = (
          sum(1 for inv in second_half if inv.state == dataform_v1.WorkflowInvocation.State.SUCCEEDED)
          / len(second_half) * 100
      )

      if second_success_rate > first_success_rate + 5:
        trend = "improving"
      elif second_success_rate < first_success_rate - 5:
        trend = "degrading"
      else:
        trend = "stable"

    return {
        "status": "success",
        "workflow_name": workflow_name or "all_workflows",
        "period_days": days,
        "metrics": {
            "total_invocations": total_invocations,
            "successful": successful,
            "failed": failed,
            "success_rate_percent": round(success_rate, 2),
            "average_duration_seconds": round(avg_duration_seconds, 2) if avg_duration_seconds else None,
        },
        "failure_patterns": failure_patterns if failure_patterns else None,
        "trend": trend,
    }

  except GoogleAPIError as e:
    error_msg = f"Error monitoring workflow health: {e}"
    print(error_msg)
    return {"status": "error", "error_message": error_msg}


@agent_tool
def get_failed_workflows(days: int = 7) -> List[Dict[str, Any]]:
  """Get list of failed workflows with error details.

  Args:
      days (int): Number of days to look back (default: 7).

  Returns:
      List[Dict[str, Any]]: List of failed workflow invocations with error information.
  """
  try:
    repository_path = DATAFORM_CLIENT.repository_path(
        config.project_id, config.location, config.repository_name
    )

    time_threshold = datetime.utcnow() - timedelta(days=days)
    time_threshold_str = time_threshold.strftime("%Y-%m-%dT%H:%M:%SZ")

    request = dataform_v1.ListWorkflowInvocationsRequest(
        parent=repository_path,
    )

    failed_workflows = []
    page = DATAFORM_CLIENT.list_workflow_invocations(request=request)
    for invocation in page:
      if invocation.state != dataform_v1.WorkflowInvocation.State.FAILED:
        continue

      if invocation.create_time and invocation.create_time < time_threshold:
        continue

      # Get detailed error information
      workflow_info = {
          "workflow_invocation_id": invocation.name,
          "workflow_config": invocation.workflow_config if hasattr(invocation, 'workflow_config') else None,
          "create_time": invocation.create_time.isoformat() if invocation.create_time else None,
          "update_time": invocation.update_time.isoformat() if invocation.update_time else None,
      }

      # Try to get execution logs for more details
      try:
        logs = get_dataform_execution_logs(invocation.name)
        if logs.get("status") == "success" and logs.get("actions"):
          failed_actions = [
              action for action in logs["actions"]
              if action.get("status") == "FAILED"
          ]
          if failed_actions:
            workflow_info["failed_actions"] = failed_actions
            workflow_info["error_summary"] = failed_actions[0].get("error_message", "Unknown error")
      except Exception:
        pass  # If we can't get logs, continue without them

      failed_workflows.append(workflow_info)

    return {
        "status": "success",
        "days": days,
        "failed_workflows": failed_workflows,
        "count": len(failed_workflows),
    }

  except GoogleAPIError as e:
    error_msg = f"Error getting failed workflows: {e}"
    print(error_msg)
    return {"status": "error", "error_message": error_msg, "failed_workflows": []}


@agent_tool
def check_pipeline_health(tags: Optional[List[str]] = None) -> Dict[str, Any]:
  """Check overall pipeline health by analyzing recent executions.

  Args:
      tags (Optional[List[str]]): Filter by specific tags. If None, checks all pipelines.

  Returns:
      Dict[str, Any]: Overall health status, metrics, and recommendations.
  """
  try:
    # First, compile to get actions with tags
    repository_path = DATAFORM_CLIENT.repository_path(
        config.project_id, config.location, config.repository_name
    )
    workspace_path = get_workspace_path()

    compilation_result = dataform_v1.CompilationResult()
    compilation_result.git_commitish = "main"
    compilation_result.workspace = workspace_path

    request = dataform_v1.CreateCompilationResultRequest(
        parent=repository_path, compilation_result=compilation_result
    )

    compilation_results = DATAFORM_CLIENT.create_compilation_result(request=request)

    if compilation_results.compilation_errors:
      return {
          "status": "error",
          "error_message": f"Compilation errors: {compilation_results.compilation_errors}",
      }

    # Get all actions
    request = dataform_v1.QueryCompilationResultActionsRequest(
        name=compilation_results.name,
    )

    all_actions = DATAFORM_CLIENT.query_compilation_result_actions(
        request=request
    ).compilation_result_actions

    # Filter by tags if provided
    if tags:
      filtered_actions = []
      for action in all_actions:
        action_tags = []
        if action.target.database_target:
          action_tags = list(action.target.database_target.tags) if action.target.database_target.tags else []
        if all(tag in action_tags for tag in tags):
          filtered_actions.append(action)
      actions_to_check = filtered_actions
    else:
      actions_to_check = list(all_actions)

    # Get recent workflow invocations to analyze
    health_metrics = monitor_workflow_health(days=7)

    # Calculate health score
    health_score = 100
    issues = []

    if health_metrics.get("status") == "success":
      success_rate = health_metrics.get("metrics", {}).get("success_rate_percent", 100)
      health_score = success_rate

      if success_rate < 90:
        issues.append(f"Low success rate: {success_rate}%")
      if health_metrics.get("trend") == "degrading":
        issues.append("Pipeline health is degrading over time")

    # Determine overall health status
    if health_score >= 95:
      status = "healthy"
    elif health_score >= 80:
      status = "warning"
    else:
      status = "critical"

    recommendations = []
    if issues:
      recommendations.append("Review failed workflows to identify root causes")
    if health_metrics.get("failure_patterns"):
      recommendations.append("Address common failure patterns")
    if not recommendations:
      recommendations.append("Pipeline is operating normally")

    return {
        "status": "success",
        "pipeline_health": {
            "overall_status": status,
            "health_score": round(health_score, 2),
            "actions_analyzed": len(actions_to_check),
            "tags_filter": tags,
        },
        "metrics": health_metrics.get("metrics") if health_metrics.get("status") == "success" else None,
        "issues": issues if issues else None,
        "recommendations": recommendations,
    }

  except GoogleAPIError as e:
    error_msg = f"Error checking pipeline health: {e}"
    print(error_msg)
    return {"status": "error", "error_message": error_msg}


def _parse_sqlx_config(file_content: str) -> Dict[str, Any]:
  """Parse config block from SQLX file.

  Args:
      file_content (str): Content of SQLX file.

  Returns:
      Dict[str, Any]: Parsed config information.
  """
  config_info = {}

  # Extract config block
  config_match = re.search(r'config\s*\{([^}]+)\}', file_content, re.DOTALL)
  if config_match:
    config_block = config_match.group(1)

    # Extract type
    type_match = re.search(r'type:\s*"([^"]+)"', config_block)
    if type_match:
      config_info["type"] = type_match.group(1)

    # Extract name
    name_match = re.search(r'name:\s*"([^"]+)"', config_block)
    if name_match:
      config_info["name"] = name_match.group(1)

    # Extract description
    desc_match = re.search(r'description:\s*"([^"]+)"', config_block)
    if desc_match:
      config_info["description"] = desc_match.group(1)

    # Extract tags
    tags_match = re.search(r'tags:\s*\[([^\]]+)\]', config_block)
    if tags_match:
      tags_str = tags_match.group(1)
      tags = [tag.strip().strip('"') for tag in tags_str.split(',')]
      config_info["tags"] = tags

    # Extract dependencies
    deps_match = re.search(r'dependencies:\s*\[([^\]]+)\]', config_block)
    if deps_match:
      deps_str = deps_match.group(1)
      # Handle ref() calls
      deps = []
      for dep in re.findall(r'ref\(["\']([^"\']+)["\']\)', deps_str):
        deps.append(dep)
      config_info["dependencies"] = deps

  return config_info


@agent_tool
def generate_pipeline_documentation(output_format: str = "markdown") -> str:
  """Generate comprehensive pipeline documentation from Dataform files.

  Args:
      output_format (str): Output format - currently only "markdown" supported (default: "markdown").

  Returns:
      str: Generated documentation in the specified format.
  """
  try:
    # Get all SQLX files
    all_files = search_files_in_dataform()
    sqlx_files = [f for f in all_files if f.endswith('.sqlx')]

    if not sqlx_files:
      return "No SQLX files found in Dataform workspace."

    # Parse all files
    files_info = []
    dependency_graph = {}
    tags_map = {}

    for file_path in sqlx_files:
      try:
        file_content = read_file_from_dataform(file_path)
        config_info = _parse_sqlx_config(file_content)

        file_info = {
            "path": file_path,
            "config": config_info,
        }

        # Build dependency graph
        if config_info.get("dependencies"):
          file_name = config_info.get("name") or file_path
          dependency_graph[file_name] = config_info["dependencies"]

        # Map tags
        if config_info.get("tags"):
          for tag in config_info["tags"]:
            if tag not in tags_map:
              tags_map[tag] = []
            tags_map[tag].append(file_path)

        files_info.append(file_info)
      except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        continue

    # Generate markdown documentation
    if output_format == "markdown":
      doc_lines = [
          "# Dataform Pipeline Documentation",
          "",
          f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
          f"**Total Files:** {len(sqlx_files)}",
          "",
          "## Pipeline Overview",
          "",
      ]

      # Group by type
      by_type = {}
      for file_info in files_info:
        file_type = file_info["config"].get("type", "unknown")
        if file_type not in by_type:
          by_type[file_type] = []
        by_type[file_type].append(file_info)

      for file_type, files in by_type.items():
        doc_lines.append(f"### {file_type.capitalize()} Files ({len(files)})")
        doc_lines.append("")
        for file_info in files:
          name = file_info["config"].get("name", file_info["path"])
          desc = file_info["config"].get("description", "No description")
          doc_lines.append(f"- **{name}** ({file_info['path']})")
          doc_lines.append(f"  - {desc}")
          if file_info["config"].get("tags"):
            doc_lines.append(f"  - Tags: {', '.join(file_info['config']['tags'])}")
          if file_info["config"].get("dependencies"):
            doc_lines.append(f"  - Dependencies: {', '.join(file_info['config']['dependencies'])}")
        doc_lines.append("")

      # Dependency graph
      if dependency_graph:
        doc_lines.append("## Dependency Graph")
        doc_lines.append("")
        doc_lines.append("```mermaid")
        doc_lines.append("graph TD")
        for node, deps in dependency_graph.items():
          for dep in deps:
            doc_lines.append(f'    {node.replace("-", "_").replace(".", "_")} --> {dep.replace("-", "_").replace(".", "_")}')
        doc_lines.append("```")
        doc_lines.append("")

      # Tags section
      if tags_map:
        doc_lines.append("## Tags")
        doc_lines.append("")
        for tag, files in sorted(tags_map.items()):
          doc_lines.append(f"### {tag}")
          doc_lines.append(f"**Files ({len(files)}):**")
          for file_path in files:
            doc_lines.append(f"- {file_path}")
          doc_lines.append("")

      return "\n".join(doc_lines)

    else:
      return f"Unsupported output format: {output_format}"

  except Exception as e:
    error_msg = f"Error generating pipeline documentation: {e}"
    print(error_msg)
    return error_msg


@agent_tool
def analyze_assertion_results(workflow_invocation_id: str) -> Dict[str, Any]:
  """Analyze assertion results from a workflow execution.

  Args:
      workflow_invocation_id (str): The workflow invocation ID to analyze.

  Returns:
      Dict[str, Any]: Assertion analysis including failed assertions, patterns, and recommendations.
  """
  try:
    # Get execution logs
    logs = get_dataform_execution_logs(workflow_invocation_id)

    if logs.get("status") != "success":
      return {
          "status": "error",
          "error_message": f"Could not get execution logs: {logs.get('error_message')}",
      }

    actions = logs.get("actions", [])
    if not actions:
      return {
          "status": "success",
          "message": "No actions found in workflow invocation",
          "assertion_results": [],
      }

    # Filter assertion actions
    assertion_actions = [
        action for action in actions
        if "assertion" in action.get("name", "").lower() or action.get("status") == "FAILED"
    ]

    failed_assertions = [
        action for action in assertion_actions
        if action.get("status") == "FAILED"
    ]

    # Analyze patterns
    patterns = {}
    for action in failed_assertions:
      action_name = action.get("name", "unknown")
      # Extract table name from action name if possible
      table_match = re.search(r'(\w+\.\w+)', action_name)
      if table_match:
        table = table_match.group(1)
        patterns[table] = patterns.get(table, 0) + 1

    # Generate recommendations
    recommendations = []
    if failed_assertions:
      recommendations.append(f"{len(failed_assertions)} assertion(s) failed - review data quality")
      if patterns:
        most_failed_table = max(patterns.items(), key=lambda x: x[1])
        recommendations.append(f"Table {most_failed_table[0]} has {most_failed_table[1]} failed assertions - investigate data quality")

    return {
        "status": "success",
        "workflow_invocation_id": workflow_invocation_id,
        "assertion_analysis": {
            "total_assertions": len(assertion_actions),
            "failed_assertions": len(failed_assertions),
            "success_rate": round((len(assertion_actions) - len(failed_assertions)) / len(assertion_actions) * 100, 2) if assertion_actions else 100,
        },
        "failed_assertions": failed_assertions if failed_assertions else None,
        "failure_patterns": patterns if patterns else None,
        "recommendations": recommendations if recommendations else ["All assertions passed"],
    }

  except Exception as e:
    error_msg = f"Error analyzing assertion results: {e}"
    print(error_msg)
    return {"status": "error", "error_message": error_msg}


@agent_tool
def check_data_quality_anomalies(table_name: str, days: int = 30) -> Dict[str, Any]:
  """Check for data quality anomalies by analyzing assertion failure history.

  Args:
      table_name (str): Table name to check (format: dataset.table or just table).
      days (int): Number of days to analyze (default: 30).

  Returns:
      Dict[str, Any]: Anomaly detection report with failure trends and recommendations.
  """
  try:
    # Get recent workflow invocations
    repository_path = DATAFORM_CLIENT.repository_path(
        config.project_id, config.location, config.repository_name
    )

    time_threshold = datetime.utcnow() - timedelta(days=days)

    request = dataform_v1.ListWorkflowInvocationsRequest(
        parent=repository_path,
    )

    assertion_failures = []
    page = DATAFORM_CLIENT.list_workflow_invocations(request=request)
    for invocation in page:
      if invocation.create_time and invocation.create_time < time_threshold:
        continue

      # Get execution logs
      try:
        logs = get_dataform_execution_logs(invocation.name)
        if logs.get("status") == "success":
          actions = logs.get("actions", [])
          for action in actions:
            action_name = action.get("name", "")
            if table_name.lower() in action_name.lower() and action.get("status") == "FAILED":
              assertion_failures.append({
                  "workflow_invocation_id": invocation.name,
                  "action_name": action_name,
                  "error_message": action.get("error_message"),
                  "timestamp": invocation.create_time.isoformat() if invocation.create_time else None,
              })
      except Exception:
        continue

    # Analyze trends
    failure_count = len(assertion_failures)
    failure_rate = (failure_count / days) if days > 0 else 0

    # Detect anomalies
    anomalies = []
    if failure_count > 10:
      anomalies.append({
          "type": "high_failure_count",
          "message": f"High number of failures ({failure_count}) in last {days} days",
          "severity": "high" if failure_count > 20 else "medium",
      })

    if failure_rate > 0.5:  # More than 0.5 failures per day
      anomalies.append({
          "type": "high_failure_rate",
          "message": f"High failure rate: {round(failure_rate, 2)} failures per day",
          "severity": "high",
      })

    # Check for increasing trend (last 7 days vs previous 7 days)
    if days >= 14:
      recent_failures = []
      older_failures = []
      for f in assertion_failures:
        if f.get("timestamp"):
          try:
            # Handle different timestamp formats
            timestamp_str = f["timestamp"]
            if timestamp_str.endswith('Z'):
              timestamp_str = timestamp_str.replace('Z', '+00:00')
            timestamp = datetime.fromisoformat(timestamp_str)
            # Convert to UTC naive datetime for comparison
            if timestamp.tzinfo:
              timestamp = timestamp.replace(tzinfo=None)
            threshold = datetime.utcnow() - timedelta(days=7)
            if timestamp > threshold:
              recent_failures.append(f)
            else:
              older_failures.append(f)
          except (ValueError, AttributeError):
            # Skip if timestamp parsing fails
            continue

      if len(recent_failures) > len(older_failures) * 1.5:
        anomalies.append({
            "type": "increasing_trend",
            "message": "Failure rate is increasing - recent failures exceed historical average",
            "severity": "medium",
        })

    recommendations = []
    if anomalies:
      recommendations.append("Investigate root cause of assertion failures")
      recommendations.append("Review data quality rules and thresholds")
      recommendations.append("Consider adding more granular assertions")
    else:
      recommendations.append("Data quality appears stable")

    return {
        "status": "success",
        "table_name": table_name,
        "analysis_period_days": days,
        "anomaly_detection": {
            "total_failures": failure_count,
            "failure_rate_per_day": round(failure_rate, 2),
            "anomalies_detected": len(anomalies),
        },
        "anomalies": anomalies if anomalies else None,
        "recent_failures": assertion_failures[:10] if assertion_failures else None,  # Last 10 failures
        "recommendations": recommendations,
    }

  except Exception as e:
    error_msg = f"Error checking data quality anomalies: {e}"
    print(error_msg)
    return {"status": "error", "error_message": error_msg}
