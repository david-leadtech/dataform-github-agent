# Quick Start Guide

Get the Data Engineering Copilot running in 5 minutes.

> **← [Back to README](README.md)** | **[View All Documentation](README.md#-documentation)**

## 🚀 Start the API Server

### Option 1: Using the Script (Recommended)

```bash
cd analytics/adk-agents-reference/data-engineering-copilot
./scripts/start_api_server.sh
```

### Option 2: Direct Python

```bash
cd analytics/adk-agents-reference/data-engineering-copilot
python api_server.py
```

### Option 3: Using uvicorn directly

```bash
cd analytics/adk-agents-reference/data-engineering-copilot
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

## ✅ Verify It's Working

Once the server starts, you should see:

```
🚀 Starting Data Engineering Copilot API server...
📖 API docs: http://localhost:8000/docs
🔍 Health check: http://localhost:8000/health
🎯 Run agent: POST http://localhost:8000/agent/run
```

### Test the Health Endpoint

**In browser:**
Open: http://localhost:8000/health

**With curl:**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "timestamp": "2025-01-28T..."
}
```

### Test the API Docs

Open in browser: **http://localhost:8000/docs**

You should see the Swagger UI with all endpoints.

## 🧪 Quick Test

### Test 1: List All Tools

```bash
curl http://localhost:8000/tools/list
```

### Test 2: Run the Agent

```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "List all available tools"}'
```

## 🔧 Troubleshooting

### Port Already in Use

If you get "Address already in use":

```bash
# Find what's using port 8000
lsof -i :8000

# Kill it (replace PID with actual process ID)
kill -9 <PID>

# Or use a different port
export API_PORT=8001
python api_server.py
```

### Dependencies Not Installed

```bash
pip install -r requirements.txt
```

### Import Errors

```bash
# Install the agent in editable mode
pip install -e .
```

### Authentication Issues

```bash
# Authenticate with Google Cloud
gcloud auth application-default login
```

## 📚 Next Steps

- **API Documentation**: See [docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)
- **Tools Reference**: See [docs/reference/TOOLS_REFERENCE.md](docs/reference/TOOLS_REFERENCE.md)
- **MCP Setup**: See [docs/mcp/MCP_DOCUMENTATION.md](docs/mcp/MCP_DOCUMENTATION.md)
- **Cursor Integration**: See [docs/integration/CURSOR_INTEGRATION.md](docs/integration/CURSOR_INTEGRATION.md)

