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

"""This module provides a comprehensive set of tools for interacting with dbt projects.

It includes functionality for running dbt commands, testing, compiling, generating documentation,
managing seeds and snapshots, and various other dbt operations commonly used by data engineers.
"""

import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

from google.adk.tools import agent_tool

logger = logging.getLogger(__name__)


def _run_dbt_command(
    command: List[str],
    project_dir: str,
    profiles_dir: Optional[str] = None,
    vars: Optional[Dict[str, Any]] = None,
    select: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    selector: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute a dbt command with common options.

    Args:
        command: Base dbt command (e.g., ['run', '--models', 'model_name']).
        project_dir: Path to dbt project directory.
        profiles_dir: Path to dbt profiles directory (defaults to project_dir).
        vars: Dictionary of variables to pass to dbt.
        select: List of selectors (e.g., ['model_name', 'tag:staging']).
        exclude: List of resources to exclude.
        selector: Name of a selector from selectors.yml.

    Returns:
        Dict with status, return_code, stdout, and stderr.
    """
    profiles_dir = profiles_dir or project_dir

    cmd = ["dbt"] + command + ["--project-dir", project_dir, "--profiles-dir", profiles_dir]

    if vars:
        vars_json = json.dumps(vars)
        cmd.extend(["--vars", vars_json])

    if select:
        cmd.extend(["--select"] + select)

    if exclude:
        cmd.extend(["--exclude"] + exclude)

    if selector:
        cmd.extend(["--selector", selector])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,  # Don't raise on non-zero exit
        )

        return {
            "status": "success" if result.returncode == 0 else "error",
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd),
        }
    except Exception as e:
        logger.error(f"Error running dbt command: {e}", exc_info=True)
        return {
            "status": "error",
            "return_code": None,
            "stdout": "",
            "stderr": str(e),
            "command": " ".join(cmd),
        }


@agent_tool
def dbt_run(
    project_dir: str,
    models: Optional[List[str]] = None,
    select: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    selector: Optional[str] = None,
    vars: Optional[Dict[str, Any]] = None,
    full_refresh: bool = False,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run dbt models.

    Args:
        project_dir: Path to dbt project directory.
        models: List of model names to run (deprecated, use select instead).
        select: List of selectors (e.g., ['model_name', 'tag:staging']).
        exclude: List of resources to exclude.
        selector: Name of a selector from selectors.yml.
        vars: Dictionary of variables to pass to dbt.
        full_refresh: If True, run with --full-refresh flag.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with execution results.
    """
    command = ["run"]

    if full_refresh:
        command.append("--full-refresh")

    if models:
        command.extend(["--models"] + models)

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        vars=vars,
        select=select,
        exclude=exclude,
        selector=selector,
    )


@agent_tool
def dbt_test(
    project_dir: str,
    select: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    selector: Optional[str] = None,
    vars: Optional[Dict[str, Any]] = None,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run dbt tests (data quality tests).

    Args:
        project_dir: Path to dbt project directory.
        select: List of selectors (e.g., ['model_name', 'tag:staging']).
        exclude: List of resources to exclude.
        selector: Name of a selector from selectors.yml.
        vars: Dictionary of variables to pass to dbt.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with test results.
    """
    command = ["test"]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        vars=vars,
        select=select,
        exclude=exclude,
        selector=selector,
    )


@agent_tool
def dbt_compile(
    project_dir: str,
    select: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    selector: Optional[str] = None,
    vars: Optional[Dict[str, Any]] = None,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Compile dbt project without executing (useful for validation).

    Args:
        project_dir: Path to dbt project directory.
        select: List of selectors.
        exclude: List of resources to exclude.
        selector: Name of a selector from selectors.yml.
        vars: Dictionary of variables to pass to dbt.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with compilation results.
    """
    command = ["compile"]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        vars=vars,
        select=select,
        exclude=exclude,
        selector=selector,
    )


@agent_tool
def dbt_build(
    project_dir: str,
    select: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    selector: Optional[str] = None,
    vars: Optional[Dict[str, Any]] = None,
    full_refresh: bool = False,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run dbt build (runs models and tests in a single operation).

    Args:
        project_dir: Path to dbt project directory.
        select: List of selectors.
        exclude: List of resources to exclude.
        selector: Name of a selector from selectors.yml.
        vars: Dictionary of variables to pass to dbt.
        full_refresh: If True, run with --full-refresh flag.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with build results.
    """
    command = ["build"]

    if full_refresh:
        command.append("--full-refresh")

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        vars=vars,
        select=select,
        exclude=exclude,
        selector=selector,
    )


@agent_tool
def dbt_docs_generate(
    project_dir: str,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate dbt documentation (creates manifest.json and catalog.json).

    Args:
        project_dir: Path to dbt project directory.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with generation results.
    """
    command = ["docs", "generate"]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
    )


