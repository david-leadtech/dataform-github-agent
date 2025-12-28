# Data Engineering Copilot - MCP Server Documentation

Complete guide for using the Data Engineering Copilot as an MCP (Model Context Protocol) server in Cursor.

> **← [Back to README](../../README.md)** | **[View All Documentation](../../README.md#-documentation)**

## 📋 Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Available Tools](#available-tools)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

---

## What is MCP?

**Model Context Protocol (MCP)** is a protocol that allows AI assistants (like Cursor's AI) to interact with external tools and services. By configuring the Data Engineering Copilot as an MCP server, Cursor's AI can directly call the copilot's tools.

### Benefits

- ✅ **Direct Integration**: Cursor's AI can use the copilot without you writing code
- ✅ **Natural Language**: Just ask Cursor to use the copilot
- ✅ **No API Calls**: Works locally, no HTTP requests needed
- ✅ **Seamless**: Feels like a native Cursor feature

---

## Quick Start

### 1. Install Dependencies

```bash
cd analytics/adk-agents-reference/data-engineering-copilot
pip install -r requirements.txt
```

### 2. Get the Absolute Path

```bash
# Run this to get the full path
pwd
# Example output: /Users/davidsanchezcamacho/Leadtech-Cursor/analytics/adk-agents-reference/data-engineering-copilot
```

### 3. Configure Cursor

**Option A: Via Cursor Settings UI**
1. Open Cursor Settings (`Cmd+,` or `Ctrl+,`)
2. Search for "MCP"
3. Click "Edit MCP Settings" or "Add MCP Server"
4. Add the configuration (see below)

**Option B: Edit Config File Directly**
1. Open `~/.cursor/mcp.json` (create if it doesn't exist)
2. Add the configuration:

```json
{
  "mcpServers": {
    "data-engineering-copilot": {
      "command": "python",
      "args": [
        "/Users/davidsanchezcamacho/Leadtech-Cursor/analytics/adk-agents-reference/data-engineering-copilot/mcp_server.py"
      ],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "your-project-id",
        "DATAFORM_REPOSITORY_NAME": "your-repo",
        "DATAFORM_WORKSPACE_NAME": "your-workspace",
        "GITHUB_TOKEN": "ghp_your_token",
        "GITHUB_REPO_PATH": "your-org/your-repo"
      }
    }
  }
}
```

**Replace the path** with your actual absolute path from step 2.

### 4. Restart Cursor

Close and reopen Cursor completely.

### 5. Test It

In Cursor, ask:
```
Use the data engineering copilot to check the health of the data pipeline
```

---

## Installation

### Prerequisites

- Python 3.8+
- Cursor IDE
- Google Cloud credentials configured
- (Optional) GitHub token for GitHub tools
- (Optional) Databricks token for Databricks tools

### Step-by-Step Installation

1. **Clone/Navigate to the agent directory:**
   ```bash
   cd analytics/adk-agents-reference/data-engineering-copilot
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python -c "from agent import root_agent; print('✅ Agent installed')"
   python -c "import mcp; print('✅ MCP SDK installed')"
   ```

4. **Test the MCP server:**
   ```bash
   python mcp_server.py
   ```
   (This will start the server - you can Ctrl+C to stop it)

---

## Configuration

### Basic Configuration

Minimum configuration in `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "data-engineering-copilot": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

### Full Configuration with Environment Variables

```json
{
  "mcpServers": {
    "data-engineering-copilot": {
      "command": "python",
      "args": [
        "/Users/davidsanchezcamacho/Leadtech-Cursor/analytics/adk-agents-reference/data-engineering-copilot/mcp_server.py"
      ],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "your-project-id",
        "GOOGLE_CLOUD_LOCATION": "us-central1",
        "DATAFORM_REPOSITORY_NAME": "your-repo",
        "DATAFORM_WORKSPACE_NAME": "your-workspace",
        "GOOGLE_GENAI_USE_VERTEXAI": "1",
        "ROOT_AGENT_MODEL": "gemini-2.5-pro",
        "GITHUB_TOKEN": "ghp_your_token_here",
        "GITHUB_REPO_PATH": "your-org/your-repo",
        "GITHUB_DEFAULT_BRANCH": "main",
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your_databricks_token"
      }
    }
  }
}
```

### Using .env File (Alternative)

Instead of setting environment variables in the MCP config, you can use a `.env` file:

1. Create `.env` in the agent directory:
   ```bash
   GOOGLE_CLOUD_PROJECT=your-project-id
   DATAFORM_REPOSITORY_NAME=your-repo
   GITHUB_TOKEN=ghp_your_token
   # ... etc
   ```

2. The agent will automatically load it (via `python-dotenv`)

### Configuration File Locations

- **macOS/Linux**: `~/.cursor/mcp.json`
- **Windows**: `C:\Users\[YourUsername]\.cursor\mcp.json`

---

## Usage Examples

### Example 1: Create a Dataform Source

**In Cursor chat:**
```
Use the data engineering copilot to create a new Dataform source for Apple Ads
```

**What happens:**
1. Cursor calls the MCP tool `run_agent_task`
2. The copilot creates the source file
3. Returns confirmation

### Example 2: Debug a Pipeline

**In Cursor chat:**
```
Use the data engineering copilot to debug the data pipeline and find any failed jobs
```

**What happens:**
1. Copilot checks pipeline health
2. Finds failed BigQuery jobs
3. Analyzes errors
4. Returns detailed report

### Example 3: Create a GitHub PR

**In Cursor chat:**
```
Use the data engineering copilot to create a branch, add a new staging table, and create a PR
```

**What happens:**
1. Creates GitHub branch
2. Writes new SQLX file
3. Creates pull request
4. Returns PR link

### Example 4: Check Pipeline Health

**In Cursor chat:**
```
Use the data engineering copilot to check the health of all staging pipelines
```

**What happens:**
1. Monitors workflow health
2. Checks data freshness
3. Analyzes assertion results
4. Returns health report

### Example 5: Optimize a Query

**In Cursor chat:**
```
Use the data engineering copilot to analyze and optimize this BigQuery job: bqjob_abc123
```

**What happens:**
1. Analyzes query performance
2. Gets execution plan
3. Suggests optimizations
4. Returns recommendations

---

## Available Tools

The MCP server currently exposes **1 high-level tool** that gives access to all 65+ underlying tools:

### `run_agent_task`

**Description:**
Run a data engineering task using the Data Engineering Copilot. The agent intelligently decides which tools to use based on your prompt.

**Parameters:**
- `prompt` (string, required): The task or question for the data engineering copilot

**Example Prompts:**
- "Create a new Dataform source for Apple Ads"
- "Debug the data pipeline and find failed jobs"
- "Check the health of all pipelines"
- "Create a PR with the new staging table"
- "Run dbt models for staging layer"
- "Submit a PySpark job to Dataproc"
- "Analyze BigQuery query performance for job abc123"

**What the Agent Can Do:**
- **Dataform**: Create/modify SQLX files, execute workflows, monitor pipelines
- **GitHub**: Create branches, PRs, sync files
- **BigQuery**: Query, analyze performance, estimate costs
- **dbt**: Run models, tests, generate docs
- **Dataproc**: Submit PySpark jobs, manage clusters
- **Databricks**: Submit jobs, manage clusters, execute notebooks

---

## Troubleshooting

### Problem: "MCP SDK not installed"

**Solution:**
```bash
pip install mcp
```

### Problem: "Agent not found" or Import Error

**Solution:**
```bash
cd analytics/adk-agents-reference/data-engineering-copilot
pip install -e .
```

### Problem: "Command not found: python"

**Solution:**
Use full path to Python:
```json
{
  "mcpServers": {
    "data-engineering-copilot": {
      "command": "/usr/bin/python3",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

Or use `python3`:
```json
{
  "command": "python3",
  "args": ["/absolute/path/to/mcp_server.py"]
}
```

### Problem: "Permission denied"

**Solution:**
Make the script executable:
```bash
chmod +x mcp_server.py
```

### Problem: MCP Server Not Appearing in Cursor

**Checklist:**
1. ✅ Config file is valid JSON (check for syntax errors)
2. ✅ Path is absolute (not relative)
3. ✅ Python path is correct
4. ✅ Cursor was restarted after config change
5. ✅ Check Cursor's MCP logs (Settings → MCP → View Logs)

### Problem: "Environment variable not set"

**Solution:**
Either:
1. Add to MCP config `env` section (see Configuration above)
2. Or create `.env` file in agent directory
3. Or set in your shell before starting Cursor

### Problem: "Google Cloud authentication failed"

**Solution:**
```bash
gcloud auth application-default login
```

### Problem: Tool Returns Error

**Check:**
1. Are required environment variables set?
2. Are credentials configured?
3. Check the error message - it usually tells you what's missing

---

## Advanced Configuration

### Using Virtual Environment

If you're using a virtual environment:

```json
{
  "mcpServers": {
    "data-engineering-copilot": {
      "command": "/path/to/venv/bin/python",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

### Using Different Python Version

```json
{
  "mcpServers": {
    "data-engineering-copilot": {
      "command": "python3.11",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

### Debugging MCP Server

1. **Test the server manually:**
   ```bash
   python mcp_server.py
   ```
   (Should start without errors)

2. **Check Cursor logs:**
   - Settings → MCP → View Logs
   - Look for error messages

3. **Enable verbose logging:**
   Add to MCP config:
   ```json
   {
     "mcpServers": {
       "data-engineering-copilot": {
         "command": "python",
         "args": ["-u", "/absolute/path/to/mcp_server.py"],
         "env": {
           "PYTHONUNBUFFERED": "1"
         }
       }
     }
   }
   ```

### Multiple MCP Servers

You can have multiple MCP servers configured:

```json
{
  "mcpServers": {
    "data-engineering-copilot": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    },
    "other-server": {
      "command": "node",
      "args": ["/path/to/other/server.js"]
    }
  }
}
```

---

## How It Works

1. **You ask Cursor** to use the copilot
2. **Cursor calls** the MCP tool `run_agent_task` with your prompt
3. **MCP server** receives the request via stdio
4. **Agent executes** the task using appropriate tools
5. **Response returns** to Cursor via MCP
6. **Cursor displays** the result

### Architecture

```
┌─────────┐
│ Cursor  │
│   AI    │
└────┬────┘
     │ MCP Protocol (stdio)
     ▼
┌─────────────────┐
│  MCP Server     │
│ (mcp_server.py) │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Root Agent     │
│  (agent.py)     │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Tools          │
│  (65+ tools)    │
└─────────────────┘
```

---

## Comparison: MCP vs API vs Direct Python

| Feature | MCP | REST API | Direct Python |
|---------|-----|----------|---------------|
| **Setup** | Medium | Easy | Easy |
| **Use in Cursor** | ✅ Native | ❌ HTTP calls | ✅ Import |
| **Natural Language** | ✅ Yes | ❌ No | ❌ No |
| **Team Sharing** | ❌ Per-user | ✅ Shared | ❌ Per-user |
| **Automation** | ⚠️ Limited | ✅ Full | ✅ Full |
| **Best For** | Daily use in Cursor | Team/automation | Scripts |

**Recommendation:**
- **MCP**: For daily development in Cursor
- **API**: For automation, CI/CD, team sharing
- **Direct Python**: For custom scripts

---

## Next Steps

1. ✅ Configure MCP server (see Quick Start)
2. ✅ Test with a simple prompt
3. ✅ Try different use cases
4. 📖 Read [Tools Reference](../reference/TOOLS_REFERENCE.md) for all available tools
5. 📖 Read [API Documentation](../api/API_DOCUMENTATION.md) for REST API usage

---

## Support

- **Issues**: Check [Troubleshooting](#troubleshooting) section
- **Documentation**: See [README.md](README.md) for full agent documentation
- **Tools Reference**: See [Tools Reference](../reference/TOOLS_REFERENCE.md) for all tools

