# Project Summary: openlca_library with MCP Server

## What You Have Now

You have created a **complete LCA automation ecosystem** with two main components:

### 1. openlca-ipc Library (Core Foundation)
**Location:** `openlca_ipc/`

A high-level Python library that wraps openLCA IPC functionality:
- ✅ Connects to openLCA desktop application
- ✅ Searches for materials, processes, impact methods
- ✅ Creates flows, processes, product systems
- ✅ **Performs LCA calculations**
- ✅ Analyzes results and contributions
- ✅ Exports data to CSV/Excel
- ✅ Handles uncertainty and scenarios

**This is your production-ready LCA library!**

### 2. MCP Server for AI Agents (Automation Layer)
**Location:** `mcp-server/`

A Model Context Protocol server that exposes your library to AI agents:
- ✅ 15+ tools organized by ISO-14040/14044 LCA phases
- ✅ Integrates with n8n, Claude Desktop, other MCP tools
- ✅ Ready-to-use 4-phase workflow template
- ✅ Complete documentation and examples

**This makes your library AI-accessible!**

## How They Work Together

```
┌─────────────────────────────────────────────────────────┐
│  AI Agent (n8n Workflow)                                 │
│  "Calculate impacts for steel widget"                    │
└───────────────────┬─────────────────────────────────────┘
                    │ MCP Protocol
                    ↓
┌─────────────────────────────────────────────────────────┐
│  MCP Server (mcp-server/src/server.py)                  │
│  • Receives tool calls from AI                          │
│  • Validates inputs                                      │
│  • Calls library methods ↓                              │
└───────────────────┬─────────────────────────────────────┘
                    │ import openlca_ipc
                    ↓
┌─────────────────────────────────────────────────────────┐
│  openlca-ipc Library (openlca_ipc/)                     │
│  • client.search.find_flows()                           │
│  • client.calculate.simple_calculation() ← CALCULATIONS │
│  • client.results.get_total_impacts()                   │
│  THIS IS WHERE THE REAL WORK HAPPENS                    │
└───────────────────┬─────────────────────────────────────┘
                    │ olca-ipc protocol
                    ↓
┌─────────────────────────────────────────────────────────┐
│  openLCA Desktop + IPC Server                           │
│  • Database                                              │
│  • Calculation engine                                    │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
openlca_library/
│
├── openlca_ipc/                    # YOUR CORE LIBRARY
│   ├── __init__.py
│   ├── client.py                   # OLCAClient
│   ├── search.py                   # SearchUtils
│   ├── data.py                     # DataBuilder
│   ├── systems.py                  # SystemBuilder
│   ├── calculations.py             # CalculationManager ← Does calculations
│   ├── results.py                  # ResultsAnalyzer
│   ├── contributions.py            # ContributionAnalyzer
│   ├── uncertainty.py              # UncertaintyAnalyzer
│   ├── parameters.py               # ParameterManager
│   └── export.py                   # ExportManager
│
├── mcp-server/                     # AI AGENT INTERFACE
│   ├── src/
│   │   ├── __init__.py
│   │   └── server.py               # MCP server (uses library above)
│   ├── docs/
│   │   ├── n8n-integration.md      # n8n setup guide
│   │   └── quickstart.md           # Quick start
│   ├── examples/
│   │   ├── README.md
│   │   └── n8n-workflows/
│   │       └── basic_lca_workflow.json  # Complete 4-phase workflow
│   ├── README.md                   # MCP server docs
│   ├── ARCHITECTURE.md             # How it uses the library
│   ├── HOW_IT_WORKS.md            # Complete explanation
│   ├── INSTALLATION.md             # Install guide
│   ├── requirements.txt            # Dependencies (includes -e ..)
│   └── .env.example               # Config template
│
├── docs/                           # LIBRARY DOCUMENTATION
│   ├── index.md                    # Documentation hub
│   ├── installation.md             # Install guide
│   ├── quickstart.md              # Quick start
│   ├── faq.md                     # FAQ
│   ├── troubleshooting.md         # Troubleshooting
│   ├── best-practices.md          # Best practices
│   ├── DOCUMENTATION_MAP.md       # Complete doc map
│   └── api/                       # API reference
│       ├── README.md
│       ├── client.md
│       └── search.md
│
├── examples/                       # LIBRARY EXAMPLES
│   ├── README.md
│   ├── working_demo.py
│   └── ... (other examples)
│
├── tests/                         # TESTS
├── README.md                      # Main README
├── setup.py                       # Package setup
└── pyproject.toml                # Project config
```

