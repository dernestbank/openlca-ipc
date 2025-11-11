# MCP Server Examples

Examples demonstrating how to use the OpenLCA MCP Server for AI-automated LCA workflows.

## Overview

This folder contains:
- **n8n workflows** - Complete workflow templates for n8n
- **Python scripts** - Direct MCP client examples
- **Agent prompts** - Sample prompts for AI agents

## n8n Workflows

### basic_lca_workflow.json

Complete 4-phase LCA workflow for n8n.

**What it does:**
- Phase 1: Goal & Scope - Search materials and impact method
- Phase 2: LCI - Create process and product system
- Phase 3: LCIA - Calculate environmental impacts
- Phase 4: Interpretation - Analyze and export results

**How to use:**
1. Import into n8n: Workflows → Import → Select file
2. Configure MCP server credential
3. Adjust input variables (product name, materials)
4. Execute workflow

**Input:**
```json
{
  "product_name": "PET Water Bottle",
  "functional_unit": "1 bottle (500ml)",
  "pet_amount": 0.025
}
```

**Output:**
```json
{
  "title": "LCA Report: PET Water Bottle",
  "phase1_goal_scope": {...},
  "phase2_inventory": {...},
  "phase3_impacts": [...],
  "phase4_interpretation": {
    "hotspots": [...],
    "recommendations": [...]
  }
}
```

### comparative_lca.json (Coming Soon)

Compare environmental impacts of multiple products.

**Use case:** PET vs Glass bottles, Electric vs Gas cars, etc.

### batch_processing.json (Coming Soon)

Process multiple LCAs in parallel or sequence.

**Use case:** Analyze product portfolio, sensitivity analysis

## Python Examples

### direct_mcp_client.py (Coming Soon)

Example of calling MCP server directly from Python without n8n.

```python
import asyncio
from mcp import ClientSession

async def run_lca():
    async with ClientSession(server_config) as session:
        # Test connection
        result = await session.call_tool("test_connection", {})

        # Search for materials
        flows = await session.call_tool("search_flows", {
            "keywords": ["steel"],
            "max_results": 5
        })

        # ... more tool calls
```

## Agent Prompt Templates

### Phase 1: Goal & Scope Definition

```
You are an LCA Goal & Scope specialist working with OpenLCA MCP server.

TASK: Define goal and scope for LCA study

PRODUCT: {product_name}
MATERIALS NEEDED: {materials_list}
IMPACT METHOD: {method_preference}

INSTRUCTIONS:
1. Call test_connection() to verify openLCA access
2. For each material, use search_flows(keywords=[...])
3. For each flow found, use find_providers(flow_id=...)
4. Use search_impact_methods(keywords=[method]) to find method
5. Return structured JSON:
   {
     "materials_found": [{id, name, provider_id, amount}],
     "materials_missing": [...],
     "impact_method": {id, name},
     "status": "complete" | "incomplete"
   }

TOOLS AVAILABLE:
- test_connection
- search_flows
- find_providers
- search_impact_methods

REMEMBER:
- All keywords are case-insensitive
- Use partial matching (broader keywords work better)
- Check for common spelling variations
```

### Phase 2: Life Cycle Inventory

```
You are an LCA Inventory (LCI) specialist working with OpenLCA MCP server.

TASK: Build life cycle inventory

INPUT FROM PHASE 1:
{phase1_results}

INSTRUCTIONS:
1. Create product flow: create_product_flow(name=product_name)
2. Build exchanges array:
   - Output: {flow: product_id, amount: 1, is_input: false, is_quantitative_reference: true}
   - Inputs: For each material from Phase 1:
     {flow: material_id, amount: X, is_input: true, provider: provider_id}
3. Create process: create_process(name=..., exchanges=[...])
4. Create system: create_product_system(process_id=...)
5. Return structured JSON:
   {
     "product_flow_id": "...",
     "process_id": "...",
     "product_system_id": "...",
     "status": "complete"
   }

TOOLS AVAILABLE:
- create_product_flow
- create_process
- create_product_system

CRITICAL:
- Exactly ONE exchange must have is_quantitative_reference: true
- ALL product inputs MUST have provider_id
- Elementary flows (CO2, water) do NOT need providers
```

### Phase 3: Impact Assessment

```
You are an LCA Impact Assessment (LCIA) specialist working with OpenLCA MCP server.

TASK: Calculate environmental impacts

INPUT FROM PHASE 2:
Product System ID: {system_id}

INPUT FROM PHASE 1:
Impact Method ID: {method_id}

INSTRUCTIONS:
1. Calculate: calculate_impacts(
     system_id=...,
     method_id=...,
     amount=1.0
   )
2. Extract result_id from response (CRITICAL for Phase 4)
3. Return structured JSON:
   {
     "result_id": "...",
     "impacts": [...],
     "status": "complete"
   }

TOOLS AVAILABLE:
- calculate_impacts
- get_inventory_results (optional)

IMPORTANT:
- Save result_id - needed for Phase 4 and cleanup
- DO NOT dispose result yet
```

### Phase 4: Interpretation

