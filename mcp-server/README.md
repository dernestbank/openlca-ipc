# OpenLCA MCP Server for AI Agent Automation

Model Context Protocol (MCP) server that exposes openLCA functionality as tools for AI agents to automate Life Cycle Assessment (LCA) workflows.

## Overview

This MCP server enables AI agents (like those in n8n workflows) to interact with openLCA programmatically. Tools are organized by the 4 phases of ISO-14040/14044 LCA methodology:

1. **Goal & Scope Definition** - Search for materials, processes, and impact methods
2. **Life Cycle Inventory (LCI)** - Create flows, processes, and product systems
3. **Life Cycle Impact Assessment (LCIA)** - Calculate environmental impacts
4. **Interpretation** - Analyze contributions, uncertainty, and export results

## Features

- ✅ **15+ specialized LCA tools** for AI agents
- ✅ **Phase-organized** following ISO LCA standards
- ✅ **n8n compatible** for workflow automation
- ✅ **Error handling** and logging for production use
- ✅ **Memory management** with result disposal
- ✅ **Async support** for concurrent operations

## Prerequisites

Before running the MCP server:

1. **openLCA Desktop**
   - Version 2.x installed and running
   - Database loaded
   - IPC server started (Tools → Developer Tools → IPC Server)

2. **Python Environment**
   - Python 3.10 or higher
   - openlca-ipc library installed

3. **For n8n Integration**
   - n8n instance running
   - MCP integration enabled in n8n

## Installation

### 1. Install Dependencies

```bash
cd mcp-server
pip install -r requirements.txt
```

This will install:
- MCP SDK
- openlca-ipc library (from parent directory)
- Pydantic for validation
- python-dotenv for configuration

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file:

```bash
# OpenLCA IPC Server Configuration
OPENLCA_PORT=8080          # Match your IPC server port
OPENLCA_HOST=localhost

# Logging Configuration
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR

# MCP Server Configuration
MCP_SERVER_NAME=openlca-lca-server
MCP_SERVER_VERSION=0.1.0
```

### 3. Test the Server

```bash
python -m src.server
```

You should see:
```
Starting OpenLCA MCP Server...
OpenLCA port: 8080
✓ Successfully connected to openLCA
MCP Server running...
```

## Available Tools

### Phase 1: Goal & Scope Definition

| Tool | Purpose | Inputs |
|------|---------|--------|
| `test_connection` | Test openLCA connection | None |
| `search_flows` | Find material flows | keywords, max_results, flow_type |
| `search_processes` | Find processes | keywords, max_results |
| `search_impact_methods` | Find LCIA methods | keywords |
| `find_providers` | Find production processes | flow_id or flow_name |

### Phase 2: Life Cycle Inventory (LCI)

| Tool | Purpose | Inputs |
|------|---------|--------|
| `create_product_flow` | Create new product | name, description |
| `create_process` | Create unit process | name, description, exchanges |
| `create_product_system` | Build product system | process_id or process_name |

### Phase 3: Life Cycle Impact Assessment (LCIA)

| Tool | Purpose | Inputs |
|------|---------|--------|
| `calculate_impacts` | Calculate environmental impacts | system_id, method_id, amount |
| `get_inventory_results` | Get LCI results | result_id |

### Phase 4: Interpretation

| Tool | Purpose | Inputs |
|------|---------|--------|
| `analyze_contributions` | Find impact hotspots | result_id, impact_category_id, n |
| `run_monte_carlo` | Uncertainty analysis | system_id, method_id, iterations |
| `export_results` | Export to CSV/JSON | data, filename, format |

### Utilities

| Tool | Purpose | Inputs |
|------|---------|--------|
| `dispose_result` | Free calculation memory | result_id |

## Usage Examples

### Example 1: Complete LCA Workflow (AI Agent Perspective)

An AI agent would call tools in this sequence:

```
1. test_connection()
   → Verify openLCA is accessible

2. search_flows(keywords=["steel"])
   → Find steel flow ID

3. find_providers(flow_id="...")
   → Find steel production process ID

4. create_product_flow(name="My Widget")
   → Create product flow, get ID

5. create_process(
     name="Widget Production",
     exchanges=[
       {flow_id: "widget_id", amount: 1.0, is_input: false, is_quantitative_reference: true},
       {flow_id: "steel_id", amount: 2.0, is_input: true, provider_id: "provider_id"}
     ]
   )
   → Create process, get ID

6. create_product_system(process_id="...")
   → Build product system, get ID

7. search_impact_methods(keywords=["TRACI"])
   → Find impact method ID

8. calculate_impacts(system_id="...", method_id="...")
   → Get impacts + result_id

9. analyze_contributions(result_id="...", impact_category_id="...")
   → Identify hotspots

10. dispose_result(result_id="...")
    → Clean up memory
```

