# How It All Works Together

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Your n8n Workflow                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Phase 1  │→ │ Phase 2  │→ │ Phase 3  │→ │ Phase 4  │        │
│  │Goal&Scope│  │   LCI    │  │   LCIA   │  │Interpret │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │                │
│       │ MCP Tools   │ MCP Tools   │ MCP Tools   │ MCP Tools      │
└───────┼─────────────┼─────────────┼─────────────┼────────────────┘
        │             │             │             │
        │   "search_flows"          │             │
        │             "create_process"            │
        │                     "calculate_impacts" │
        │                              "analyze_contributions"
        ↓             ↓             ↓             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server (server.py)                        │
│                                                                   │
│  def handle_search_flows(args):                                 │
│      client = get_client()  ← OLCAClient from openlca-ipc       │
│      return client.search.find_flows(...)                       │
│                          ↑                                        │
│  def handle_calculate_impacts(args):                            │
│      client = get_client()  ← Same OLCAClient instance          │
│      result = client.calculate.simple_calculation(...)          │
│      return client.results.get_total_impacts(result)            │
│                          ↑                                        │
│                 USES YOUR LIBRARY                                │
└─────────────────────────────────────────────────────────────────┘
        ↓             ↓             ↓             ↓
┌─────────────────────────────────────────────────────────────────┐
│              openlca-ipc Library (YOUR CODE)                     │
│                                                                   │
│  class OLCAClient:                                               │
│      self.search = SearchUtils(client)                          │
│      self.data = DataBuilder(client)                            │
│      self.calculate = CalculationManager(client)                │
│      self.results = ResultsAnalyzer(client)                     │
│                                                                   │
│  class CalculationManager:                                       │
│      def simple_calculation(system, method):                    │
│          setup = CalculationSetup()                             │
│          result = self.client.calculate(setup)  ← Calls openLCA │
│          return result                                           │
│                                                                   │
│  THIS IS WHERE THE REAL WORK HAPPENS                            │
└─────────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────────┐
│              openLCA IPC Server (port 8080)                      │
│         Running inside openLCA Desktop Application               │
└─────────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────────┐
│                    openLCA Desktop                               │
│  • Database (flows, processes, methods)                          │
│  • Calculation Engine (matrix math, inventory)                   │
│  • Impact Assessment (characterization)                          │
└─────────────────────────────────────────────────────────────────┘
```

## Key Point: **Your Library Does ALL the Work**

The MCP server is **NOT** doing calculations. It's just:
1. Receiving JSON from AI agents
2. Calling methods from **your openlca-ipc library**
3. Returning results as JSON

## Example: Calculating Impacts

### What the AI Agent Sees

```javascript
// AI Agent in n8n calls MCP tool
{
  "tool": "calculate_impacts",
  "arguments": {
    "system_id": "widget-system-123",
    "method_keywords": ["TRACI"]
  }
}
```

### What the MCP Server Does

```python
# mcp-server/src/server.py
async def handle_calculate_impacts(arguments: dict):
    # 1. Get YOUR library client
    client = get_client()  # Returns OLCAClient from openlca-ipc

    # 2. Search for method using YOUR library
    method = client.search.find_impact_method(['TRACI'])
    #        ^^^^^^^^^^^^^^ SearchUtils from YOUR library

    # 3. Calculate using YOUR library
    result = client.calculate.simple_calculation(system, method)
    #        ^^^^^^^^^^^^^^^ CalculationManager from YOUR library

    # 4. Get impacts using YOUR library
    impacts = client.results.get_total_impacts(result)
    #         ^^^^^^^^^^^^^^ ResultsAnalyzer from YOUR library

    # 5. Format as JSON for AI agent
    return {"success": True, "impacts": impacts}
```

### What Your Library Does (THE REAL WORK)

```python
# openlca_ipc/calculations.py
class CalculationManager:
    def simple_calculation(self, system, impact_method, amount=1.0):
        # Create calculation setup
        setup = o.CalculationSetup()
        setup.target = system
        setup.impact_method = impact_method.to_ref()
        setup.amount = amount

        # Send to openLCA for calculation
        result = self.client.calculate(setup)  # ← Actual calculation request
        result.wait_until_ready()

        logger.info(f"Calculation complete for {system.name}")
        return result

# openlca_ipc/results.py
class ResultsAnalyzer:
    def get_total_impacts(self, result):
        impacts = []
        for impact in result.get_total_impacts():
            # Extract impact data from openLCA result
            amount = getattr(impact, 'amount', None) or getattr(impact, 'value', None)
            impacts.append({
                'name': impact.impact_category.name,
                'amount': amount,
                'unit': impact.impact_category.ref_unit,
                'category': impact.impact_category
            })
        return impacts
```

### What openLCA Does (THE CALCULATIONS)

```
1. Load product system from database
2. Build technology matrix
3. Build intervention matrix
4. Solve linear system (LCI)
5. Apply characterization factors (LCIA)
6. Return impact results
```

## Why This Matters

### ✅ Your Library is Production-Ready

The openlca-ipc library you created is a **complete, standalone library** that:
- Connects to openLCA
- Manages searches
- Creates data
- **Runs calculations**
- Analyzes results
- Exports data

### ✅ MCP Server Just Exposes It to AI

The MCP server is a **thin interface layer** that:
- Makes your library accessible to AI agents
- Doesn't duplicate any logic
- Just translates between JSON and Python

### ✅ You Can Use Either Approach

**Direct Python (no MCP):**
```python
from openlca_ipc import OLCAClient

