# Architecture: How MCP Server Uses openlca-ipc Library

## Overview

The MCP server is **NOT** a replacement for the openlca-ipc library. Instead, it's a **thin wrapper** that exposes the library's functionality to AI agents via the Model Context Protocol.

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ AI Agent (n8n workflow)                                      │
│ "Calculate impacts for steel widget"                         │
└──────────────────┬──────────────────────────────────────────┘
                   │ MCP Protocol
                   │ (JSON tool calls)
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ MCP Server (mcp-server/src/server.py)                       │
│                                                               │
│ Tool: calculate_impacts                                      │
│ ↓                                                             │
│ Handler: handle_calculate_impacts()                          │
│   - Validate JSON inputs                                     │
│   - Get client: get_client() → OLCAClient                   │
│   - Call library methods ↓                                   │
└──────────────────┬──────────────────────────────────────────┘
                   │ Python function calls
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ openlca-ipc Library (openlca_ipc/)                          │
│                                                               │
│ client = OLCAClient(port=8080)                               │
│   ↓                                                           │
│ client.search.find_impact_method(['TRACI'])                 │
│   ↓                                                           │
│ client.calculate.simple_calculation(system, method)          │
│   ↓                                                           │
│ client.results.get_total_impacts(result)                    │
│                                                               │
│ These are YOUR library methods!                              │
└──────────────────┬──────────────────────────────────────────┘
                   │ olca-ipc protocol
                   │ (IPC/RPC calls)
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ openLCA IPC Server (port 8080)                              │
│ Running inside openLCA Desktop                               │
└──────────────────┬──────────────────────────────────────────┘
                   │ Database queries
                   │ Calculations
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ openLCA Desktop Application                                  │
│ - Database with flows, processes, methods                    │
│ - Calculation engine                                          │
│ - Impact assessment                                           │
└─────────────────────────────────────────────────────────────┘
```

## Code-Level Integration

### 1. MCP Server Imports the Library

**File: `mcp-server/src/server.py` (lines 1-25)**

```python
from openlca_ipc import OLCAClient          # ← Our library!
import olca_schema as o

# Global client instance
_client: Optional[OLCAClient] = None        # ← Using OLCAClient type

def get_client() -> OLCAClient:             # ← Returns OLCAClient
    """Get or create OpenLCA client."""
    global _client
    if _client is None:
        port = int(os.getenv("OPENLCA_PORT", "8080"))
        _client = OLCAClient(port=port)     # ← Creates instance of our class
        logger.info(f"Connected to openLCA on port {port}")
    return _client
```

### 2. Every Tool Uses Library Methods

**Example 1: Search Tool**

```python
# MCP Tool Definition
TOOL_SEARCH_FLOWS = Tool(
    name="search_flows",
    description="Search for material flows...",
    # ... schema ...
)

# Tool Handler - Uses Library
async def handle_search_flows(arguments: dict) -> List[TextContent]:
    client = get_client()                               # ← Get OLCAClient

    # CALLING OUR LIBRARY METHOD:
    flows = client.search.find_flows(                   # ← SearchUtils.find_flows()
        keywords=arguments["keywords"],
        max_results=arguments.get("max_results", 10),
        flow_type=flow_type
    )

    # Format for MCP response
    return [TextContent(type="text", text=json.dumps({
        "success": True,
        "flows": [{"id": f.id, "name": f.name} for f in flows]
    }))]
```

**Example 2: Calculation Tool**

```python
# MCP Tool Definition
TOOL_CALCULATE_IMPACTS = Tool(
    name="calculate_impacts",
    description="Calculate environmental impacts...",
    # ... schema ...
)

# Tool Handler - Uses Library
async def handle_calculate_impacts(arguments: dict) -> List[TextContent]:
    client = get_client()                               # ← Get OLCAClient

    # Get method using LIBRARY:
    method = client.search.find_impact_method(          # ← SearchUtils.find_impact_method()
        arguments["method_keywords"]
    )

    # Calculate using LIBRARY:
    result = client.calculate.simple_calculation(       # ← CalculationManager.simple_calculation()
        system_ref, method, amount
    )

    # Get impacts using LIBRARY:
    impacts = client.results.get_total_impacts(result)  # ← ResultsAnalyzer.get_total_impacts()

    # Format for MCP response
    return [TextContent(type="text", text=json.dumps({
        "success": True,
        "impacts": impacts,
        "result_id": result_id
    }))]
