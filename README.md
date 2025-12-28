# 🤖 Data Engineering Copilot

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/david-leadtech/data-engineering-copilot/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

**AI-powered data engineering copilot** that helps you build and manage data pipelines across multiple platforms:

- ✅ **Dataform**: Create, modify, compile, and execute Dataform SQLX pipelines
- ✅ **dbt**: Full dbt project management (run, test, compile, docs, seed, snapshot, etc.)
- ✅ **PySpark/Dataproc**: Submit and manage PySpark jobs on Google Cloud Dataproc
- ✅ **Databricks**: Manage Databricks clusters, submit PySpark jobs, and execute notebooks
- ✅ **BigQuery**: Query, analyze, and optimize BigQuery workloads
- ✅ **GitHub**: Full GitHub integration (branches, PRs, file sync, branch cleanup)

## 📖 Documentation

- **[Quick Start](#-quick-start)** - Get started in 5 minutes
- **[Cursor Integration](CURSOR_INTEGRATION.md)** - Use the agent in Cursor IDE
- **[Releases](RELEASES.md)** - Release management and versioning
- **[Changelog](CHANGELOG.md)** - Version history and changes

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Google Cloud SDK installed and authenticated
- Access to a Google Cloud project with Dataform, BigQuery, and Dataproc APIs enabled
- (Optional) GitHub token for GitHub integration
- (Optional) Databricks credentials for Databricks integration

### 1. Install Dependencies

#### Option A: Using pip (recommended)

```bash
cd data-engineering-copilot
pip install -r requirements.txt
```

#### Option B: Using pip with pyproject.toml

```bash
cd data-engineering-copilot
pip install -e .
```

### 2. Authenticate with Google Cloud

```bash
# Authenticate with Google Cloud
gcloud auth login --update-adc
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable dataform.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable dataproc.googleapis.com
gcloud services enable aiplatform.googleapis.com  # For Vertex AI
```

### 3. Configure Environment Variables

Create a `.env` file in the `data-engineering-copilot` directory:

```bash
# Google Cloud (Required)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1  # or EU, etc.

# Vertex AI (Required if using Vertex AI models)
GOOGLE_GENAI_USE_VERTEXAI=1

# Model Configuration (Optional, defaults to gemini-2.5-pro)
ROOT_AGENT_MODEL=gemini-2.5-pro

# Dataform (Required)
DATAFORM_REPOSITORY_NAME=your-dataform-repository
DATAFORM_WORKSPACE_NAME=your-workspace

# GitHub (Optional but recommended)
# Create a token at: https://github.com/settings/tokens
# Required scope: repo
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO_PATH=your-org/your-repo
GITHUB_DEFAULT_BRANCH=main

# Databricks (Optional)
# Get token from: https://your-workspace.cloud.databricks.com/#setting/account
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your_databricks_token_here
```

### 4. Run the Agent

#### Option A: Using ADK Web Interface (Recommended)

```bash
cd data-engineering-copilot
adk web
```

This will start a web server (usually at `http://localhost:8080`) where you can interact with the agent through a chat interface.

#### Option B: Using ADK CLI

```bash
cd data-engineering-copilot
adk run data_engineering_copilot
```

#### Option C: Programmatic Usage

```python
from data_engineering_copilot.agent import root_agent

# Use the agent in your code
response = root_agent.run("Create a new Dataform source for Apple Ads")
print(response)
```

### 5. Verify Installation

Test that everything is working:

```bash
# Check if ADK is installed
adk --version

# List available agents
adk list

# You should see 'data_engineering_copilot' in the list
```

## 📝 What is the .env file?

The `.env` file is a **local** file (not uploaded to GitHub) where you store your **secrets and configurations**:

- **API Tokens** (GitHub, Google Cloud)
- **Project IDs**
- **Environment-specific configurations**

**Example:**
```bash
# .env (only on your machine, never in GitHub)
GITHUB_TOKEN=ghp_abc123xyz  # Your secret token
GOOGLE_CLOUD_PROJECT=your-project-id
```

## 🔧 Dependencies

Dependencies are the **Python libraries** the code needs to function:

- `google-adk`: Google's Agent Development Kit framework
- `PyGithub`: To interact with GitHub API
- `google-cloud-dataform`: To work with Dataform pipelines
- `google-cloud-bigquery`: To query and analyze BigQuery
- `google-cloud-dataproc`: To manage Dataproc clusters and PySpark jobs
- `databricks-sdk`: To manage Databricks clusters and jobs
- `dbt-core`: To work with dbt projects
- `python-dotenv`: To load environment variables from `.env` file

They are automatically installed with `pip install -r requirements.txt` or `pip install -e .`.

## 📦 Installation Methods

### Method 1: Direct Installation (Quick Start)

```bash
git clone https://github.com/david-leadtech/data-engineering-copilot.git
cd data-engineering-copilot
pip install -r requirements.txt
```

### Method 2: Editable Installation (Development)

```bash
git clone https://github.com/david-leadtech/data-engineering-copilot.git
cd data-engineering-copilot
pip install -e .
```

This allows you to modify the code and have changes reflected immediately.

### Method 3: From PyPI (Future)

Once published:
```bash
pip install data-engineering-copilot
```

## 💡 Usage Examples

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
User: "Execute all PLTV staging tables"

Agent:
1. execute_dataform_by_tags(['pltv', 'staging'])
   - Executes only actions with BOTH 'pltv' AND 'staging' tags
```

**Tag Filtering Logic:**
- Actions must have **ALL** specified tags to be included (AND logic)
- **Tags are project-specific** - they must exist in your Dataform SQLX files
- Each project defines its own tags in the `config { tags: [...] }` block
- `['pltv', 'staging']` → Only actions with both 'pltv' AND 'staging' tags
- `['gold']` → All actions with 'gold' tag
- **Any combination of tags from your specific Dataform project files**

### Example 3: Run dbt models and tests

```
User: "Run all staging models in the dbt project and run tests"

Agent:
1. dbt_run(project_dir='./dbt_project', select=['tag:staging'])
   - Executes all models with 'staging' tag
2. dbt_test(project_dir='./dbt_project', select=['tag:staging'])
   - Runs tests for staging models
```

### Example 4: Generate dbt documentation

```
User: "Generate documentation for the dbt project"

Agent:
1. dbt_docs_generate(project_dir='./dbt_project')
   - Generates manifest.json and catalog.json
   - Creates documentation artifacts
```

### Example 5: Submit PySpark job to Dataproc

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

### Example 6: Create serverless PySpark batch

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

### Example 7: Submit PySpark job to Databricks

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

### Example 8: Execute Databricks notebook

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

### Example 7: Monitor pipeline health

```
User: "Check the health of the PLTV pipeline"

Agent:
1. check_pipeline_health(tags=['pltv'])
   - Analyzes recent workflow executions
   - Calculates success rate, average duration
   - Identifies failure patterns
   - Provides recommendations
```

### Example 10: Analyze query performance

```
User: "Analyze the performance of job abc123"

Agent:
1. analyze_query_performance('abc123')
   - Extracts bytes processed, slot usage, duration
   - Calculates cost estimate
   - Identifies optimization opportunities
   - Suggests improvements
```

### Example 11: Generate pipeline documentation

```
User: "Generate documentation for the pipeline"

Agent:
1. generate_pipeline_documentation()
   - Parses all SQLX files
   - Extracts dependencies, tags, descriptions
   - Generates markdown with dependency graph
   - Creates comprehensive documentation
```

### Example 12: Debug BigQuery memory error (PLTV pipeline)

```
User: "The PLTV pipeline failed with a memory error, job ID abc123"

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

### Example 13: Find and analyze failed jobs

```
User: "Find all failed jobs for ltv_dimensions table in the last 7 days"

Agent:
1. find_failed_bigquery_jobs(
     table_name='ltv_dimensions',
     days=7,
     limit=20
   )
   - Lists all failed jobs with error details
   - Shows error messages, reasons, and locations
2. For each failed job, analyze_bigquery_error(job_id='...')
   - Provides detailed analysis and fix suggestions
```

## 🛠️ Available Tools

### Dataform (15 tools)
- `read_file_from_dataform`: Read SQLX files
- `write_file_to_dataform`: Write/modify files
- `compile_dataform`: Compile pipeline and view DAG
- `search_files_in_dataform`: Search files
- `execute_dataform_workflow`: Execute workflow by name
- `execute_dataform_by_tags`: Execute actions filtered by tags
- `get_workflow_status`: Check workflow execution status
- `read_workflow_settings`: Read workflow configuration
- `monitor_workflow_health`: Monitor workflow execution health over time (success rate, duration, trends)
- `get_failed_workflows`: Get list of failed workflows with error details
- `check_pipeline_health`: Check overall pipeline health status and get recommendations
- `generate_pipeline_documentation`: Automatically generate comprehensive pipeline documentation
- `analyze_assertion_results`: Analyze data quality assertion results from workflow executions
- `check_data_quality_anomalies`: Detect data quality issues and trends over time
- `delete_file_from_dataform`: Delete files from Dataform workspace

### dbt (14 tools)
- `dbt_run`: Execute dbt models (with selectors, tags, or specific models)
- `dbt_test`: Run data quality tests
- `dbt_compile`: Compile dbt project without executing (validation)
- `dbt_build`: Run models and tests in a single operation
- `dbt_docs_generate`: Generate dbt documentation (manifest.json, catalog.json)
- `dbt_docs_serve`: Serve dbt documentation locally
- `dbt_seed`: Load seed data from CSV files
- `dbt_snapshot`: Run snapshots for SCD Type 2 tracking
- `dbt_ls`: List dbt resources (models, tests, seeds, etc.)
- `dbt_show`: Preview compiled SQL without executing
- `dbt_debug`: Debug dbt project and profile configuration
- `dbt_deps`: Install dbt package dependencies
- `dbt_run_operation`: Execute custom dbt macros
- `dbt_source_freshness`: Check when source data was last updated
- `dbt_parse`: Parse and validate dbt project syntax

### PySpark/Dataproc (9 tools)
- `create_dataproc_cluster`: Create a new Dataproc cluster
- `list_dataproc_clusters`: List all clusters in a region
- `get_dataproc_cluster_details`: Get detailed cluster information
- `delete_dataproc_cluster`: Delete a cluster
- `submit_pyspark_job`: Submit PySpark job to a cluster (file must be in GCS)
- `check_dataproc_job_status`: Check job execution status
- `list_dataproc_jobs`: List jobs (optionally filtered by type or cluster)
- `create_dataproc_serverless_batch`: Create serverless PySpark batch (no cluster needed)
- `check_dataproc_serverless_batch_status`: Check serverless batch status

### Databricks (9 tools)
- `create_databricks_cluster`: Create a new Databricks cluster
- `list_databricks_clusters`: List all clusters
- `get_databricks_cluster_status`: Get detailed cluster status and information
- `delete_databricks_cluster`: Delete a cluster
- `submit_databricks_pyspark_job`: Submit PySpark job to a cluster (file must be in Databricks workspace or DBFS)
- `submit_databricks_notebook_job`: Execute a Databricks notebook as a job
- `check_databricks_job_status`: Check job run status and details
- `list_databricks_jobs`: List all jobs
- `get_databricks_job_runs`: Get recent job runs (optionally filtered by job ID)

### BigQuery (9 tools)
- `sample_table_data_tool`: View table data
- `bigquery_toolset`: SQL queries (via ADK BigQuery toolset)
- `analyze_query_performance`: Analyze BigQuery job performance metrics (bytes, slots, cost, duration)
- `get_query_execution_plan`: Get detailed query execution plan with bottleneck identification
- `estimate_query_cost`: Estimate query cost before execution using dry-run
- `check_data_freshness`: Check when tables were last updated and detect stale data
- `analyze_bigquery_error`: **AI-powered error analysis** - Analyze failed BigQuery jobs and get fix suggestions (memory errors, timeouts, permissions, etc.)
- `find_failed_bigquery_jobs`: Find failed jobs by table, error type, or time period (perfect for troubleshooting pipeline failures)
- `suggest_query_optimization`: **AI-powered optimization** - Get specific optimization suggestions based on query structure and error context

### GitHub (11 tools)
- `read_file_from_github`: Read files from GitHub
- `write_file_to_github`: Write files with commit
- `create_github_branch`: Create branches
- `create_github_pull_request`: Create PRs
- `create_github_repository`: Create new GitHub repositories
- `delete_github_branch`: Delete branches (useful after merging PRs)
- `get_merged_pull_requests`: List merged PRs
- `cleanup_merged_branches`: Automatically clean up merged branches
- `sync_dataform_to_github`: Sync Dataform → GitHub
- `list_github_files`: List files in directories
- `get_github_file_history`: View commit history for files

### GCS (4 tools)
- `list_bucket_files_tool`: List files in GCS bucket
- `read_gcs_file_tool`: Read files from GCS
- `validate_bucket_exists_tool`: Check if bucket exists
- `validate_file_exists_tool`: Check if file exists in bucket

**Total: 71 tools** across all platforms

## ✅ Capabilities

### Pipeline Development
- Create and modify SQLX files (tables, views, incremental tables)
- Design multi-stage pipelines with dependencies
- Configure incremental processing, partitioning, assertions
- Compile and validate pipelines
- Execute workflows by name or tags

### dbt Project Management
- Run dbt models with selectors, tags, or specific models
- Execute data quality tests
- Compile and validate dbt projects
- Generate documentation (manifest.json, catalog.json)
- Manage seeds and snapshots
- Check source data freshness
- Execute custom macros
- List and preview resources

### PySpark/Dataproc Operations
- Create and manage Dataproc clusters
- Submit PySpark jobs to clusters
- Create serverless PySpark batches (no cluster management)
- Monitor job and batch execution
- List and filter jobs by type or cluster

### Databricks Operations
- Create and manage Databricks clusters
- Submit PySpark jobs to clusters (files in workspace or DBFS)
- Execute Databricks notebooks as jobs
- Monitor job execution and runs
- List jobs and job runs

### Version Control & Collaboration
- Sync Dataform ↔ GitHub
- Create branches and pull requests
- Manage file history and changes
- Clean up merged branches
- Create new GitHub repositories

### Performance & Monitoring
- Analyze BigQuery query performance and identify optimization opportunities
- Get detailed query execution plans and identify bottlenecks
- Estimate query costs before execution
- Check data freshness and detect stale data
- **AI-powered error analysis**: Automatically analyze failed BigQuery jobs and get fix suggestions
- **Find failed jobs**: Search failed jobs by table, error type, or time period
- **Query optimization suggestions**: Get AI-powered optimization recommendations based on query structure and errors
- Monitor workflow health and track success rates over time
- Identify and troubleshoot failed workflows
- Check overall pipeline health with recommendations
- Analyze data quality assertion results
- Detect data quality anomalies and trends

### Documentation
- Generate comprehensive pipeline documentation with dependency graphs
- Generate dbt documentation (manifest.json, catalog.json)

## ❌ Limitations

The agent **cannot** do the following (these require human judgment, business context, or deep expertise):

- **Design data models and schemas from scratch** (requires business context)
- **Create complex data transformations without examples** (requires deep understanding)
- **Understand business requirements deeply** (requires human judgment)
- **Make architectural decisions** (e.g., when to use incremental vs full refresh - requires experience)
- **Optimize memory usage for complex pipelines** (requires deep analysis)
- **Document business logic and transformations** (requires understanding intent)
- **Make strategic decisions** (requires business knowledge)

The agent is a **powerful assistant** that excels at:
- Executing routine data engineering tasks
- Following patterns and examples
- Managing version control and deployments
- Handling repetitive pipeline modifications
- Automating monitoring and documentation

**Best Use Case:** The agent works best as a **copilot** that handles the mechanical aspects of data engineering, allowing data engineers to focus on design, optimization, and strategic problem-solving.

## 🚀 Releases

This project uses [Semantic Versioning](https://semver.org/). See [RELEASES.md](RELEASES.md) for release management.

**Current Version:** `1.1.0`

**Latest Release:** [v1.0.0](https://github.com/david-leadtech/data-engineering-copilot/releases/latest)

**Changelog:** [CHANGELOG.md](CHANGELOG.md)

### Creating a Release

```bash
# Patch release (1.0.0 -> 1.0.1)
./scripts/release.sh patch

# Minor release (1.0.0 -> 1.1.0)
./scripts/release.sh minor

# Major release (1.0.0 -> 2.0.0)
./scripts/release.sh major
```

See [RELEASES.md](RELEASES.md) for detailed instructions.

## 📚 Additional Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [Dataform Documentation](https://cloud.google.com/dataform/docs)
- [Dataform API Reference](https://cloud.google.com/dataform/docs/reference/rest)
- [Dataform Core Reference](https://cloud.google.com/dataform/docs/reference/dataform-core)
- [dbt Documentation](https://docs.getdbt.com/)
- [Dataproc Documentation](https://cloud.google.com/dataproc/docs)
