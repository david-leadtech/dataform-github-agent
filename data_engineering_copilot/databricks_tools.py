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

"""This module provides tools for managing Databricks clusters, jobs, and notebooks.

It includes functionality for cluster management, job submission, notebook execution,
and monitoring. Useful for running PySpark workloads on Databricks.
"""

import logging
from typing import Any, Dict, List, Optional

from google.adk.tools import agent_tool

import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

logger = logging.getLogger(__name__)

# Try to import Databricks SDK
try:
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.compute import (
        ClusterSpec,
        DataSecurityMode,
        SparkVersion,
    )
    from databricks.sdk.service.jobs import (
        JobSettings,
        NotebookTask,
        PythonWheelTask,
        SparkPythonTask,
        Task,
    )
    DATABRICKS_AVAILABLE = True
except ImportError:
    DATABRICKS_AVAILABLE = False
    logger.warning(
        "Databricks SDK not installed. Install with: pip install databricks-sdk"
    )


def _get_databricks_client() -> Optional[Any]:
    """Get Databricks WorkspaceClient instance.

    Requires DATABRICKS_HOST and DATABRICKS_TOKEN environment variables.
    """
    if not DATABRICKS_AVAILABLE:
        return None

    databricks_host = config.databricks_host or os.getenv("DATABRICKS_HOST")
    databricks_token = config.databricks_token or os.getenv("DATABRICKS_TOKEN")

    if not databricks_host or not databricks_token:
        logger.warning(
            "Databricks credentials not configured. Set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables."
        )
        return None

    try:
        return WorkspaceClient(
            host=databricks_host,
            token=databricks_token,
        )
    except Exception as e:
        logger.error(f"Error creating Databricks client: {e}", exc_info=True)
        return None


# ==================== CLUSTER MANAGEMENT ====================