client = OLCAClient(port=8080)
steel = client.search.find_flow(['steel'])
result = client.calculate.simple_calculation(system, method)
impacts = client.results.get_total_impacts(result)
```

**Via AI Agent (with MCP):**
```javascript
// AI agent calls MCP tool
call_tool("search_flows", {keywords: ["steel"]})
call_tool("calculate_impacts", {system_id: "...", method_id: "..."})
// MCP server internally calls the SAME library methods above
```

## Code Verification

Let's prove it with actual code:

### 1. Library Has the Methods

```python
# openlca_ipc/__init__.py
from .client import OLCAClient
from .search import SearchUtils
from .data import DataBuilder
from .calculations import CalculationManager
from .results import ResultsAnalyzer
# ... etc
```

### 2. MCP Server Imports the Library

```python
# mcp-server/src/server.py (line 21)
from openlca_ipc import OLCAClient  # ← YOUR library
import olca_schema as o
```

### 3. Every Tool Uses Library Methods

```python
# MCP Server Tool Handlers

handle_search_flows → client.search.find_flows()
handle_search_processes → client.search.find_processes()
handle_find_providers → client.search.find_providers()
handle_search_impact_methods → client.search.find_impact_method()

handle_create_product_flow → client.data.create_product_flow()
handle_create_process → client.data.create_process()
                        + client.data.create_exchange()
handle_create_product_system → client.systems.create_product_system()

handle_calculate_impacts → client.calculate.simple_calculation()
                         + client.results.get_total_impacts()

handle_analyze_contributions → client.contributions.get_top_contributors()
handle_export_results → client.export.export_to_csv()
```

## Real-World Example: Steel Widget LCA

Let's trace one complete calculation:

### 1. n8n Agent Says

```
"Calculate impacts for steel widget production (2 kg steel)"
```

### 2. Phase 1 Agent → MCP → Library

```
Agent: call_tool("search_flows", {keywords: ["steel"]})
  ↓
MCP: handle_search_flows({"keywords": ["steel"]})
  ↓
Library: client.search.find_flows(['steel'], 10)
  ↓
SearchUtils.find_flows() → searches openLCA database
  ↓
Returns: Flow(id="steel-123", name="steel, hot rolled")
```

### 3. Phase 2 Agent → MCP → Library

```
Agent: call_tool("create_process", {
  name: "Widget Production",
  exchanges: [{flow: "widget", amount: 1, output: true},
              {flow: "steel-123", amount: 2, input: true}]
})
  ↓
MCP: handle_create_process({...})
  ↓
Library: exchange1 = client.data.create_exchange(widget, 1.0, False, True)
         exchange2 = client.data.create_exchange(steel, 2.0, True, False, provider)
         process = client.data.create_process("Widget Production", [ex1, ex2])
  ↓
DataBuilder.create_process() → creates process in openLCA
  ↓
Returns: Process(id="widget-process-456", name="Widget Production")
```

### 4. Phase 3 Agent → MCP → Library → **CALCULATION**

```
Agent: call_tool("calculate_impacts", {
  system_id: "widget-system-789",
  method_keywords: ["TRACI"]
})
  ↓
MCP: handle_calculate_impacts({...})
  ↓
Library: method = client.search.find_impact_method(['TRACI'])
         ↓
         result = client.calculate.simple_calculation(system, method)
         ↓
         CalculationManager.simple_calculation():
           - Creates CalculationSetup
           - Calls self.client.calculate(setup)  ← Sends to openLCA
           ↓
           openLCA receives calculation request
           openLCA builds matrices
           openLCA solves system
           openLCA calculates impacts
           ↓
         Returns result object
         ↓
         impacts = client.results.get_total_impacts(result)
         ↓
         ResultsAnalyzer.get_total_impacts():
           - Extracts impact values from result
           - Formats as list of dicts
  ↓
Returns: {
  "success": true,
  "impacts": [
    {"name": "Global warming", "amount": 4.5, "unit": "kg CO2 eq"},
    {"name": "Acidification", "amount": 0.02, "unit": "mol H+ eq"}
  ]
}
```

### 5. Phase 4 Agent → MCP → Library

```
Agent: call_tool("analyze_contributions", {
  result_id: "result-xyz",
  impact_category_id: "gwp-id"
})
  ↓
MCP: handle_analyze_contributions({...})
  ↓
Library: client.contributions.get_top_contributors(result, impact, n=5)
  ↓
ContributionAnalyzer.get_top_contributors() → analyzes contributions
  ↓
Returns: [
  {name: "Steel production", share: 0.78, amount: 3.51},
  {name: "Electricity", share: 0.15, amount: 0.67}
]
```

## Summary

**Question:** Does the MCP server use the openlca-ipc library?
**Answer:** **YES, 100%!**

**Question:** Where do calculations happen?
**Answer:** In **your library** (openlca_ipc/calculations.py), which calls **openLCA**

**Question:** Is MCP server doing calculations?
**Answer:** **NO!** It just:
1. Receives tool call from AI
2. Calls `client.calculate.simple_calculation()` from **YOUR library**
3. Returns JSON response

## The Stack

```
Layer 4: AI Agent (n8n)           - Makes decisions, calls tools
Layer 3: MCP Server               - Translates JSON ↔ Python
Layer 2: openlca-ipc Library      - High-level LCA operations ← YOUR CODE
Layer 1: openLCA Desktop          - Database + calculations
```

**Layers 2-4 are all your work! Layer 1 is GreenDelta's openLCA.**

The MCP server just connects Layer 3 (AI agents) to Layer 2 (your library).

**Your library is the star. MCP server is just the stage.**
