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

"""This module provides tools for managing Google Cloud Dataproc clusters and PySpark jobs.

It includes functionality for cluster management, job submission, monitoring, and serverless batches.
Useful for running PySpark workloads on Dataproc (similar to Databricks).
"""

import logging
from typing import Any, Dict, List, Optional

from google.api_core.exceptions import GoogleAPICallError, NotFound
from google.cloud import dataproc_v1 as dataproc
from google.cloud.dataproc_v1 import (
    BatchControllerClient,
    ClusterControllerClient,
    JobControllerClient,
)
from google.cloud.dataproc_v1.types import (
    Batch,
    Cluster,
    ClusterConfig,
    CreateBatchRequest,
    DiskConfig,
    EnvironmentConfig,
    ExecutionConfig,
    GceClusterConfig,
    InstanceGroupConfig,
    Job,
    JobPlacement,
    PeripheralsConfig,
    PySparkBatch,
    PySparkJob,
    RuntimeConfig,
    SparkBatch,
    SparkHistoryServerConfig,
    SparkJob,
)
from google.adk.tools import agent_tool

import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

logger = logging.getLogger(__name__)


def _get_cluster_client(region: Optional[str] = None) -> ClusterControllerClient:
    """Get a Dataproc ClusterControllerClient for a specific region."""
    region = region or config.location
    return ClusterControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )


def _get_job_client(region: Optional[str] = None) -> JobControllerClient:
    """Get a Dataproc JobControllerClient for a specific region."""
    region = region or config.location
    return JobControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )


def _get_batch_client(region: Optional[str] = None) -> BatchControllerClient:
    """Get a Dataproc BatchControllerClient for a specific region."""
    region = region or config.location
    return BatchControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )


# ==================== CLUSTER MANAGEMENT ====================


