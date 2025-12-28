# Using Data Engineering Copilot in Cursor

The agent can be used **locally** in Cursor in several ways. You don't need to deploy it to GCP - it runs on your machine and connects to GCP services via APIs.

## 🎯 Option 1: Direct Python Usage in Cursor (Simplest)

You can import and use the agent directly in Python scripts within Cursor:

```python
# In any Python file in Cursor
from data_engineering_copilot.agent import root_agent

# Use the agent
response = root_agent.run("Create a new Dataform source for Apple Ads")
print(response)
```

### Setup for Direct Usage

1. **Install the agent in editable mode:**
   ```bash
   cd analytics/adk-agents-reference/data-engineering-copilot
   pip install -e .
   ```

2. **Configure environment variables** (create `.env` file or set in Cursor):
   ```bash
   # In Cursor, you can set these in your .env file or terminal
   export GOOGLE_CLOUD_PROJECT=your-project-id
   export DATAFORM_REPOSITORY_NAME=your-repo
   export DATAFORM_WORKSPACE_NAME=your-workspace
   # ... etc
   ```

3. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth application-default login
   ```

4. **Use in Cursor:**
   - Create a Python file
   - Import and use the agent
   - Cursor's AI can help you write code that uses the agent

## 🌐 Option 2: ADK Web Interface (Recommended for Interactive Use)

Run the agent as a local web server and interact with it through a browser:

### Setup

1. **Install dependencies:**
   ```bash
   cd analytics/adk-agents-reference/data-engineering-copilot
   pip install -r requirements.txt
   ```

2. **Configure `.env` file** (see README.md for details)

3. **Run the web server:**
   ```bash
   adk web
   ```

4. **Access in browser:**
   - Opens at `http://localhost:8080` (or similar)
   - Chat interface to interact with the agent
   - Can use while coding in Cursor

### Benefits
- ✅ Interactive chat interface
- ✅ See agent's reasoning and tool calls
- ✅ No need to write Python code
- ✅ Works alongside Cursor

## 🔌 Option 3: MCP Server (Advanced - For Cursor AI Integration)

The MCP server is **already implemented**! It exposes the agent's tools directly to Cursor's AI.

**📖 For complete MCP documentation, see [MCP_DOCUMENTATION.md](MCP_DOCUMENTATION.md)**

### Quick Setup

1. **Install dependencies:**
   ```bash
   cd analytics/adk-agents-reference/data-engineering-copilot
   pip install -r requirements.txt
   ```

2. **Configure in Cursor:**
   
   Open `~/.cursor/mcp.json` and add:
   ```json
   {
     "mcpServers": {
       "data-engineering-copilot": {
         "command": "python",
         "args": ["/absolute/path/to/data-engineering-copilot/mcp_server.py"]
       }
     }
   }
   ```
   
   **Get the path:**
   ```bash
   cd analytics/adk-agents-reference/data-engineering-copilot
   pwd  # Copy this path
   ```

3. **Restart Cursor** and use:
   - Ask Cursor: "Use the data engineering copilot to create a new source"
   - Cursor's AI can now call the copilot directly

**See [MCP_DOCUMENTATION.md](MCP_DOCUMENTATION.md) for:**
- Complete setup guide
- Configuration examples
- Troubleshooting
- Usage examples
- Advanced configuration

## 📡 Option 4: REST API Server (For Team Use)

The REST API server is **already implemented**! It exposes the agent as a FastAPI service.

### Setup API Server

1. **Install dependencies:**
   ```bash
   cd analytics/adk-agents-reference/data-engineering-copilot
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   ./scripts/start_api_server.sh
   ```
   
   Or directly:
   ```bash
   python api_server.py
   ```

3. **Access the API:**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Run Agent: POST http://localhost:8000/agent/run

4. **Example usage:**
   ```bash
   curl -X POST http://localhost:8000/agent/run \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "Check the health of the data pipeline"}'
   ```

5. **For async execution:**
   ```bash
   curl -X POST http://localhost:8000/agent/run \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "Create a new Dataform source", "async_execution": true}'
   
   # Then check status:
   curl http://localhost:8000/agent/status/{task_id}
   ```

## 🔧 Configuration for Local Use

### Environment Variables

Create a `.env` file in the agent directory:

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
DATAFORM_REPOSITORY_NAME=your-repo
DATAFORM_WORKSPACE_NAME=your-workspace

# Optional but recommended
GOOGLE_GENAI_USE_VERTEXAI=1  # Use Vertex AI (requires GCP project)
ROOT_AGENT_MODEL=gemini-2.5-pro
GITHUB_TOKEN=ghp_your_token
GITHUB_REPO_PATH=your-org/your-repo
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your_token
```

### Authentication

**For Google Cloud services:**
```bash
# Authenticate with Application Default Credentials
gcloud auth application-default login

# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

**For GitHub:**
- Create token at: https://github.com/settings/tokens
- Scope: `repo`

**For Databricks:**
- Get token from Databricks workspace settings

## 💡 Usage Examples in Cursor

### Example 1: Direct Python Usage

```python
# In a Python file in Cursor
from data_engineering_copilot.agent import root_agent

# Task 1: Create a new source
result = root_agent.run(
    "Create a new Dataform source for Apple Ads and make a PR"
)
print(result)

# Task 2: Debug a pipeline
result = root_agent.run(
    "Check the health of the data pipeline and find any failed jobs"
)
print(result)
```

### Example 2: Using with Cursor's AI

1. **Ask Cursor's AI:**
   ```
   "Use the data engineering copilot to create a new staging table for user events"
   ```

2. **Cursor will:**
   - Import the agent
   - Call it with your request
   - Show you the results

### Example 3: Script Automation

```python
# scripts/automate_pipeline.py
from data_engineering_copilot.agent import root_agent

def create_pipeline_stage(stage_name: str, tags: list):
    """Automate pipeline stage creation."""
    prompt = f"""
    Create a new Dataform staging table called {stage_name} 
    with tags {tags}. Make sure it follows our project conventions.
    """
    return root_agent.run(prompt)

# Use in Cursor or run as script
if __name__ == "__main__":
    result = create_pipeline_stage("user_events", ["staging", "events"])
    print(result)
```

## 🚀 Quick Start for Cursor

1. **Install the agent:**
   ```bash
   cd analytics/adk-agents-reference/data-engineering-copilot
   pip install -e .
   ```

2. **Set up `.env`** (copy from README.md)

3. **Authenticate:**
   ```bash
   gcloud auth application-default login
   ```

4. **Use in Cursor:**
   - Import in Python files
   - Or run `adk web` in terminal and use browser interface
   - Or ask Cursor's AI to use the agent

## ❓ FAQ

**Q: Do I need to deploy to GCP?**  
A: No! The agent runs locally on your machine. It only connects to GCP services (Dataform, BigQuery, etc.) via APIs.

**Q: Can I use it without Vertex AI?**  
A: Yes, but you'll need to configure a different model. The agent uses Google's Gemini models, which can run via Vertex AI (GCP) or potentially other endpoints.

**Q: How do I use it with Cursor's AI?**  
A: Either import it directly in Python, or create an MCP server (Option 3) to expose it to Cursor's AI directly.

**Q: Can multiple people use it?**  
A: Yes! Each person runs it locally with their own credentials. Or set up the REST API server (Option 4) for shared use.

## 🔗 Related Documentation

- [README.md](README.md) - Full agent documentation
- [RELEASES.md](RELEASES.md) - Release management
- [CHANGELOG.md](CHANGELOG.md) - Version history