@agent_tool
def dbt_docs_serve(
    project_dir: str,
    port: int = 8080,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Serve dbt documentation (starts a local web server).

    Args:
        project_dir: Path to dbt project directory.
        port: Port number for the web server (default: 8080).
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with server information.
    """
    command = ["docs", "serve", "--port", str(port)]

    result = _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
    )

    if result["status"] == "success":
        result["message"] = f"dbt docs server started on http://localhost:{port}"
        result["note"] = "This is a blocking operation. Use dbt_docs_generate to create docs without serving."

    return result


@agent_tool
def dbt_seed(
    project_dir: str,
    select: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    vars: Optional[Dict[str, Any]] = None,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Load seed data from CSV files into the data warehouse.

    Args:
        project_dir: Path to dbt project directory.
        select: List of seed files to load.
        exclude: List of seed files to exclude.
        vars: Dictionary of variables to pass to dbt.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with seed results.
    """
    command = ["seed"]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        vars=vars,
        select=select,
        exclude=exclude,
    )


@agent_tool
def dbt_snapshot(
    project_dir: str,
    select: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    vars: Optional[Dict[str, Any]] = None,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run dbt snapshots (for SCD Type 2 tracking).

    Args:
        project_dir: Path to dbt project directory.
        select: List of snapshots to run.
        exclude: List of snapshots to exclude.
        vars: Dictionary of variables to pass to dbt.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with snapshot results.
    """
    command = ["snapshot"]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        vars=vars,
        select=select,
        exclude=exclude,
    )


@agent_tool
def dbt_ls(
    project_dir: str,
    select: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    selector: Optional[str] = None,
    resource_type: Optional[str] = None,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """List dbt resources (models, tests, seeds, etc.).

    Args:
        project_dir: Path to dbt project directory.
        select: List of selectors.
        exclude: List of resources to exclude.
        selector: Name of a selector from selectors.yml.
        resource_type: Filter by resource type (e.g., 'model', 'test', 'seed').
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with list of resources.
    """
    command = ["ls"]

    if resource_type:
        command.extend(["--resource-type", resource_type])

    result = _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        select=select,
        exclude=exclude,
        selector=selector,
    )

    if result["status"] == "success" and result["stdout"]:
        resources = [line.strip() for line in result["stdout"].split("\n") if line.strip()]
        result["resources"] = resources
        result["count"] = len(resources)

    return result


@agent_tool
def dbt_show(
    project_dir: str,
    select: Optional[List[str]] = None,
    limit: int = 5,
    vars: Optional[Dict[str, Any]] = None,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Preview compiled SQL for models without executing.

    Args:
        project_dir: Path to dbt project directory.
        select: List of models to show (must select exactly one).
        limit: Number of rows to preview (default: 5).
        vars: Dictionary of variables to pass to dbt.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with compiled SQL preview.
    """
    command = ["show", "--limit", str(limit)]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        vars=vars,
        select=select,
    )


@agent_tool
def dbt_debug(
    project_dir: str,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Debug dbt project and profile configuration.

    Args:
        project_dir: Path to dbt project directory.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with debug information.
    """
    command = ["debug"]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
    )


@agent_tool
def dbt_deps(
    project_dir: str,
) -> Dict[str, Any]:
    """Install dbt package dependencies.

    Args:
        project_dir: Path to dbt project directory.

    Returns:
        Dict with installation results.
    """
    command = ["deps"]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
    )


@agent_tool
def dbt_run_operation(
    project_dir: str,
    macro_name: str,
    vars: Optional[Dict[str, Any]] = None,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run a dbt macro as an operation.

    Args:
        project_dir: Path to dbt project directory.
        macro_name: Name of the macro to run (e.g., 'my_macro').
        vars: Dictionary of variables to pass to the macro.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with operation results.
    """
    command = ["run-operation", macro_name]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        vars=vars,
    )


@agent_tool
def dbt_source_freshness(
    project_dir: str,
    select: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    vars: Optional[Dict[str, Any]] = None,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Check source data freshness (when sources were last updated).

    Args:
        project_dir: Path to dbt project directory.
        select: List of sources to check.
        exclude: List of sources to exclude.
        vars: Dictionary of variables to pass to dbt.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with freshness check results.
    """
    command = ["source", "freshness"]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        vars=vars,
        select=select,
        exclude=exclude,
    )


@agent_tool
def dbt_parse(
    project_dir: str,
    profiles_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Parse dbt project and validate syntax.

    Args:
        project_dir: Path to dbt project directory.
        profiles_dir: Path to dbt profiles directory.

    Returns:
        Dict with parse results.
    """
    command = ["parse"]

    return _run_dbt_command(
        command=command,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
    )

