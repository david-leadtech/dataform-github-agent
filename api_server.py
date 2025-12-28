#!/usr/bin/env python3
"""
REST API Server for Data Engineering Copilot
Exposes the agent as a FastAPI service for team use

API Structure:
- /agent/run - High-level agent execution (agent decides which tools to use)
- /tools/{category}/{tool_name} - Direct tool execution (specific tool calls)
- /tools/list - List all available tools
"""

import os
import sys
import inspect
from typing import Optional, Any, Dict, List
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Path
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:
    print("ERROR: FastAPI not installed. Install with: pip install fastapi uvicorn", file=sys.stderr)
    sys.exit(1)

from agent import root_agent

# Import all tool modules to expose them
from data_engineering_copilot import (
    # Dataform tools
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
    # GitHub tools
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
    # BigQuery tools
    analyze_query_performance,
    get_query_execution_plan,
    estimate_query_cost,
    check_data_freshness,
    analyze_bigquery_error,
    find_failed_bigquery_jobs,
    suggest_query_optimization,
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
    # Dataproc tools
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
)


# Create FastAPI app
app = FastAPI(
    title="Data Engineering Copilot API",
    description="REST API for the Data Engineering Copilot - AI-powered data engineering agent",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Tool registry - organized by category
TOOL_REGISTRY = {
    "dataform": {
        "compile_dataform": compile_dataform,
        "read_file_from_dataform": read_file_from_dataform,
        "write_file_to_dataform": write_file_to_dataform,
        "delete_file_from_dataform": delete_file_from_dataform,
        "search_files_in_dataform": search_files_in_dataform,
        "execute_dataform_workflow": execute_dataform_workflow,
        "execute_dataform_by_tags": execute_dataform_by_tags,
        "get_dataform_execution_logs": get_dataform_execution_logs,
        "get_dataform_repo_link": get_dataform_repo_link,
        "read_workflow_settings": read_workflow_settings,
        "get_workflow_status": get_workflow_status,
        "monitor_workflow_health": monitor_workflow_health,
        "get_failed_workflows": get_failed_workflows,
        "check_pipeline_health": check_pipeline_health,
        "generate_pipeline_documentation": generate_pipeline_documentation,
        "analyze_assertion_results": analyze_assertion_results,
        "check_data_quality_anomalies": check_data_quality_anomalies,
    },
    "github": {
        "read_file_from_github": read_file_from_github,
        "write_file_to_github": write_file_to_github,
        "create_github_branch": create_github_branch,
        "create_github_pull_request": create_github_pull_request,
        "list_github_files": list_github_files,
        "get_github_file_history": get_github_file_history,
        "sync_dataform_to_github": sync_dataform_to_github,
        "delete_github_branch": delete_github_branch,
        "get_merged_pull_requests": get_merged_pull_requests,
        "cleanup_merged_branches": cleanup_merged_branches,
        "create_github_repository": create_github_repository,
    },
    "bigquery": {
        "analyze_query_performance": analyze_query_performance,
        "get_query_execution_plan": get_query_execution_plan,
        "estimate_query_cost": estimate_query_cost,
        "check_data_freshness": check_data_freshness,
        "analyze_bigquery_error": analyze_bigquery_error,
        "find_failed_bigquery_jobs": find_failed_bigquery_jobs,
        "suggest_query_optimization": suggest_query_optimization,
    },
    "dbt": {
        "dbt_run": dbt_run,
        "dbt_test": dbt_test,
        "dbt_compile": dbt_compile,
        "dbt_build": dbt_build,
        "dbt_docs_generate": dbt_docs_generate,
        "dbt_docs_serve": dbt_docs_serve,
        "dbt_seed": dbt_seed,
        "dbt_snapshot": dbt_snapshot,
        "dbt_ls": dbt_ls,
        "dbt_show": dbt_show,
        "dbt_debug": dbt_debug,
        "dbt_deps": dbt_deps,
        "dbt_run_operation": dbt_run_operation,
        "dbt_source_freshness": dbt_source_freshness,
        "dbt_parse": dbt_parse,
    },
    "dataproc": {
        "create_dataproc_cluster": create_dataproc_cluster,
        "list_dataproc_clusters": list_dataproc_clusters,
        "get_dataproc_cluster_details": get_dataproc_cluster_details,
        "delete_dataproc_cluster": delete_dataproc_cluster,
        "submit_pyspark_job": submit_pyspark_job,
        "check_dataproc_job_status": check_dataproc_job_status,
        "list_dataproc_jobs": list_dataproc_jobs,
        "create_dataproc_serverless_batch": create_dataproc_serverless_batch,
        "check_dataproc_serverless_batch_status": check_dataproc_serverless_batch_status,
    },
    "databricks": {
        "create_databricks_cluster": create_databricks_cluster,
        "list_databricks_clusters": list_databricks_clusters,
        "get_databricks_cluster_status": get_databricks_cluster_status,
        "delete_databricks_cluster": delete_databricks_cluster,
        "submit_databricks_pyspark_job": submit_databricks_pyspark_job,
        "submit_databricks_notebook_job": submit_databricks_notebook_job,
        "check_databricks_job_status": check_databricks_job_status,
        "list_databricks_jobs": list_databricks_jobs,
        "get_databricks_job_runs": get_databricks_job_runs,
    },
}


# Request/Response models
class AgentRequest(BaseModel):
    """Request model for agent tasks."""
    prompt: str = Field(..., description="The task or question for the data engineering copilot")
    async_execution: bool = Field(
        default=False,
        description="If True, returns immediately with a task ID. If False, waits for completion."
    )


class ToolRequest(BaseModel):
    """Request model for direct tool execution."""
    args: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class AgentResponse(BaseModel):
    """Response model for agent tasks."""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    task_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ToolResponse(BaseModel):
    """Response model for tool execution."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    tool_name: str
    category: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ToolInfo(BaseModel):
    """Information about a tool."""
    name: str
    category: str
    description: str
    parameters: Dict[str, Any]


# In-memory task storage (for async execution)
task_store: dict[str, dict] = {}


def get_tool_info(func) -> Dict[str, Any]:
    """Extract tool information from function signature and docstring."""
    sig = inspect.signature(func)
    params = {}
    for param_name, param in sig.parameters.items():
        params[param_name] = {
            "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
            "default": param.default if param.default != inspect.Parameter.empty else None,
            "required": param.default == inspect.Parameter.empty
        }
    
    return {
        "parameters": params,
        "description": func.__doc__ or "No description available"
    }


# ============================================================================
# High-Level Agent Endpoints
# ============================================================================

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Data Engineering Copilot API",
        "version": "1.1.0",
        "description": "REST API for AI-powered data engineering agent",
        "endpoints": {
            "health": "/health",
            "agent": {
                "run": "/agent/run",
                "status": "/agent/status/{task_id}"
            },
            "tools": {
                "list": "/tools/list",
                "list_by_category": "/tools/list/{category}",
                "execute": "/tools/{category}/{tool_name}",
                "info": "/tools/{category}/{tool_name}/info"
            },
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.1.0"
    )


@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest, background_tasks: BackgroundTasks):
    """
    Run a data engineering task using the AI agent.
    
    The agent intelligently decides which tools to use based on your prompt.
    This is the recommended endpoint for high-level tasks.
    
    Examples:
    - "Create a new Dataform source for Apple Ads"
    - "Debug the data pipeline and find failed jobs"
    - "Check the health of all pipelines"
    - "Create a PR with the new staging table"
    """
    try:
        if request.async_execution:
            import uuid
            task_id = str(uuid.uuid4())
            
            task_store[task_id] = {
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "prompt": request.prompt
            }
            
            background_tasks.add_task(execute_agent_task, task_id, request.prompt)
            
            return AgentResponse(
                success=True,
                task_id=task_id,
                response=None
            )
        else:
            response = root_agent.run(request.prompt)
            
            return AgentResponse(
                success=True,
                response=str(response)
            )
    except Exception as e:
        return AgentResponse(
            success=False,
            error=str(e)
        )


@app.get("/agent/status/{task_id}", response_model=AgentResponse)
async def get_task_status(task_id: str):
    """Get the status of an async agent task."""
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_store[task_id]
    
    if task["status"] == "completed":
        return AgentResponse(
            success=True,
            response=task.get("response"),
            task_id=task_id
        )
    elif task["status"] == "failed":
        return AgentResponse(
            success=False,
            error=task.get("error"),
            task_id=task_id
        )
    else:
        return AgentResponse(
            success=True,
            response=f"Task is {task['status']}",
            task_id=task_id
        )


# ============================================================================
# Direct Tool Execution Endpoints
# ============================================================================

@app.get("/tools/list", response_model=Dict[str, List[str]])
async def list_all_tools():
    """List all available tools organized by category."""
    return {
        category: list(tools.keys())
        for category, tools in TOOL_REGISTRY.items()
    }


@app.get("/tools/list/{category}", response_model=List[str])
async def list_tools_by_category(category: str = Path(..., description="Tool category")):
    """List all tools in a specific category."""
    if category not in TOOL_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category}' not found. Available categories: {list(TOOL_REGISTRY.keys())}"
        )
    
    return list(TOOL_REGISTRY[category].keys())


@app.get("/tools/{category}/{tool_name}/info", response_model=ToolInfo)
async def get_tool_info(
    category: str = Path(..., description="Tool category"),
    tool_name: str = Path(..., description="Tool name")
):
    """Get detailed information about a specific tool."""
    if category not in TOOL_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category}' not found"
        )
    
    if tool_name not in TOOL_REGISTRY[category]:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found in category '{category}'"
        )
    
    tool_func = TOOL_REGISTRY[category][tool_name]
    info = get_tool_info(tool_func)
    
    return ToolInfo(
        name=tool_name,
        category=category,
        description=info["description"],
        parameters=info["parameters"]
    )


@app.post("/tools/{category}/{tool_name}", response_model=ToolResponse)
async def execute_tool(
    category: str = Path(..., description="Tool category"),
    tool_name: str = Path(..., description="Tool name"),
    request: ToolRequest = ToolRequest()
):
    """
    Execute a specific tool directly.
    
    This endpoint allows you to call tools directly without going through the agent.
    Useful for automation, testing, or when you know exactly which tool to use.
    
    Example:
    POST /tools/dataform/compile_dataform
    Body: {}
    
    POST /tools/github/create_github_branch
    Body: {"args": {"branch_name": "feature/new-table", "base_branch": "main"}}
    """
    if category not in TOOL_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category}' not found. Available: {list(TOOL_REGISTRY.keys())}"
        )
    
    if tool_name not in TOOL_REGISTRY[category]:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found in category '{category}'. "
                   f"Available tools: {list(TOOL_REGISTRY[category].keys())}"
        )
    
    tool_func = TOOL_REGISTRY[category][tool_name]
    
    try:
        # Call the tool with provided arguments
        result = tool_func(**request.args)
        
        return ToolResponse(
            success=True,
            result=result,
            tool_name=tool_name,
            category=category
        )
    except TypeError as e:
        # Handle missing required arguments
        return ToolResponse(
            success=False,
            error=f"Invalid arguments: {str(e)}. Check /tools/{category}/{tool_name}/info for required parameters.",
            tool_name=tool_name,
            category=category
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            error=str(e),
            tool_name=tool_name,
            category=category
        )


# ============================================================================
# Background Tasks
# ============================================================================

async def execute_agent_task(task_id: str, prompt: str):
    """Execute agent task in background."""
    try:
        task_store[task_id]["status"] = "running"
        response = root_agent.run(prompt)
        task_store[task_id]["status"] = "completed"
        task_store[task_id]["response"] = str(response)
        task_store[task_id]["completed_at"] = datetime.utcnow().isoformat()
    except Exception as e:
        task_store[task_id]["status"] = "failed"
        task_store[task_id]["error"] = str(e)
        task_store[task_id]["failed_at"] = datetime.utcnow().isoformat()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"🚀 Starting Data Engineering Copilot API server...")
    print(f"📖 API docs: http://localhost:{port}/docs")
    print(f"🔍 Health check: http://localhost:{port}/health")
    print(f"🎯 Agent endpoint: POST http://localhost:{port}/agent/run")
    print(f"🔧 Tools endpoint: POST http://localhost:{port}/tools/{{category}}/{{tool_name}}")
    print(f"📋 List tools: GET http://localhost:{port}/tools/list")
    print()
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