## Key Files Explained

### Library Core

| File | Purpose | What It Does |
|------|---------|--------------|
| `openlca_ipc/client.py` | Main client | Connects to openLCA, provides module access |
| `openlca_ipc/search.py` | Search utilities | Find flows, processes, methods |
| `openlca_ipc/calculations.py` | **Calculations** | **Runs LCA calculations** |
| `openlca_ipc/results.py` | Results analysis | Extracts impact values |

### MCP Server

| File | Purpose | What It Does |
|------|---------|--------------|
| `mcp-server/src/server.py` | MCP server | Exposes library as MCP tools for AI |
| `mcp-server/requirements.txt` | Dependencies | Includes `-e ..` to install library |
| `mcp-server/docs/n8n-integration.md` | n8n guide | Complete n8n setup instructions |
| `mcp-server/examples/basic_lca_workflow.json` | n8n template | Ready-to-import workflow |

### Documentation

| File | Purpose | Audience |
|------|---------|----------|
| `docs/index.md` | Main docs hub | All users |
| `docs/quickstart.md` | Quick start | New users |
| `docs/api/` | API reference | Developers |
| `mcp-server/README.md` | MCP docs | AI/n8n users |
| `mcp-server/ARCHITECTURE.md` | Integration details | Understanding how it works |

## How Calculations Work

### Direct Python Use

```python
from openlca_ipc import OLCAClient

client = OLCAClient(port=8080)

# Search for materials
steel = client.search.find_flow(['steel'])
provider = client.search.find_best_provider(steel)

# Create process
product = client.data.create_product_flow("Widget")
exchanges = [
    client.data.create_exchange(product, 1.0, False, True),
    client.data.create_exchange(steel, 2.0, True, False, provider)
]
process = client.data.create_process("Widget Production", exchanges)

# Calculate ← THIS HAPPENS IN YOUR LIBRARY
system = client.systems.create_product_system(process)
method = client.search.find_impact_method(['TRACI'])
result = client.calculate.simple_calculation(system, method)  # ← Calculation!
impacts = client.results.get_total_impacts(result)

# The library calls openLCA which performs:
# 1. Matrix building
# 2. Linear system solving (LCI)
# 3. Impact characterization (LCIA)
```

### Via AI Agent (n8n)

```javascript
// AI agent calls MCP tool
{
  "tool": "calculate_impacts",
  "arguments": {
    "system_id": "widget-system-id",
    "method_keywords": ["TRACI"]
  }
}

// ↓ MCP server receives

// ↓ Internally calls:
client = get_client()  // OLCAClient from your library
result = client.calculate.simple_calculation(...)  // YOUR library method
impacts = client.results.get_total_impacts(result)  // YOUR library method

// ↓ Returns JSON to AI agent
{
  "success": true,
  "impacts": [
    {"name": "Global warming", "amount": 4.5, "unit": "kg CO2 eq"}
  ]
}
```

**Both paths use THE SAME library code!**

## Usage Scenarios

### Scenario 1: Python Scripting (No MCP)

Use the library directly for Python automation:

```python
from openlca_ipc import OLCAClient

client = OLCAClient(port=8080)
# ... use client.search, client.calculate, etc.
```

**Use case:** Batch processing, data analysis, custom scripts

### Scenario 2: AI Agent Automation (With MCP)

Use MCP server for AI-driven workflows:

```bash
cd mcp-server
python -m src.server  # Start MCP server

# Then in n8n:
# Import basic_lca_workflow.json
# Configure agents with prompts
# Let AI orchestrate the LCA
```

**Use case:** Interactive LCA, multi-agent workflows, intelligent analysis

### Scenario 3: Hybrid Approach

Use both:
- **Library** for heavy computation and data processing
- **MCP server** for high-level orchestration and decision-making

## What Each Component Does

### openlca-ipc Library (THE BRAIN)

✅ **Connects** to openLCA
✅ **Searches** database
✅ **Creates** data entities
✅ **Performs calculations** (calls openLCA calculation engine)
✅ **Analyzes** results
✅ **Exports** data

**This is production-ready and can be used standalone!**

### MCP Server (THE INTERFACE)

