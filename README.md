# 🤖 Dataform GitHub Agent

**Independent Project** - AI-powered agent that helps you build and manage Dataform pipelines with **GitHub integration**. This agent can:

- ✅ Create and modify Dataform SQLX files
- ✅ Compile and validate Dataform pipelines
- ✅ **Read/write files directly to GitHub**
- ✅ **Create branches and pull requests**
- ✅ **Sync Dataform workspace with GitHub repository**
- ✅ Query BigQuery tables and schemas
- ✅ **Execute workflows by tags** (e.g., all PLTV pipeline stages)
- ✅ **Clean up merged branches automatically**

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd dataform-github-agent
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in this directory:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=rosseca-nova
GOOGLE_CLOUD_LOCATION=EU

# Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=1

# Model
ROOT_AGENT_MODEL=gemini-2.5-pro

# Dataform
DATAFORM_REPOSITORY_NAME=your-dataform-repository
DATAFORM_WORKSPACE_NAME=your-workspace

# GitHub (Optional but recommended)
# Create a token at: https://github.com/settings/tokens
# Required scope: repo
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO_PATH=leadtechcorp/dataform-pltv-pipeline
GITHUB_DEFAULT_BRANCH=main
```

### 3. Run the Agent

```bash
# With web interface
adk web

# Or from command line
adk run dataform_github_agent
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
GOOGLE_CLOUD_PROJECT=rosseca-nova
```

## 🔧 Dependencies

Dependencies are the **Python libraries** the code needs to function:

- `google-adk`: Google's agent framework
- `PyGithub`: To interact with GitHub
- `google-cloud-dataform`: To work with Dataform
- `google-cloud-bigquery`: To query BigQuery

They are automatically installed with `pip install -r requirements.txt`.

## 💡 Usage Examples

### Example 1: Create a new source and make a PR

```
User: "Create a new source for Apple Ads and make a PR"

Agent:
1. Creates branch: feature/add-apple-ads-source
2. Reads existing file from GitHub
3. Creates/modifies file in Dataform
4. Syncs to GitHub with commit
5. Creates PR automatically
```

### Example 2: Sync Dataform with GitHub

```
User: "Sync all Dataform files to GitHub"

Agent:
1. Lists files in Dataform
2. Reads each file from Dataform
3. Writes each file to GitHub
4. Commits with descriptive message
```

### Example 3: Execute pipeline by specific tags

The agent can execute actions filtered by **any combination of tags from your Dataform project**. Tags are defined in each SQLX file's `config` block and are **project-specific**. Actions must have **ALL** specified tags to be included.

```
User: "Execute all PLTV staging tables"

Agent:
1. execute_dataform_by_tags(['pltv', 'staging'])
   - Executes only actions with BOTH 'pltv' AND 'staging' tags
   
User: "Execute all gold layer tables"

Agent:
1. execute_dataform_by_tags(['gold'])
   - Executes all actions with 'gold' tag

User: "Execute all silver layer tables"

Agent:
1. execute_dataform_by_tags(['silver'])
   - Executes all actions with 'silver' tag

User: "Execute all intermediate PLTV tables"

Agent:
1. execute_dataform_by_tags(['pltv', 'intermediate'])
   - Executes only actions with both 'pltv' AND 'intermediate' tags

User: "Execute all cost-related staging tables"

Agent:
1. execute_dataform_by_tags(['cost', 'staging'])
   - Executes only actions with both 'cost' AND 'staging' tags
   - Works if your project has files with tags: ["silver", "cost", "staging"]
```

### Example 4: Monitor pipeline health

```
User: "Check the health of the PLTV pipeline"

Agent:
1. check_pipeline_health(tags=['pltv'])
   - Analyzes recent workflow executions
   - Calculates success rate, average duration
   - Identifies failure patterns
   - Provides recommendations
```

### Example 5: Analyze query performance

```
User: "Analyze the performance of job abc123"

Agent:
1. analyze_query_performance('abc123')
   - Extracts bytes processed, slot usage, duration
   - Calculates cost estimate
   - Identifies optimization opportunities
   - Suggests improvements
```

### Example 6: Generate pipeline documentation

```
User: "Generate documentation for the pipeline"

Agent:
1. generate_pipeline_documentation()
   - Parses all SQLX files
   - Extracts dependencies, tags, descriptions
   - Generates markdown with dependency graph
   - Creates comprehensive documentation
```

### Example 7: Run dbt models and tests

```
User: "Run all staging models in the dbt project and run tests"

Agent:
1. dbt_run(project_dir='./dbt_project', select=['tag:staging'])
   - Executes all models with 'staging' tag