```
You are an LCA Interpretation specialist working with OpenLCA MCP server.

TASK: Analyze results and provide insights

INPUT FROM PHASE 3:
Result ID: {result_id}
Impacts: {impacts_list}

INSTRUCTIONS:
1. For each major impact category (amount > 0.01):
   - analyze_contributions(result_id=..., impact_category_id=..., n=5)
   - Identify hotspots (contribution > 10%)
2. Export results: export_results(data=impacts, filename="results.csv", format="csv")
3. Generate insights and recommendations
4. Return structured JSON:
   {
     "hotspots": [{impact, contributor, percent, amount}],
     "exports": {csv_file: "..."},
     "recommendations": [...],
     "status": "complete"
   }

TOOLS AVAILABLE:
- analyze_contributions
- export_results
- run_monte_carlo (optional)

DO NOT:
- Call dispose_result (handled separately in cleanup node)

PROVIDE:
- Clear identification of hotspots
- Actionable recommendations
- Quantified contribution percentages
```

## Tool Usage Patterns

### Pattern 1: Search with Fallback

```javascript
// Try specific search first
let flow = await callTool("search_flows", {
  keywords: ["polyethylene", "terephthalate", "bottle"],
  max_results: 1
});

// If not found, try broader search
if (flow.count === 0) {
  flow = await callTool("search_flows", {
    keywords: ["polyethylene", "terephthalate"],
    max_results: 5
  });
}

// If still not found, try abbreviation
if (flow.count === 0) {
  flow = await callTool("search_flows", {
    keywords: ["PET"],
    max_results: 10
  });
}
```

### Pattern 2: Validate Before Proceeding

```javascript
// Search for all required materials
const materials = ["steel", "aluminum", "copper"];
const found = [];
const missing = [];

for (const material of materials) {
  const result = await callTool("search_flows", {
    keywords: [material],
    max_results: 1
  });

  if (result.count > 0) {
    found.push({name: material, id: result.flows[0].id});
  } else {
    missing.push(material);
  }
}

// Only proceed if all found
if (missing.length > 0) {
  return {
    error: `Missing materials: ${missing.join(", ")}`,
    action: "request_user_input"
  };
}

// Continue with LCA...
```

### Pattern 3: Error Recovery

```javascript
try {
  const result = await callTool("calculate_impacts", {
    system_id: systemId,
    method_id: methodId
  });

  if (!result.success) {
    // Log error and try alternative
    console.error("Calculation failed:", result.error);

    // Try with different method
    const altMethod = await callTool("search_impact_methods", {
      keywords: ["ReCiPe"]
    });

    // Retry calculation
    return await callTool("calculate_impacts", {
      system_id: systemId,
      method_id: altMethod.method.id
    });
  }

  return result;

} catch (error) {
  console.error("Fatal error:", error);
  return {
    success: false,
    error: error.message,
    troubleshooting: [
      "Check if openLCA is running",
      "Verify product system is complete",
      "Check if impact method is compatible"
    ]
  };
}
```

## Testing Examples

### Test Individual Tools

Create small n8n workflows to test each tool:

**test_search.json:**
```json
{
  "nodes": [
    {
      "type": "ManualTrigger"
    },
    {
      "type": "MCPToolCall",
      "parameters": {
        "tool": "search_flows",
        "arguments": {
          "keywords": ["steel"],
          "max_results": 5
        }
      }
    }
  ]
}
```

**test_calculate.json:**
```json
{
  "nodes": [
    {
      "type": "ManualTrigger"
    },
    {
      "type": "Set",
      "parameters": {
        "values": {
          "system_id": "your-test-system-id",
          "method_id": "your-test-method-id"
        }
      }
    },
    {
      "type": "MCPToolCall",
      "parameters": {
        "tool": "calculate_impacts",
        "arguments": {
          "system_id": "={{ $json.system_id }}",
          "method_id": "={{ $json.method_id }}"
        }
      }
    }
  ]
}
```

## Common Use Cases

### Use Case 1: Material Substitution Analysis

Compare impacts of using different materials:

1. Create process with Material A
2. Calculate impacts
3. Create process with Material B
4. Calculate impacts
5. Compare results

### Use Case 2: Sensitivity Analysis

Test how parameter changes affect impacts:

1. Create base process
2. Calculate base case
3. Modify amounts (e.g., transport distance)
4. Recalculate
5. Compare results

### Use Case 3: Product Portfolio LCA

Analyze multiple products:

1. Loop through product list
2. For each product:
   - Search materials
   - Create process
   - Calculate impacts
3. Aggregate results
4. Identify worst performers

## Integration Examples

### Integrate with External Systems

**Send results to dashboard:**
```javascript
// After Phase 4
const results = $('Phase 4: Interpretation').item.json;

await fetch('https://your-dashboard.com/api/lca-results', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    product: productName,
    impacts: results.impacts,
    hotspots: results.hotspots,
    timestamp: new Date().toISOString()
  })
});
```

**Email report:**
```javascript
// After generating report
await sendEmail({
  to: 'stakeholder@company.com',
  subject: `LCA Report: ${productName}`,
  body: formatReport(results),
  attachments: [results.exports.csv_file]
});
```

## Best Practices

1. **Always test connection first**
2. **Validate search results before using**
3. **Handle missing data gracefully**
4. **Dispose results after use**
5. **Log all tool calls for debugging**
6. **Add error recovery logic**
7. **Use specific keywords in searches**
8. **Check tool response success field**

## Troubleshooting

See main [README.md](../README.md#troubleshooting) for common issues.

## Contributing Examples

Have a useful example? Please contribute!

1. Create example file
2. Add documentation
3. Test thoroughly
4. Submit PR

## License

Examples are part of the openlca-mcp-server project (MIT License).