@agent_tool
def create_dataproc_cluster(
    cluster_name: str,
    region: Optional[str] = None,
    num_workers: int = 2,
    machine_type_master: str = "n1-standard-4",
    machine_type_worker: str = "n1-standard-4",
    boot_disk_size_gb: int = 100,
    pip_packages: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a new Dataproc cluster.

    Args:
        cluster_name: Name of the cluster to create.
        region: GCP region (defaults to config.location).
        num_workers: Number of worker nodes (default: 2).
        machine_type_master: Machine type for master node (default: n1-standard-4).
        machine_type_worker: Machine type for worker nodes (default: n1-standard-4).
        boot_disk_size_gb: Boot disk size in GB (default: 100).
        pip_packages: List of pip packages to install (e.g., ['pandas==2.0.0', 'numpy']).

    Returns:
        Dict with cluster creation status.
    """
    try:
        region = region or config.location
        cluster_client = _get_cluster_client(region)

        # Master node configuration
        master_config = InstanceGroupConfig(
            num_instances=1,
            machine_type_uri=machine_type_master,
            disk_config=DiskConfig(boot_disk_size_gb=boot_disk_size_gb),
        )

        # Worker node configuration
        worker_config = InstanceGroupConfig(
            num_instances=num_workers,
            machine_type_uri=machine_type_worker,
            disk_config=DiskConfig(boot_disk_size_gb=boot_disk_size_gb),
        )

        # GCE cluster configuration
        gce_cluster_config = GceClusterConfig(
            service_account_scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        # Software configuration
        software_properties = {}
        if pip_packages:
            software_properties["dataproc:pip.packages"] = ",".join(pip_packages)

        software_config = dataproc.SoftwareConfig(
            image_version="2.1-debian11", properties=software_properties
        )

        # Construct cluster configuration
        cluster = Cluster(
            project_id=config.project_id,
            cluster_name=cluster_name,
            labels={"created_by": "dataform_github_agent"},
            config=ClusterConfig(
                gce_cluster_config=gce_cluster_config,
                master_config=master_config,
                worker_config=worker_config,
                software_config=software_config,
            ),
        )

        # Create the cluster
        operation = cluster_client.create_cluster(
            request={
                "project_id": config.project_id,
                "region": region,
                "cluster": cluster,
            }
        )

        return {
            "status": "success",
            "message": f"Cluster '{cluster_name}' creation initiated in region '{region}'",
            "cluster_name": cluster_name,
            "operation_name": operation.operation.name if hasattr(operation, 'operation') else None,
            "note": "Cluster creation may take several minutes. Use list_dataproc_clusters to check status.",
        }

    except GoogleAPICallError as e:
        logger.error(f"Error creating Dataproc cluster: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to create cluster: {e.message}",
        }
    except Exception as e:
        logger.error(f"Unexpected error creating cluster: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
        }


@agent_tool
def list_dataproc_clusters(
    region: Optional[str] = None,
) -> Dict[str, Any]:
    """List all Dataproc clusters in a region.

    Args:
        region: GCP region (defaults to config.location).

    Returns:
        Dict with list of clusters and their status.
    """
    try:
        region = region or config.location
        cluster_client = _get_cluster_client(region)

        clusters = cluster_client.list_clusters(
            project_id=config.project_id, region=region
        )

        cluster_list = []
        for cluster in clusters:
            cluster_info = {
                "cluster_name": cluster.cluster_name,
                "status": cluster.status.state.name if cluster.status else "UNKNOWN",
                "num_workers": cluster.config.worker_config.num_instances if cluster.config.worker_config else 0,
                "region": region,
            }
            cluster_list.append(cluster_info)

        return {
            "status": "success",
            "clusters": cluster_list,
            "count": len(cluster_list),
        }

    except GoogleAPICallError as e:
        logger.error(f"Error listing clusters: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to list clusters: {e.message}",
        }
    except Exception as e:
        logger.error(f"Unexpected error listing clusters: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
        }


@agent_tool
def get_dataproc_cluster_details(
    cluster_name: str,
    region: Optional[str] = None,
) -> Dict[str, Any]:
    """Get detailed information about a Dataproc cluster.

    Args:
        cluster_name: Name of the cluster.
        region: GCP region (defaults to config.location).

    Returns:
        Dict with cluster details.
    """
    try:
        region = region or config.location
        cluster_client = _get_cluster_client(region)

        cluster = cluster_client.get_cluster(
            project_id=config.project_id,
            region=region,
            cluster_name=cluster_name,
        )

        return {
            "status": "success",
            "cluster_name": cluster.cluster_name,
            "status": cluster.status.state.name if cluster.status else "UNKNOWN",
            "num_workers": cluster.config.worker_config.num_instances if cluster.config.worker_config else 0,
            "master_machine_type": cluster.config.master_config.machine_type_uri if cluster.config.master_config else None,
            "worker_machine_type": cluster.config.worker_config.machine_type_uri if cluster.config.worker_config else None,
            "region": region,
        }

    except NotFound:
        return {
            "status": "error",
            "error_message": f"Cluster '{cluster_name}' not found in region '{region}'",
        }
    except GoogleAPICallError as e:
        logger.error(f"Error getting cluster details: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to get cluster details: {e.message}",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
        }


@agent_tool
def delete_dataproc_cluster(
    cluster_name: str,
    region: Optional[str] = None,
) -> Dict[str, Any]:
    """Delete a Dataproc cluster.

    Args:
        cluster_name: Name of the cluster to delete.
        region: GCP region (defaults to config.location).

    Returns:
        Dict with deletion status.
    """
    try:
        region = region or config.location
        cluster_client = _get_cluster_client(region)

        operation = cluster_client.delete_cluster(
            project_id=config.project_id,
            region=region,
            cluster_name=cluster_name,
        )

        return {
            "status": "success",
            "message": f"Cluster '{cluster_name}' deletion initiated",
            "cluster_name": cluster_name,
            "note": "Cluster deletion may take several minutes.",
        }

    except NotFound:
        return {
            "status": "error",
            "error_message": f"Cluster '{cluster_name}' not found",
        }
    except GoogleAPICallError as e:
        logger.error(f"Error deleting cluster: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to delete cluster: {e.message}",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
        }


# ==================== PYSPARK JOB MANAGEMENT ====================


@agent_tool
def submit_pyspark_job(
    cluster_name: str,
    main_python_file_uri: str,
    args: Optional[List[str]] = None,
    region: Optional[str] = None,
    py_files: Optional[List[str]] = None,
    jars: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Submit a PySpark job to a Dataproc cluster.

    Args:
        cluster_name: Name of the Dataproc cluster.
        main_python_file_uri: GCS URI of the main Python file (e.g., 'gs://bucket/script.py').
        args: List of arguments to pass to the job.
        region: GCP region (defaults to config.location).
        py_files: List of additional Python files to include (GCS URIs).
        jars: List of JAR files to include (GCS URIs).

    Returns:
        Dict with job submission status and job ID.
    """
    try:
        region = region or config.location
        job_client = _get_job_client(region)

        # Define PySpark job configuration
        pyspark_job = PySparkJob(
            main_python_file_uri=main_python_file_uri,
            args=args or [],
            python_file_uris=py_files or [],
            jar_file_uris=jars or [],
        )

        # Define job placement
        placement = JobPlacement(cluster_name=cluster_name)

        # Construct job object
        job = Job(
            placement=placement,
            pyspark_job=pyspark_job,
            labels={"submitted_by": "dataform_github_agent"},
        )

        # Submit the job
        submitted_job = job_client.submit_job(
            project_id=config.project_id, region=region, job=job
        )

        job_id = submitted_job.reference.job_id

        return {
            "status": "success",
            "message": f"PySpark job submitted successfully",
            "job_id": job_id,
            "cluster_name": cluster_name,
            "main_file": main_python_file_uri,
        }

    except GoogleAPICallError as e:
        logger.error(f"Error submitting PySpark job: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to submit job: {e.message}",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
        }


@agent_tool
def check_dataproc_job_status(
    job_id: str,
    region: Optional[str] = None,
) -> Dict[str, Any]:
    """Check the status of a Dataproc job.

    Args:
        job_id: ID of the job to check.
        region: GCP region (defaults to config.location).

    Returns:
        Dict with job status information.
    """
    try:
        region = region or config.location
        job_client = _get_job_client(region)

        job = job_client.get_job(
            project_id=config.project_id, region=region, job_id=job_id
        )

        job_type = "Unknown"
        if job.pyspark_job:
            job_type = "PySpark"
        elif job.spark_job:
            job_type = "Spark"
        elif job.hadoop_job:
            job_type = "Hadoop"
        elif job.spark_sql_job:
            job_type = "Spark SQL"

        return {
            "status": "success",
            "job_id": job_id,
            "job_type": job_type,
            "state": job.status.state.name if job.status else "UNKNOWN",
            "state_message": job.status.details if job.status and job.status.details else None,
            "cluster_name": job.placement.cluster_name if job.placement else None,
        }

    except NotFound:
        return {
            "status": "error",
            "error_message": f"Job '{job_id}' not found",
        }
    except GoogleAPICallError as e:
        logger.error(f"Error checking job status: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to check job status: {e.message}",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
        }


@agent_tool
def list_dataproc_jobs(
    region: Optional[str] = None,
    job_type: Optional[str] = None,
    cluster_name: Optional[str] = None,
) -> Dict[str, Any]:
    """List Dataproc jobs, optionally filtered by type or cluster.

    Args:
        region: GCP region (defaults to config.location).
        job_type: Filter by job type ('PySpark', 'Spark', 'Hadoop', 'Spark SQL').
        cluster_name: Filter by cluster name.

    Returns:
        Dict with list of jobs.
    """
    try:
        region = region or config.location
        job_client = _get_job_client(region)

        jobs = job_client.list_jobs(project_id=config.project_id, region=region)

        job_list = []
        for job in jobs:
            # Determine job type
            job_type_detected = "Unknown"
            if job.pyspark_job:
                job_type_detected = "PySpark"
            elif job.spark_job:
                job_type_detected = "Spark"
            elif job.hadoop_job:
                job_type_detected = "Hadoop"
            elif job.spark_sql_job:
                job_type_detected = "Spark SQL"

            # Apply filters
            if job_type and job_type_detected != job_type:
                continue
            if cluster_name and job.placement.cluster_name != cluster_name:
                continue

            job_info = {
                "job_id": job.reference.job_id,
                "job_type": job_type_detected,
                "state": job.status.state.name if job.status else "UNKNOWN",
                "cluster_name": job.placement.cluster_name if job.placement else None,
            }
            job_list.append(job_info)

        return {
            "status": "success",
            "jobs": job_list,
            "count": len(job_list),
        }

    except GoogleAPICallError as e:
        logger.error(f"Error listing jobs: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to list jobs: {e.message}",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
        }


# ==================== SERVERLESS BATCHES ====================


@agent_tool
def create_dataproc_serverless_batch(
    batch_id: str,
    main_python_file_uri: str,
    args: Optional[List[str]] = None,
    region: Optional[str] = None,
    runtime_version: str = "1.1",
    service_account: Optional[str] = None,
    py_files: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a Dataproc Serverless batch job (no cluster management needed).

    Args:
        batch_id: Unique identifier for the batch job.
        main_python_file_uri: GCS URI of the main Python file.
        args: List of arguments to pass to the job.
        region: GCP region (defaults to config.location).
        runtime_version: Dataproc runtime version (default: '1.1').
        service_account: Service account to use (optional).
        py_files: List of additional Python files (GCS URIs).

    Returns:
        Dict with batch creation status.
    """
    try:
        region = region or config.location
        batch_client = _get_batch_client(region)

        # PySpark batch configuration
        pyspark_batch = PySparkBatch(
            main_python_file_uri=main_python_file_uri,
            args=args or [],
            python_file_uris=py_files or [],
        )

        # Runtime configuration
        runtime_config = RuntimeConfig(version=runtime_version)

        # Execution configuration
        execution_config = None
        if service_account:
            execution_config = ExecutionConfig(service_account=service_account)

        environment_config = EnvironmentConfig()
        if execution_config:
            environment_config.execution_config = execution_config

        # Create batch
        batch = Batch(
            pyspark_batch=pyspark_batch,
            labels={"created_by": "dataform_github_agent"},
            environment_config=environment_config,
            runtime_config=runtime_config,
        )

        parent = f"projects/{config.project_id}/locations/{region}"
        request = CreateBatchRequest(parent=parent, batch_id=batch_id, batch=batch)

        batch_client.create_batch(request=request)

        return {
            "status": "success",
            "message": f"Serverless batch '{batch_id}' created successfully",
            "batch_id": batch_id,
            "main_file": main_python_file_uri,
        }

    except GoogleAPICallError as e:
        logger.error(f"Error creating serverless batch: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to create batch: {e.message}",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
        }


@agent_tool
def check_dataproc_serverless_batch_status(
    batch_id: str,
    region: Optional[str] = None,
) -> Dict[str, Any]:
    """Check the status of a Dataproc Serverless batch job.

    Args:
        batch_id: ID of the batch job.
        region: GCP region (defaults to config.location).

    Returns:
        Dict with batch status information.
    """
    try:
        region = region or config.location
        batch_client = _get_batch_client(region)

        batch_name = f"projects/{config.project_id}/locations/{region}/batches/{batch_id}"
        batch = batch_client.get_batch(name=batch_name)

        return {
            "status": "success",
            "batch_id": batch_id,
            "state": batch.state.name if batch.state else "UNKNOWN",
            "state_message": batch.state_message if hasattr(batch, 'state_message') else None,
        }

    except NotFound:
        return {
            "status": "error",
            "error_message": f"Batch '{batch_id}' not found",
        }
    except GoogleAPICallError as e:
        logger.error(f"Error checking batch status: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Failed to check batch status: {e.message}",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
        }