```

**Example 3: Data Creation Tool**

```python
# MCP Tool Definition
TOOL_CREATE_PROCESS = Tool(
    name="create_process",
    description="Create a new process...",
    # ... schema ...
)

# Tool Handler - Uses Library
async def handle_create_process(arguments: dict) -> List[TextContent]:
    client = get_client()                               # ← Get OLCAClient

    # Create exchanges using LIBRARY:
    exchange = client.data.create_exchange(             # ← DataBuilder.create_exchange()
        flow_ref,
        ex_data["amount"],
        ex_data["is_input"],
        ex_data.get("is_quantitative_reference", False),
        provider
    )

    # Create process using LIBRARY:
    process = client.data.create_process(               # ← DataBuilder.create_process()
        name, description, exchanges
    )

    # Format for MCP response
    return [TextContent(type="text", text=json.dumps({
        "success": True,
        "process": {"id": process.id, "name": process.name}
    }))]
```

## Complete Mapping

| MCP Tool | Library Class | Library Method | What It Does |
|----------|--------------|----------------|--------------|
| `test_connection` | `OLCAClient` | `test_connection()` | Verify openLCA connection |
| `search_flows` | `SearchUtils` | `find_flows()` | Search material database |
| `find_providers` | `SearchUtils` | `find_providers()` | Find production processes |
| `search_impact_methods` | `SearchUtils` | `find_impact_method()` | Find LCIA methods |
| `create_product_flow` | `DataBuilder` | `create_product_flow()` | Create new product |
| `create_process` | `DataBuilder` | `create_process()` + `create_exchange()` | Build unit process |
| `create_product_system` | `SystemBuilder` | `create_product_system()` | Build product system |
| `calculate_impacts` | `CalculationManager` + `ResultsAnalyzer` | `simple_calculation()` + `get_total_impacts()` | **Run LCA calculation** |
| `analyze_contributions` | `ContributionAnalyzer` | `get_top_contributors()` | Identify hotspots |
| `export_results` | `ExportManager` | `export_to_csv()` | Export data |

## Why This Architecture?

### The MCP Server is Just an Interface Layer

```python
# What MCP Server Does:
1. Receives JSON from AI agent
2. Validates inputs
3. Calls library method ← THE ACTUAL WORK
4. Formats response as JSON
5. Returns to AI agent

# What openlca-ipc Library Does:
1. Connects to openLCA
2. Searches database
3. Creates data
4. Runs calculations ← THIS IS WHERE CALCULATIONS HAPPEN
5. Analyzes results
6. Exports data
```

### Benefits of This Separation

✅ **Library can be used independently** - Direct Python scripts can use it
✅ **MCP server is just a thin wrapper** - No duplicate logic
✅ **Easy to maintain** - Fix bugs in library, MCP server automatically fixed
✅ **Type safety** - Library has Python types, MCP validates JSON
✅ **Testable** - Can test library and MCP server separately

## Proof: Check the Imports

**File: `mcp-server/requirements.txt`**

```txt
mcp>=0.9.0              # MCP protocol SDK
pydantic>=2.0.0         # Data validation
python-dotenv>=1.0.0    # Config
-e ..                   # ← INSTALLS openlca-ipc library from parent directory!
```

That `-e ..` line means: **Install the openlca-ipc library in development mode**.

When you run `pip install -r requirements.txt`, it:
1. Installs MCP SDK
2. Installs pydantic
3. Installs python-dotenv
4. **Installs your openlca-ipc library from the parent directory**

## Testing the Flow

### Test 1: Library Works Standalone

```python
# Direct library use (no MCP)
from openlca_ipc import OLCAClient

client = OLCAClient(port=8080)
steel = client.search.find_flow(['steel'])
print(steel.name)  # "steel, hot rolled, coil"
```

### Test 2: MCP Server Uses Library

```python
# MCP server handler
async def handle_search_flows(arguments):
    client = get_client()  # Same OLCAClient!
    flows = client.search.find_flows(['steel'])  # Same method!
    return format_as_json(flows)
