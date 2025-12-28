# Capabilities & Limitations

Complete overview of what the Data Engineering Copilot can and cannot do.

> **← [Back to README](../../README.md)** | **[View All Documentation](../../README.md#-documentation)**

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

## 🎯 Best Use Case

The agent is a **powerful assistant** that excels at:
- Executing routine data engineering tasks
- Following patterns and examples
- Managing version control and deployments
- Handling repetitive pipeline modifications
- Automating monitoring and documentation

**Best Use Case:** The agent works best as a **copilot** that handles the mechanical aspects of data engineering, allowing data engineers to focus on design, optimization, and strategic problem-solving.

## 📊 Tool Inventory

### Dataform (16 tools)
- File operations: read, write, delete, search
- Compilation and validation
- Workflow execution (by name or tags)
- Monitoring and health checks
- Documentation generation
- Data quality analysis

### GitHub (11 tools)
- File operations: read, write, history
- Branch management: create, delete, cleanup
- Pull request creation
- Repository creation
- Dataform ↔ GitHub sync

### BigQuery (6 tools)
- Query performance analysis
- Execution plan analysis
- Cost estimation
- Data freshness tracking
- AI-powered error analysis
- Query optimization suggestions

### dbt (14 tools)
- Model execution (run, test, compile, build)
- Documentation generation
- Seed and snapshot management
- Source freshness checks
- Custom macro execution
- Resource listing and preview

### Dataproc (9 tools)
- Cluster management (create, list, delete)
- PySpark job submission
- Serverless batch creation
- Job monitoring and status

### Databricks (9 tools)
- Cluster management (create, list, delete, status)
- PySpark job submission
- Notebook execution
- Job monitoring and runs

**Total: 65 tools** across all platforms

---

For detailed tool reference, see [TOOLS_REFERENCE.md](./TOOLS_REFERENCE.md)