2. dbt_test(project_dir='./dbt_project', select=['tag:staging'])
   - Runs tests for staging models
```

### Example 8: Generate dbt documentation

```
User: "Generate documentation for the dbt project"

Agent:
1. dbt_docs_generate(project_dir='./dbt_project')
   - Generates manifest.json and catalog.json
   - Creates documentation artifacts
```

### Example 9: Submit PySpark job to Dataproc

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

### Example 10: Create serverless PySpark batch

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

**Tag Filtering Logic:**
- Actions must have **ALL** specified tags to be included (AND logic)
- **Tags are project-specific** - they must exist in your Dataform SQLX files
- Each project defines its own tags in the `config { tags: [...] }` block
- `['pltv', 'staging']` → Only actions with both 'pltv' AND 'staging' tags
- `['gold']` → All actions with 'gold' tag
- `['silver', 'pltv', 'staging']` → Only actions with all three tags
- `['cost']` → All actions with 'cost' tag
- **Any combination of tags from your specific Dataform project files**

## 🛠️ Available Tools

### Dataform
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

### GitHub
- `read_file_from_github`: Read files from GitHub
- `write_file_to_github`: Write files with commit
- `create_github_branch`: Create branches
- `create_github_pull_request`: Create PRs
- `delete_github_branch`: Delete branches (useful after merging PRs)
- `get_merged_pull_requests`: List merged PRs
- `cleanup_merged_branches`: Automatically clean up merged branches
- `sync_dataform_to_github`: Sync Dataform → GitHub
- `list_github_files`: List files in directories
- `get_github_file_history`: View commit history for files

### BigQuery
- `sample_table_data_tool`: View table data
- `bigquery_toolset`: SQL queries
- `analyze_query_performance`: Analyze BigQuery job performance metrics (bytes, slots, cost, duration)
- `get_query_execution_plan`: Get detailed query execution plan with bottleneck identification
- `estimate_query_cost`: Estimate query cost before execution using dry-run
- `check_data_freshness`: Check when tables were last updated and detect stale data

### dbt
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

### PySpark/Dataproc
- `create_dataproc_cluster`: Create a new Dataproc cluster
- `list_dataproc_clusters`: List all clusters in a region
- `get_dataproc_cluster_details`: Get detailed cluster information
- `delete_dataproc_cluster`: Delete a cluster
- `submit_pyspark_job`: Submit PySpark job to a cluster (file must be in GCS)
- `check_dataproc_job_status`: Check job execution status
- `list_dataproc_jobs`: List jobs (optionally filtered by type or cluster)
- `create_dataproc_serverless_batch`: Create serverless PySpark batch (no cluster needed)
- `check_dataproc_serverless_batch_status`: Check serverless batch status

## 🤔 Is This a Complete Data Engineer?

The agent can handle **many data engineering tasks**, but it's not a complete replacement for a data engineer. Here's what it can and cannot do:

### ✅ What the Agent CAN Do (Current Capabilities)

**Pipeline Development:**
- ✅ Create and modify SQLX files (tables, views, incremental tables)
- ✅ Design multi-stage pipelines with dependencies
- ✅ Configure incremental processing, partitioning, assertions
- ✅ Compile and validate pipelines
- ✅ Execute workflows by name or tags

**Version Control & Collaboration:**
- ✅ Sync Dataform ↔ GitHub
- ✅ Create branches and pull requests
- ✅ Manage file history and changes
- ✅ Clean up merged branches

**Data Operations:**
- ✅ Query BigQuery tables and schemas
- ✅ Sample table data
- ✅ Read/write files in Dataform workspace

**dbt Operations:**
- ✅ Run dbt models with selectors, tags, or specific models
- ✅ Execute data quality tests
- ✅ Compile and validate dbt projects
- ✅ Generate documentation
- ✅ Manage seeds and snapshots
- ✅ Check source data freshness
- ✅ Execute custom macros
- ✅ List and preview resources

**PySpark/Dataproc Operations:**
- ✅ Create and manage Dataproc clusters
- ✅ Submit PySpark jobs to clusters
- ✅ Create serverless PySpark batches (no cluster management)
- ✅ Monitor job and batch execution
- ✅ List and filter jobs by type or cluster

**Performance & Monitoring:**
- ✅ Analyze BigQuery query performance and identify optimization opportunities
- ✅ Get detailed query execution plans and identify bottlenecks
- ✅ Estimate query costs before execution
- ✅ Check data freshness and detect stale data
- ✅ Monitor workflow health and track success rates over time
- ✅ Identify and troubleshoot failed workflows
- ✅ Check overall pipeline health with recommendations
- ✅ Analyze data quality assertion results
- ✅ Detect data quality anomalies and trends

### ❌ What the Agent CANNOT Do (Missing Capabilities)

**Performance & Optimization:**
- ✅ Analyze query performance and suggest optimizations
- ✅ Estimate BigQuery costs before execution
- ✅ Analyze query execution plans and identify bottlenecks
- ⚠️ Optimize JOINs, aggregations, or window functions *(Partially - can identify issues, but optimization requires deeper analysis)*
- ⚠️ Recommend partitioning strategies *(Could be added - requires schema analysis)*

**Monitoring & Operations:**
- ✅ Monitor pipeline health and track trends
- ✅ Track data freshness and detect stale data
- ✅ Analyze failure patterns and get recommendations
- ⚠️ Manage retry logic and error handling *(Could be added - workflow configuration)*
- ✅ Monitor BigQuery slot usage and efficiency

**Advanced Data Engineering:**
- ❌ Design data models and schemas from scratch *(Hard - requires business context)*
- ❌ Create complex data transformations without examples *(Hard - requires deep understanding)*
- ❌ Understand business requirements deeply *(Very Hard - requires human judgment)*
- ❌ Make architectural decisions (e.g., when to use incremental vs full refresh) *(Hard - requires experience)*
- ❌ Debug complex data quality issues *(Could be added - requires analysis tools)*
- ❌ Optimize memory usage (like the PLTV pipeline refactoring) *(Hard - requires deep analysis)*

**Documentation & Knowledge:**
- ✅ Generate comprehensive pipeline documentation with dependency graphs
- ⚠️ Create data dictionaries *(Could be added - requires schema analysis)*
- ⚠️ Document business logic and transformations *(Hard - requires understanding intent)*
- ⚠️ Maintain runbooks and troubleshooting guides *(Could be added - template-based)*

### 🎯 Verdict: **Pseudo-Data Engineer**

The agent is a **powerful assistant** that can:
- Execute routine data engineering tasks
- Follow patterns and examples
- Manage version control and deployments
- Handle repetitive pipeline modifications

But it **cannot replace** a data engineer for:
- Strategic decisions
- Performance optimization
- Complex problem-solving
- Business logic understanding
- Architecture design

**Best Use Case:** The agent excels as a **copilot** that handles the mechanical aspects of data engineering, allowing data engineers to focus on design, optimization, and problem-solving.

## 🚧 Future Enhancements

Based on Dataform documentation, we could add support for:

1. **Advanced Assertions**: More complex data quality validations
   - Custom assertion logic
   - Multi-table assertions
   - Conditional assertions

2. **JavaScript Functions**: Reusable macros and functions
   - Create and manage JavaScript functions
   - Use functions in SQLX files
   - Share common logic across files

3. **Workflow Scheduling**: Automatic workflow scheduling
   - Create scheduled workflows programmatically
   - Manage cron-based schedules
   - Configure workflow triggers

4. **Data Quality Tests**: Advanced quality testing
   - Custom test definitions
   - Test result monitoring
   - Automated quality checks

5. **Custom Operations**: Custom operations
   - Define custom SQL operations
   - Manage operation dependencies
   - Execute custom transformations

**Additional Enhancements to Consider:**

**High Value & Feasible (✅ IMPLEMENTED):**
- ✅ Query performance analysis and optimization suggestions
- ✅ Cost estimation before execution
- ✅ Automated monitoring and alerting
- ✅ Pipeline documentation generation
- ✅ Data quality anomaly detection
- ✅ Query execution plan analysis
- ✅ Data freshness tracking

**Medium Value & Feasible (Could Add):**
- ⚠️ Schema analysis and recommendations (requires BigQuery schema API)
- ⚠️ Failure pattern analysis (requires log aggregation)
- ⚠️ Automated retry logic (requires workflow configuration)

**Low Value or Hard to Implement (Maybe Skip):**
- ❌ Business requirement understanding (requires human judgment)
- ❌ Architectural decision-making (requires experience and context)
- ❌ Deep memory optimization (requires complex analysis)
- ❌ Business logic documentation (requires understanding intent)

**Recommendation:** Focus on adding the "High Value & Feasible" features first, as they provide immediate value and are technically achievable using existing APIs.

## 📚 Additional Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [Dataform Documentation](https://cloud.google.com/dataform/docs)
- [Dataform API Reference](https://cloud.google.com/dataform/docs/reference/rest)
- [Dataform Core Reference](https://cloud.google.com/dataform/docs/reference/dataform-core)