```

### Test 3: AI Agent Uses MCP Server

```javascript
// n8n workflow
{
  "tool": "search_flows",
  "arguments": {"keywords": ["steel"]}
}
// ↓
// MCP Server receives
// ↓
// Calls client.search.find_flows(['steel'])
// ↓
// Returns JSON to n8n
```

## Real Example: Complete LCA Flow

Let's trace a complete LCA through all layers:

### 1. AI Agent Request (n8n)

```
"Calculate GWP for steel widget (2kg steel)"
```

### 2. Phase 1: Agent Calls `search_flows`

**MCP Tool Call:**
```json
{"tool": "search_flows", "arguments": {"keywords": ["steel"]}}
```

**MCP Handler:**
```python
client = get_client()
flows = client.search.find_flows(['steel'], 10)  # ← LIBRARY METHOD
```

**Library (SearchUtils.find_flows):**
```python
for flow_ref in self.client.get_descriptors(o.Flow):
    if all(kw in flow_ref.name.lower() for kw in keywords_lower):
        matches.append(flow_ref)
```

**openLCA IPC:** Returns flow descriptors from database

**Response to Agent:**
```json
{"success": true, "flows": [{"id": "steel-123", "name": "steel, hot rolled"}]}
```

### 3. Phase 2: Agent Calls `create_process`

**MCP Tool Call:**
```json
{
  "tool": "create_process",
  "arguments": {
    "name": "Widget Production",
    "exchanges": [
      {"flow_id": "widget-id", "amount": 1.0, "is_input": false, "is_quantitative_reference": true},
      {"flow_id": "steel-123", "amount": 2.0, "is_input": true, "provider_id": "steel-provider-456"}
    ]
  }
}
```

**MCP Handler:**
```python
client = get_client()
exchange = client.data.create_exchange(...)       # ← LIBRARY METHOD
process = client.data.create_process(name, exchanges)  # ← LIBRARY METHOD
```

**Library (DataBuilder):**
```python
def create_process(self, name, description, exchanges):
    process = o.Process()
    process.name = name
    process.exchanges = exchanges
    self.client.put(process)  # ← Saves to openLCA
    return process
```

**openLCA IPC:** Saves process to database

### 4. Phase 3: Agent Calls `calculate_impacts`

**MCP Tool Call:**
```json
{
  "tool": "calculate_impacts",
  "arguments": {
    "system_id": "widget-system-789",
    "method_keywords": ["TRACI"]
  }
}
```

**MCP Handler:**
```python
client = get_client()
method = client.search.find_impact_method(['TRACI'])           # ← LIBRARY
result = client.calculate.simple_calculation(system, method)   # ← LIBRARY (CALCULATION!)
impacts = client.results.get_total_impacts(result)             # ← LIBRARY
```

**Library (CalculationManager.simple_calculation):**
```python
def simple_calculation(self, system, impact_method, amount):
    setup = o.CalculationSetup()
    setup.target = system
    setup.impact_method = impact_method.to_ref()
    result = self.client.calculate(setup)  # ← Calls openLCA to calculate!
    result.wait_until_ready()
    return result
```

**openLCA IPC:** **PERFORMS THE LCA CALCULATION** (matrix operations, inventory, LCIA)

**Library (ResultsAnalyzer.get_total_impacts):**
```python
def get_total_impacts(self, result):
    impacts = []
    for impact in result.get_total_impacts():
        impacts.append({
            'name': impact.impact_category.name,
            'amount': impact.amount,
            'unit': impact.impact_category.ref_unit
        })
    return impacts
```

**Response to Agent:**
```json
{
  "success": true,
  "impacts": [
    {"name": "Global warming", "amount": 4.5, "unit": "kg CO2 eq"}
  ]
}
```

## Summary

**YES, the MCP server absolutely uses the openlca-ipc library for ALL operations!**

✅ Every tool call → calls library method
✅ All searches → use SearchUtils
✅ All data creation → use DataBuilder
✅ **All calculations → use CalculationManager** ← YOUR LIBRARY DOES THE WORK
✅ All analysis → use ResultsAnalyzer, ContributionAnalyzer

**The MCP server is just a translation layer** that makes your library accessible to AI agents!

```
AI Agent → MCP Server → openlca-ipc Library → openLCA
         (interface)    (your code)          (calculation engine)
```

**Your library is the brain. MCP server is just the mouth that speaks to AI agents.**