✅ **Receives** tool calls from AI agents
✅ **Validates** JSON inputs
✅ **Translates** to library method calls
✅ **Returns** formatted JSON responses

**This makes the library AI-accessible!**

### n8n Workflow (THE ORCHESTRATOR)

✅ **Manages** multi-agent conversation
✅ **Coordinates** 4 LCA phases
✅ **Makes decisions** based on results
✅ **Generates** reports

**This automates the entire LCA process!**

## Installation Quick Guide

### 1. Install Library

```bash
cd openlca_library
pip install -e ".[full]"
```

### 2. Install MCP Server (Optional)

```bash
cd mcp-server
pip install -r requirements.txt  # This also installs library via -e ..
cp .env.example .env
```

### 3. Configure n8n (Optional)

```json
{
  "name": "OpenLCA LCA Server",
  "command": "python",
  "args": ["-m", "src.server"],
  "cwd": "/path/to/mcp-server"
}
```

## Documentation Quick Links

### For Library Users

- [Main README](README.md) - Overview
- [Installation](docs/installation.md) - Setup
- [Quick Start](docs/quickstart.md) - Get started
- [API Reference](docs/api/README.md) - Complete API
- [Examples](examples/README.md) - Code examples

### For MCP/n8n Users

- [MCP Server README](mcp-server/README.md) - Overview
- [n8n Integration](mcp-server/docs/n8n-integration.md) - Complete n8n guide
- [Quick Start](mcp-server/docs/quickstart.md) - Get started in 10 min
- [Architecture](mcp-server/ARCHITECTURE.md) - How it works
- [Workflow Template](mcp-server/examples/n8n-workflows/basic_lca_workflow.json)

### For Understanding Integration

- [HOW_IT_WORKS.md](mcp-server/HOW_IT_WORKS.md) - Complete explanation
- [ARCHITECTURE.md](mcp-server/ARCHITECTURE.md) - Technical details
- [test_integration.py](mcp-server/test_integration.py) - Verify integration

## Key Insights

### 1. MCP Server USES the Library

The MCP server doesn't duplicate functionality. Every tool call maps to a library method:

```
search_flows → client.search.find_flows()
calculate_impacts → client.calculate.simple_calculation()
analyze_contributions → client.contributions.get_top_contributors()
```

### 2. Calculations Happen in Your Library

When an AI agent requests calculation:
1. n8n → calls MCP tool `calculate_impacts`
2. MCP → calls `client.calculate.simple_calculation()` from **your library**
3. Library → calls openLCA calculation engine
4. openLCA → performs actual calculation
5. Library → extracts results
6. MCP → returns JSON to n8n

### 3. Two Usage Modes, One Codebase

**Direct Python:**
```python
from openlca_ipc import OLCAClient
client = OLCAClient(port=8080)
```

**Via MCP/AI:**
```javascript
call_tool("calculate_impacts", {...})
// Internally uses same OLCAClient
```

**Same library, different interfaces!**

## Next Steps

### For Direct Python Use

1. Read [docs/quickstart.md](docs/quickstart.md)
2. Try [examples/working_demo.py](examples/working_demo.py)
3. Review [API reference](docs/api/README.md)

### For AI Agent Automation

1. Read [mcp-server/README.md](mcp-server/README.md)
2. Follow [n8n integration guide](mcp-server/docs/n8n-integration.md)
3. Import [workflow template](mcp-server/examples/n8n-workflows/basic_lca_workflow.json)

### For Understanding the System

1. Read [ARCHITECTURE.md](mcp-server/ARCHITECTURE.md)
2. Read [HOW_IT_WORKS.md](mcp-server/HOW_IT_WORKS.md)
3. Run [test_integration.py](mcp-server/test_integration.py)

## Summary

You have created:

✅ **A production-ready Python library** for LCA automation
✅ **Complete documentation** (20+ guides and references)
✅ **An MCP server** for AI agent integration
✅ **n8n workflow templates** for 4-phase LCA automation
✅ **Full integration** between all components

**Everything works together seamlessly!**

The library is the foundation. The MCP server is the interface. The n8n workflow is the orchestrator. Together, they enable fully automated AI-driven Life Cycle Assessment!

---

**Questions? See:**
- [FAQ](docs/faq.md)
- [Troubleshooting](docs/troubleshooting.md)
- [GitHub Issues](https://github.com/dernestbank/openlca-ipc/issues)