### Example 2: Search and Discovery

```json
// Tool: search_flows
{
  "keywords": ["polyethylene", "terephthalate"],
  "max_results": 5,
  "flow_type": "PRODUCT_FLOW"
}

// Response:
{
  "success": true,
  "count": 2,
  "flows": [
    {
      "id": "abc-123",
      "name": "polyethylene terephthalate, granulate, bottle grade",
      "category": "plastics"
    }
  ]
}
```

### Example 3: Create Process

```json
// Tool: create_process
{
  "name": "PET Bottle Production",
  "description": "Produces 1 PET bottle from granulate",
  "exchanges": [
    {
      "flow_id": "bottle_flow_id",
      "amount": 1.0,
      "is_input": false,
      "is_quantitative_reference": true
    },
    {
      "flow_id": "pet_granulate_id",
      "amount": 0.025,
      "is_input": true,
      "provider_id": "pet_production_id"
    }
  ]
}

// Response:
{
  "success": true,
  "process": {
    "id": "process-123",
    "name": "PET Bottle Production",
    "description": "Produces 1 PET bottle from granulate"
  }
}
```

### Example 4: Calculate Impacts

```json
// Tool: calculate_impacts
{
  "system_id": "system-123",
  "method_id": "traci-method-id",
  "amount": 1.0
}

// Response:
{
  "success": true,
  "result_id": "result-456",
  "impacts": [
    {
      "name": "Global warming",
      "amount": 0.05,
      "unit": "kg CO2 eq",
      "category": "gwp-id"
    },
    {
      "name": "Acidification",
      "amount": 0.0001,
      "unit": "mol H+ eq",
      "category": "acid-id"
    }
  ],
  "message": "IMPORTANT: Call dispose_result when done with this result_id"
}
```

## n8n Integration

### Setup Steps

1. **Install MCP Integration in n8n**
   - Install MCP nodes in your n8n instance
   - Configure MCP connection

2. **Configure MCP Server Connection**
   ```json
   {
     "name": "OpenLCA LCA Server",
     "serverType": "stdio",
     "command": "python",
     "args": ["-m", "src.server"],
     "cwd": "/path/to/mcp-server",
     "env": {
       "OPENLCA_PORT": "8080",
       "LOG_LEVEL": "INFO"
     }
   }
   ```

3. **Create n8n Workflow**

   See [examples/n8n-workflows/](examples/n8n-workflows/) for complete workflow templates.

### 4-Phase LCA Workflow Template

Your n8n workflow should have 4 agent phases:

**Phase 1 Agent: Goal & Scope**
- Use: `test_connection`, `search_flows`, `search_processes`, `search_impact_methods`
- Output: List of required materials, processes, and impact method

**Phase 2 Agent: Life Cycle Inventory**
- Use: `create_product_flow`, `create_process`, `create_product_system`
- Output: Product system ID ready for calculation

**Phase 3 Agent: Impact Assessment**
- Use: `calculate_impacts`, `get_inventory_results`
- Output: Impact results with result_id

**Phase 4 Agent: Interpretation**
- Use: `analyze_contributions`, `export_results`, `dispose_result`
- Output: Analysis report and exported files

See [docs/n8n-integration.md](docs/n8n-integration.md) for detailed setup.

## Architecture

```
┌─────────────────────────────────────────┐
│         n8n Workflow Agents             │
│  ┌────────┬────────┬────────┬────────┐  │
│  │Phase 1 │Phase 2 │Phase 3 │Phase 4 │  │
│  │ Goal & │  LCI   │  LCIA  │Interp. │  │
│  │ Scope  │        │        │        │  │
│  └───┬────┴───┬────┴───┬────┴───┬────┘  │
│      │        │        │        │       │
│      └────────┴────────┴────────┘       │
│               MCP Protocol               │
└──────────────────┬──────────────────────┘
                   │
          ┌────────▼────────┐
          │   MCP Server    │
          │  (this server)  │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │ openlca-ipc lib │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │  openLCA IPC    │
          │     Server      │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │openLCA Desktop  │
          │   Application   │
          └─────────────────┘
```