@agent_tool
def create_databricks_cluster(
    cluster_name: str,
    num_workers: int = 2,
    node_type_id: str = "i3.xlarge",
    spark_version: str = "14.3.x-scala2.12",
    autotermination_minutes: int = 60,
    spark_conf: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Create a new Databricks cluster.

    Args:
        cluster_name: Name of the cluster to create.
        num_workers: Number of worker nodes (default: 2).
        node_type_id: Instance type for nodes (default: 'i3.xlarge').
        spark_version: Spark version (default: '14.3.x-scala2.12').
        autotermination_minutes: Minutes of inactivity before auto-termination (default: 60).
        spark_conf: Optional Spark configuration dictionary.

    Returns:
        Dict with cluster creation status and cluster ID.
    """
    if not DATABRICKS_AVAILABLE:
        return {
            "status": "error",
            "error_message": "Databricks SDK not installed. Install with: pip install databricks-sdk",
        }

    client = _get_databricks_client()
    if not client:
        return {
            "status": "error",
            "error_message": "Databricks client not available. Configure DATABRICKS_HOST and DATABRICKS_TOKEN.",
        }

    try:
        cluster_spec = ClusterSpec(
            cluster_name=cluster_name,
            num_workers=num_workers,
            node_type_id=node_type_id,
            spark_version=spark_version,
            autotermination_minutes=autotermination_minutes,
            spark_conf=spark_conf or {},
            data_security_mode=DataSecurityMode.SINGLE_USER,
        )

        cluster_info = client.clusters.create(cluster_spec)

        return {
            "status": "success",
            "message": f"Cluster '{cluster_name}' creation initiated",
            "cluster_id": cluster_info.cluster_id,
            "cluster_name": cluster_name,
            "state": cluster_info.state.value if cluster_info.state else "PENDING",
            "note": "Cluster creation may take several minutes. Use get_databricks_cluster_status to check progress.",
        }

    except Exception as e:
        logger.error(f"Error creating Databricks cluster: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to create cluster: {str(e)}",
        }


@agent_tool
def list_databricks_clusters(
    include_terminated: bool = False,
) -> Dict[str, Any]:
    """List all Databricks clusters.

    Args:
        include_terminated: Whether to include terminated clusters (default: False).

    Returns:
        Dict with list of clusters and their status.
    """
    if not DATABRICKS_AVAILABLE:
        return {
            "status": "error",
            "error_message": "Databricks SDK not installed. Install with: pip install databricks-sdk",
        }

    client = _get_databricks_client()
    if not client:
        return {
            "status": "error",
            "error_message": "Databricks client not available. Configure DATABRICKS_HOST and DATABRICKS_TOKEN.",
        }

    try:
        clusters = client.clusters.list()

        cluster_list = []
        for cluster in clusters:
            if not include_terminated and cluster.state and cluster.state.value == "TERMINATED":
                continue

            cluster_info = {
                "cluster_id": cluster.cluster_id,
                "cluster_name": cluster.cluster_name,
                "state": cluster.state.value if cluster.state else "UNKNOWN",
                "num_workers": cluster.num_workers,
                "spark_version": cluster.spark_version,
            }
            cluster_list.append(cluster_info)

        return {
            "status": "success",
            "clusters": cluster_list,
            "count": len(cluster_list),
        }

    except Exception as e:
        logger.error(f"Error listing Databricks clusters: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to list clusters: {str(e)}",
        }


@agent_tool
def get_databricks_cluster_status(
    cluster_id: str,
) -> Dict[str, Any]:
    """Get status and details of a Databricks cluster.

    Args:
        cluster_id: ID of the cluster to check.

    Returns:
        Dict with cluster status and details.
    """
    if not DATABRICKS_AVAILABLE:
        return {
            "status": "error",
            "error_message": "Databricks SDK not installed. Install with: pip install databricks-sdk",
        }

    client = _get_databricks_client()
    if not client:
        return {
            "status": "error",
            "error_message": "Databricks client not available. Configure DATABRICKS_HOST and DATABRICKS_TOKEN.",
        }

    try:
        cluster = client.clusters.get(cluster_id)

        return {
            "status": "success",
            "cluster_id": cluster.cluster_id,
            "cluster_name": cluster.cluster_name,
            "state": cluster.state.value if cluster.state else "UNKNOWN",
            "num_workers": cluster.num_workers,
            "spark_version": cluster.spark_version,
            "node_type_id": cluster.node_type_id,
            "driver_node_type_id": cluster.driver_node_type_id,
            "autotermination_minutes": cluster.autotermination_minutes,
            "start_time": cluster.start_time.isoformat() if cluster.start_time else None,
        }

    except Exception as e:
        logger.error(f"Error getting cluster status: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to get cluster status: {str(e)}",
        }


@agent_tool
def delete_databricks_cluster(
    cluster_id: str,
) -> Dict[str, Any]:
    """Delete a Databricks cluster.

    Args:
        cluster_id: ID of the cluster to delete.

    Returns:
        Dict with deletion status.
    """
    if not DATABRICKS_AVAILABLE:
        return {
            "status": "error",
            "error_message": "Databricks SDK not installed. Install with: pip install databricks-sdk",
        }

    client = _get_databricks_client()
    if not client:
        return {
            "status": "error",
            "error_message": "Databricks client not available. Configure DATABRICKS_HOST and DATABRICKS_TOKEN.",
        }

    try:
        client.clusters.delete(cluster_id)

        return {
            "status": "success",
            "message": f"Cluster {cluster_id} deletion initiated",
            "cluster_id": cluster_id,
        }

    except Exception as e:
        logger.error(f"Error deleting Databricks cluster: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to delete cluster: {str(e)}",
        }


# ==================== JOB MANAGEMENT ====================


@agent_tool
def submit_databricks_pyspark_job(
    job_name: str,
    python_file: str,
    cluster_id: Optional[str] = None,
    existing_cluster_id: Optional[str] = None,
    parameters: Optional[List[str]] = None,
    libraries: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Submit a PySpark job to Databricks.

    Args:
        job_name: Name for the job.
        python_file: Path to Python file in Databricks workspace (e.g., '/Workspace/scripts/process.py')
                     or DBFS path (e.g., 'dbfs:/scripts/process.py').
        cluster_id: ID of existing cluster to use (alternative to existing_cluster_id).
        existing_cluster_id: ID of existing cluster (alternative to cluster_id).
        parameters: List of parameters to pass to the Python script.
        libraries: List of library specifications (e.g., [{'pypi': {'package': 'pandas==2.0.0'}}]).

    Returns:
        Dict with job submission status and job ID.
    """
    if not DATABRICKS_AVAILABLE:
        return {
            "status": "error",
            "error_message": "Databricks SDK not installed. Install with: pip install databricks-sdk",
        }

    client = _get_databricks_client()
    if not client:
        return {
            "status": "error",
            "error_message": "Databricks client not available. Configure DATABRICKS_HOST and DATABRICKS_TOKEN.",
        }

    try:
        # Use existing_cluster_id if provided, otherwise use cluster_id
        target_cluster_id = existing_cluster_id or cluster_id

        if not target_cluster_id:
            return {
                "status": "error",
                "error_message": "Either cluster_id or existing_cluster_id must be provided",
            }

        # Create Spark Python task
        task = Task(
            task_key="main_task",
            spark_python_task=SparkPythonTask(
                python_file=python_file,
                parameters=parameters or [],
            ),
            existing_cluster_id=target_cluster_id,
            libraries=libraries or [],
        )

        # Create job settings
        job_settings = JobSettings(
            name=job_name,
            tasks=[task],
        )

        # Create job
        job = client.jobs.create(job_settings)

        # Run the job immediately
        run = client.jobs.run_now(job.job_id)

        return {
            "status": "success",
            "message": f"PySpark job '{job_name}' submitted successfully",
            "job_id": job.job_id,
            "run_id": run.run_id,
            "cluster_id": target_cluster_id,
            "python_file": python_file,
        }

    except Exception as e:
        logger.error(f"Error submitting Databricks job: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to submit job: {str(e)}",
        }


@agent_tool
def submit_databricks_notebook_job(
    job_name: str,
    notebook_path: str,
    cluster_id: Optional[str] = None,
    existing_cluster_id: Optional[str] = None,
    base_parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Submit a Databricks notebook job.

    Args:
        job_name: Name for the job.
        notebook_path: Path to notebook in Databricks workspace (e.g., '/Workspace/notebooks/process').
        cluster_id: ID of existing cluster to use (alternative to existing_cluster_id).
        existing_cluster_id: ID of existing cluster (alternative to cluster_id).
        base_parameters: Dictionary of parameters to pass to the notebook.

    Returns:
        Dict with job submission status and job ID.
    """
    if not DATABRICKS_AVAILABLE:
        return {
            "status": "error",
            "error_message": "Databricks SDK not installed. Install with: pip install databricks-sdk",
        }

    client = _get_databricks_client()
    if not client:
        return {
            "status": "error",
            "error_message": "Databricks client not available. Configure DATABRICKS_HOST and DATABRICKS_TOKEN.",
        }

    try:
        target_cluster_id = existing_cluster_id or cluster_id

        if not target_cluster_id:
            return {
                "status": "error",
                "error_message": "Either cluster_id or existing_cluster_id must be provided",
            }

        # Create notebook task
        task = Task(
            task_key="notebook_task",
            notebook_task=NotebookTask(
                notebook_path=notebook_path,
                base_parameters=base_parameters or {},
            ),
            existing_cluster_id=target_cluster_id,
        )

        # Create job settings
        job_settings = JobSettings(
            name=job_name,
            tasks=[task],
        )

        # Create job
        job = client.jobs.create(job_settings)

        # Run the job immediately
        run = client.jobs.run_now(job.job_id)

        return {
            "status": "success",
            "message": f"Notebook job '{job_name}' submitted successfully",
            "job_id": job.job_id,
            "run_id": run.run_id,
            "cluster_id": target_cluster_id,
            "notebook_path": notebook_path,
        }

    except Exception as e:
        logger.error(f"Error submitting Databricks notebook job: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to submit job: {str(e)}",
        }


@agent_tool
def check_databricks_job_status(
    run_id: str,
) -> Dict[str, Any]:
    """Check the status of a Databricks job run.

    Args:
        run_id: ID of the job run to check.

    Returns:
        Dict with job run status and details.
    """
    if not DATABRICKS_AVAILABLE:
        return {
            "status": "error",
            "error_message": "Databricks SDK not installed. Install with: pip install databricks-sdk",
        }

    client = _get_databricks_client()
    if not client:
        return {
            "status": "error",
            "error_message": "Databricks client not available. Configure DATABRICKS_HOST and DATABRICKS_TOKEN.",
        }

    try:
        run = client.jobs.get_run(run_id)

        return {
            "status": "success",
            "run_id": run_id,
            "job_id": run.job_id,
            "state": run.state.life_cycle_state.value if run.state else "UNKNOWN",
            "result_state": run.state.result_state.value if run.state and run.state.result_state else None,
            "state_message": run.state.state_message if run.state else None,
            "start_time": run.start_time.isoformat() if run.start_time else None,
            "end_time": run.end_time.isoformat() if run.end_time else None,
            "setup_duration": run.setup_duration,
            "execution_duration": run.execution_duration,
            "cleanup_duration": run.cleanup_duration,
        }

    except Exception as e:
        logger.error(f"Error checking Databricks job status: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to check job status: {str(e)}",
        }


@agent_tool
def list_databricks_jobs(
    limit: int = 20,
) -> Dict[str, Any]:
    """List Databricks jobs.

    Args:
        limit: Maximum number of jobs to return (default: 20).

    Returns:
        Dict with list of jobs.
    """
    if not DATABRICKS_AVAILABLE:
        return {
            "status": "error",
            "error_message": "Databricks SDK not installed. Install with: pip install databricks-sdk",
        }

    client = _get_databricks_client()
    if not client:
        return {
            "status": "error",
            "error_message": "Databricks client not available. Configure DATABRICKS_HOST and DATABRICKS_TOKEN.",
        }

    try:
        jobs = client.jobs.list(limit=limit)

        job_list = []
        for job in jobs:
            job_info = {
                "job_id": job.job_id,
                "job_name": job.settings.name if job.settings else "Unknown",
                "created_time": job.created_time.isoformat() if job.created_time else None,
            }
            job_list.append(job_info)

        return {
            "status": "success",
            "jobs": job_list,
            "count": len(job_list),
        }

    except Exception as e:
        logger.error(f"Error listing Databricks jobs: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to list jobs: {str(e)}",
        }


@agent_tool
def get_databricks_job_runs(
    job_id: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """Get recent job runs, optionally filtered by job ID.

    Args:
        job_id: Optional job ID to filter runs (if None, returns runs for all jobs).
        limit: Maximum number of runs to return (default: 20).

    Returns:
        Dict with list of job runs.
    """
    if not DATABRICKS_AVAILABLE:
        return {
            "status": "error",
            "error_message": "Databricks SDK not installed. Install with: pip install databricks-sdk",
        }

    client = _get_databricks_client()
    if not client:
        return {
            "status": "error",
            "error_message": "Databricks client not available. Configure DATABRICKS_HOST and DATABRICKS_TOKEN.",
        }

    try:
        if job_id:
            runs = client.jobs.list_runs(job_id=job_id, limit=limit)
        else:
            runs = client.jobs.list_runs(limit=limit)

        run_list = []
        for run in runs:
            run_info = {
                "run_id": run.run_id,
                "job_id": run.job_id,
                "state": run.state.life_cycle_state.value if run.state else "UNKNOWN",
                "result_state": run.state.result_state.value if run.state and run.state.result_state else None,
                "start_time": run.start_time.isoformat() if run.start_time else None,
            }
            run_list.append(run_info)

        return {
            "status": "success",
            "runs": run_list,
            "count": len(run_list),
        }

    except Exception as e:
        logger.error(f"Error getting Databricks job runs: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to get job runs: {str(e)}",
        }