## Error Handling

The MCP server includes comprehensive error handling:

```json
// Success response
{
  "success": true,
  "data": { ... }
}

// Error response
{
  "success": false,
  "error": "Detailed error message"
}
```

Common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| "Could not connect to openLCA" | IPC server not running | Start IPC server in openLCA |
| "Flow not found" | Material doesn't exist | Try different keywords or add to database |
| "No provider found" | Elementary flow or missing process | Check flow type or add provider |
| "Result X not found" | Result already disposed | Don't reuse disposed results |

## Best Practices for AI Agents

### 1. Always Test Connection First
```
Step 1: Call test_connection()
Step 2: If connected, proceed with workflow
```

### 2. Check Search Results
```
Step 1: Call search_flows(keywords=[...])
Step 2: If count > 0, use first result
Step 3: If count == 0, try alternative keywords
```

### 3. Always Dispose Results
```
Step 1: Call calculate_impacts() → get result_id
Step 2: Use result_id for analysis
Step 3: Call dispose_result(result_id) when done
```

### 4. Handle Missing Data Gracefully
```
If search returns empty:
  - Try broader keywords
  - Try alternative spellings
  - Create the needed data
  - Report to user
```

## Development

### Running in Development Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run server
python -m src.server
```

### Testing Tools

Use MCP inspector or direct tool calls:

```bash
# Install MCP inspector
npm install -g @modelcontextprotocol/inspector

# Inspect server
mcp-inspector python -m src.server
```

### Adding New Tools

1. Define tool schema in `server.py`:
```python
TOOL_MY_NEW_TOOL = Tool(
    name="my_new_tool",
    description="What it does",
    inputSchema={...}
)
```

2. Implement handler:
```python
async def handle_my_new_tool(arguments: dict) -> List[TextContent]:
    # Implementation
    pass
```

3. Register in handlers map:
```python
TOOL_HANDLERS = {
    "my_new_tool": handle_my_new_tool,
    ...
}
```

4. Add to tool list:
```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [..., TOOL_MY_NEW_TOOL]
```

## Troubleshooting

### Server Won't Start

**Problem:** Server fails to start

**Check:**
1. Is Python 3.10+ installed? `python --version`
2. Are dependencies installed? `pip list | grep mcp`
3. Is .env file configured? `cat .env`

### Can't Connect to openLCA

**Problem:** `test_connection` returns false

**Check:**
1. Is openLCA running?
2. Is database loaded?
3. Is IPC server started?
4. Does port in .env match IPC server?

### Tool Calls Fail

**Problem:** Tools return errors

**Check:**
1. Review error message in response
2. Check server logs (LOG_LEVEL=DEBUG)
3. Verify inputs match schema
4. Test with MCP inspector

## Logging

View logs to debug issues:

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run server and view logs
python -m src.server 2>&1 | tee server.log
```

Log levels:
- **DEBUG**: All operations and data
- **INFO**: Major operations (default)
- **WARNING**: Issues that don't stop operation
- **ERROR**: Failures and exceptions

## Performance

### Resource Usage

- **Memory**: ~50-100 MB baseline
- **CPU**: Minimal (most work in openLCA)
- **Network**: Localhost only (IPC)

### Optimization Tips

1. **Dispose results promptly** - Prevents memory leaks
2. **Limit search results** - Use max_results parameter
3. **Cache impact methods** - Reuse method IDs
4. **Batch operations** - Create multiple processes before calculating

## Security

### Local Only

This server is designed for **local use only**:
- Connects to localhost openLCA
- No network exposure
- No authentication required

### Production Deployment

For production use:
- Add authentication
- Restrict tool access
- Audit tool calls
- Limit concurrent connections

## Contributing

Contributions welcome! See main project [CONTRIBUTING.md](../CONTRIBUTING.md).

## License

MIT License - See [LICENSE](../LICENSE) for details.

## Support

- **Documentation**: [Full docs](docs/)
- **Issues**: [GitHub Issues](https://github.com/dernestbank/openlca-ipc/issues)
- **Email**: dernestbanksch@gmail.com

## Acknowledgments

Built on:
- [MCP Protocol](https://modelcontextprotocol.io/) by Anthropic
- [openlca-ipc](https://github.com/dernestbank/openlca-ipc)
- [openLCA](https://www.openlca.org/) by GreenDelta

---

**Ready to automate your LCA workflows with AI agents!**
