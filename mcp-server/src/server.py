#!/usr/bin/env python3
"""
OpenLCA MCP Server for Life Cycle Assessment Automation

This MCP server exposes openLCA functionality as tools for AI agents to automate
Life Cycle Assessment workflows. Tools are organized by the 4 LCA phases:

1. Goal & Scope Definition
2. Life Cycle Inventory (LCI)
3. Life Cycle Impact Assessment (LCIA)
4. Interpretation

Usage:
    python -m mcp-server.src.server

Environment Variables:
    OPENLCA_PORT: Port for openLCA IPC server (default: 8080)
    OPENLCA_HOST: Host for openLCA IPC server (default: localhost)
    LOG_LEVEL: Logging level (default: INFO)
"""

import os
import logging
import json
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from openlca_ipc import OLCAClient
import olca_schema as o

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global client instance
_client: Optional[OLCAClient] = None


def get_client() -> OLCAClient:
    """Get or create OpenLCA client."""
    global _client
    if _client is None:
        port = int(os.getenv("OPENLCA_PORT", "8080"))
        _client = OLCAClient(port=port)
        logger.info(f"Connected to openLCA on port {port}")
    return _client


# ============================================================================
# PHASE 1: GOAL & SCOPE DEFINITION TOOLS
# ============================================================================

TOOL_SEARCH_FLOWS = Tool(
    name="search_flows",
    description=(
        "Search for material flows in the openLCA database. "
        "Use this to find materials, products, or elementary flows needed for your LCA study. "
        "Keywords are case-insensitive and use partial matching (all keywords must be present). "
        "Example: keywords=['steel', 'hot', 'rolled'] finds 'Steel, hot rolled, coil'"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of keywords to search for (all must match)"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10
            },
            "flow_type": {
                "type": "string",
                "enum": ["PRODUCT_FLOW", "ELEMENTARY_FLOW", "WASTE_FLOW"],
                "description": "Optional filter by flow type"
            }
        },
        "required": ["keywords"]
    }
)

TOOL_SEARCH_PROCESSES = Tool(
    name="search_processes",
    description=(
        "Search for processes in the openLCA database. "
        "Use this to find existing production processes, transport processes, etc. "
        "Keywords are case-insensitive and use partial matching."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of keywords to search for"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results",
                "default": 10
            }
        },
        "required": ["keywords"]
    }
)

TOOL_SEARCH_IMPACT_METHODS = Tool(
    name="search_impact_methods",
    description=(
        "Search for LCIA methods in the database. "
        "Use this to find impact assessment methods like TRACI, ReCiPe, CML, ILCD, etc. "
        "Common methods: TRACI (US EPA), ReCiPe (Europe), CML (baseline), ILCD (recommended)"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Keywords for impact method (e.g., ['TRACI'], ['ReCiPe'])"
            }
        },
        "required": ["keywords"]
    }
)

TOOL_FIND_PROVIDERS = Tool(
    name="find_providers",
    description=(
        "Find all processes that produce a specific flow. "
        "Use this after searching for a flow to identify its production processes. "
        "Returns list of provider process references."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "flow_id": {
                "type": "string",
                "description": "ID of the flow to find providers for"
            },
            "flow_name": {
                "type": "string",
                "description": "Name of the flow (used if flow_id not provided)"
            }
        }
    }
)

# ============================================================================
# PHASE 2: LIFE CYCLE INVENTORY (LCI) TOOLS
# ============================================================================

TOOL_CREATE_PRODUCT_FLOW = Tool(
    name="create_product_flow",
    description=(
        "Create a new product flow in openLCA. "
        "Use this to define the product you're assessing or intermediate products. "
        "Flow will be created with Mass property and kg unit."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the product flow"
            },
            "description": {
                "type": "string",
                "description": "Optional description"
            }
        },
        "required": ["name"]
    }
)

TOOL_CREATE_PROCESS = Tool(
    name="create_process",
    description=(
        "Create a new process in openLCA with inputs and outputs. "
        "This is a core LCI tool for defining unit processes. "
        "Provide exchanges as list of objects with flow_id, amount, is_input, is_quantitative_reference, provider_id"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Process name"
            },
            "description": {
                "type": "string",
                "description": "Process description"
            },
            "exchanges": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "flow_id": {"type": "string", "description": "Flow ID or name"},
                        "amount": {"type": "number", "description": "Amount in kg"},
                        "is_input": {"type": "boolean", "description": "True if input"},
                        "is_quantitative_reference": {
                            "type": "boolean",
                            "description": "True if this is the main output"
                        },
                        "provider_id": {
                            "type": "string",
                            "description": "Optional provider process ID"
                        }
                    },
                    "required": ["flow_id", "amount", "is_input"]
                },
                "description": "List of exchanges (inputs and outputs)"
            }
        },
        "required": ["name", "exchanges"]
    }
)

TOOL_CREATE_PRODUCT_SYSTEM = Tool(
    name="create_product_system",
    description=(
        "Create a product system from a process. "
        "Product systems define the scope of LCA and automatically link processes via exchanges. "
        "Returns product system ID for use in calculations."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "process_id": {
                "type": "string",
                "description": "ID of the process to create system from"
            },
            "process_name": {
                "type": "string",
                "description": "Name of process (if ID not provided)"
            }
        }
    }
)

# ============================================================================
# PHASE 3: LIFE CYCLE IMPACT ASSESSMENT (LCIA) TOOLS
# ============================================================================

TOOL_CALCULATE_IMPACTS = Tool(
    name="calculate_impacts",
    description=(
        "Calculate environmental impacts for a product system. "
        "This performs LCIA and returns total impacts for all impact categories. "
        "Results include category name, amount, and unit. "
        "IMPORTANT: Results must be disposed after use with dispose_result tool."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "system_id": {
                "type": "string",
                "description": "Product system ID"
            },
            "system_name": {
                "type": "string",
                "description": "Product system name (if ID not provided)"
            },
            "method_id": {
                "type": "string",
                "description": "Impact method ID (from search_impact_methods)"
            },
            "method_keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Keywords to find method (if ID not provided)"
            },
            "amount": {
                "type": "number",
                "description": "Reference amount (default: 1.0)",
                "default": 1.0
            }
        }
    }
)

TOOL_GET_INVENTORY = Tool(
    name="get_inventory_results",
    description=(
        "Get detailed inventory results showing all flows and their amounts. "
        "Use this to see the full life cycle inventory (LCI) before or after impact assessment. "
        "Returns flows with amounts and units. Requires result_id from calculate_impacts."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "result_id": {
                "type": "string",
                "description": "Result ID from calculate_impacts"
            }
        },
        "required": ["result_id"]
    }
)

# ============================================================================
# PHASE 4: INTERPRETATION TOOLS
# ============================================================================

TOOL_CONTRIBUTION_ANALYSIS = Tool(
    name="analyze_contributions",
    description=(
        "Analyze which processes or flows contribute most to an impact category. "
        "Essential for interpretation phase - identifies hotspots in the system. "
        "Returns top contributors with their share (%) and absolute amounts."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "result_id": {
                "type": "string",
                "description": "Result ID from calculate_impacts"
            },
            "impact_category_id": {
                "type": "string",
                "description": "ID of impact category to analyze"
            },
            "n": {
                "type": "integer",
                "description": "Number of top contributors to return",
                "default": 10
            },
            "min_share": {
                "type": "number",
                "description": "Minimum contribution share (0-1)",
                "default": 0.01
            }
        },
        "required": ["result_id", "impact_category_id"]
    }
)

TOOL_MONTE_CARLO = Tool(
    name="run_monte_carlo",
    description=(
        "Run Monte Carlo uncertainty analysis to quantify uncertainty in results. "
        "Returns statistical summary: mean, std deviation, CV, percentiles. "
        "Use this for robust interpretation and decision-making. "
        "WARNING: Can be time-consuming for large systems."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "system_id": {
                "type": "string",
                "description": "Product system ID"
            },
            "method_id": {
                "type": "string",
                "description": "Impact method ID"
            },
            "iterations": {
                "type": "integer",
                "description": "Number of Monte Carlo iterations",
                "default": 100
            }
        },
        "required": ["system_id", "method_id"]
    }
)

TOOL_EXPORT_RESULTS = Tool(
    name="export_results",
    description=(
        "Export calculation results to CSV or JSON format. "
        "Use this to save results for reporting and further analysis. "
        "Supports both impact results and inventory results."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "description": "Results data to export (from calculate_impacts or other tools)"
            },
            "filename": {
                "type": "string",
                "description": "Output filename"
            },
            "format": {
                "type": "string",
                "enum": ["csv", "json"],
                "description": "Export format",
                "default": "csv"
            }
        },
        "required": ["data", "filename"]
    }
)

TOOL_DISPOSE_RESULT = Tool(
    name="dispose_result",
    description=(
        "Dispose of calculation result to free memory. "
        "CRITICAL: Always call this after finishing with results from calculate_impacts. "
        "Prevents memory leaks in openLCA server."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "result_id": {
                "type": "string",
                "description": "Result ID to dispose"
            }
        },
        "required": ["result_id"]
    }
)

# ============================================================================
# UTILITY TOOLS
# ============================================================================

TOOL_TEST_CONNECTION = Tool(
    name="test_connection",
    description=(
        "Test connection to openLCA IPC server. "
        "Use this first to verify openLCA is running and accessible. "
        "Returns connection status and server info."
    ),
    inputSchema={
        "type": "object",
        "properties": {},
    }
)

TOOL_LIST_DATABASES = Tool(
    name="list_databases",
    description=(
        "List all available databases in openLCA. "
        "Shows which databases are available for LCA studies."
    ),
    inputSchema={
        "type": "object",
        "properties": {},
    }
)


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

# Store active results for disposal
_active_results: Dict[str, Any] = {}


async def handle_search_flows(arguments: dict) -> List[TextContent]:
    """Handle search_flows tool call."""
    try:
        client = get_client()
        keywords = arguments["keywords"]
        max_results = arguments.get("max_results", 10)
        flow_type_str = arguments.get("flow_type")

        flow_type = None
        if flow_type_str:
            flow_type = getattr(o.FlowType, flow_type_str)

        flows = client.search.find_flows(keywords, max_results, flow_type)

        results = [
            {
                "id": f.id,
                "name": f.name,
                "category": f.category if hasattr(f, 'category') else None
            }
            for f in flows
        ]

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "count": len(results),
                "flows": results
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in search_flows: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_search_processes(arguments: dict) -> List[TextContent]:
    """Handle search_processes tool call."""
    try:
        client = get_client()
        keywords = arguments["keywords"]
        max_results = arguments.get("max_results", 10)

        processes = client.search.find_processes(keywords, max_results)

        results = [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category if hasattr(p, 'category') else None
            }
            for p in processes
        ]

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "count": len(results),
                "processes": results
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in search_processes: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_search_impact_methods(arguments: dict) -> List[TextContent]:
    """Handle search_impact_methods tool call."""
    try:
        client = get_client()
        keywords = arguments["keywords"]

        method = client.search.find_impact_method(keywords)

        if method:
            result = {
                "success": True,
                "method": {
                    "id": method.id,
                    "name": method.name,
                    "categories": [
                        {"id": cat.id, "name": cat.name}
                        for cat in (method.impact_categories or [])
                    ]
                }
            }
        else:
            result = {
                "success": False,
                "error": f"Impact method not found with keywords: {keywords}"
            }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error in search_impact_methods: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_find_providers(arguments: dict) -> List[TextContent]:
    """Handle find_providers tool call."""
    try:
        client = get_client()

        # Get flow reference
        if "flow_id" in arguments:
            flow_ref = o.Ref(id=arguments["flow_id"])
        elif "flow_name" in arguments:
            flows = client.search.find_flows([arguments["flow_name"]], max_results=1)
            if not flows:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Flow not found: {arguments['flow_name']}"
                    }, indent=2)
                )]
            flow_ref = flows[0]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Either flow_id or flow_name must be provided"
                }, indent=2)
            )]

        providers = client.search.find_providers(flow_ref)

        results = [
            {"id": p.id, "name": p.name}
            for p in providers
        ]

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "count": len(results),
                "providers": results
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in find_providers: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_create_product_flow(arguments: dict) -> List[TextContent]:
    """Handle create_product_flow tool call."""
    try:
        client = get_client()
        name = arguments["name"]
        description = arguments.get("description", "")

        flow = client.data.create_product_flow(name, description)

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "flow": {
                    "id": flow.id,
                    "name": flow.name,
                    "description": flow.description
                }
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in create_product_flow: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_create_process(arguments: dict) -> List[TextContent]:
    """Handle create_process tool call."""
    try:
        client = get_client()
        name = arguments["name"]
        description = arguments.get("description", "")
        exchanges_data = arguments["exchanges"]

        # Create exchanges
        exchanges = []
        for ex_data in exchanges_data:
            # Get flow
            flow_id = ex_data["flow_id"]
            flows = client.search.find_flows([flow_id], max_results=1)
            if not flows:
                # Try as ID directly
                flow_ref = o.Ref(id=flow_id)
            else:
                flow_ref = flows[0]

            # Get provider if specified
            provider = None
            if "provider_id" in ex_data:
                provider = o.Ref(id=ex_data["provider_id"])

            exchange = client.data.create_exchange(
                flow_ref,
                ex_data["amount"],
                ex_data["is_input"],
                ex_data.get("is_quantitative_reference", False),
                provider
            )
            exchanges.append(exchange)

        process = client.data.create_process(name, description, exchanges)

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "process": {
                    "id": process.id,
                    "name": process.name,
                    "description": process.description
                }
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in create_process: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_create_product_system(arguments: dict) -> List[TextContent]:
    """Handle create_product_system tool call."""
    try:
        client = get_client()

        # Get process reference
        if "process_id" in arguments:
            process_ref = o.Ref(id=arguments["process_id"])
        elif "process_name" in arguments:
            processes = client.search.find_processes([arguments["process_name"]], max_results=1)
            if not processes:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Process not found: {arguments['process_name']}"
                    }, indent=2)
                )]
            process_ref = processes[0]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Either process_id or process_name must be provided"
                }, indent=2)
            )]

        system = client.systems.create_product_system(process_ref)

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "product_system": {
                    "id": system.id,
                    "name": system.name
                }
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in create_product_system: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_calculate_impacts(arguments: dict) -> List[TextContent]:
    """Handle calculate_impacts tool call."""
    try:
        client = get_client()

        # Get system
        if "system_id" in arguments:
            system_ref = o.Ref(id=arguments["system_id"])
        elif "system_name" in arguments:
            # Search by name (simplified - may need better lookup)
            system_ref = o.Ref(id=arguments["system_name"])
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Either system_id or system_name must be provided"
                }, indent=2)
            )]

        # Get method
        if "method_id" in arguments:
            method = client.client.get(o.ImpactMethod, arguments["method_id"])
        elif "method_keywords" in arguments:
            method = client.search.find_impact_method(arguments["method_keywords"])
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Either method_id or method_keywords must be provided"
                }, indent=2)
            )]

        if not method:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Impact method not found"
                }, indent=2)
            )]

        amount = arguments.get("amount", 1.0)

        # Calculate
        result = client.calculate.simple_calculation(system_ref, method, amount)

        # Store result for later disposal
        result_id = str(id(result))
        _active_results[result_id] = result

        # Get impacts
        impacts = client.results.get_total_impacts(result)

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "result_id": result_id,
                "impacts": impacts,
                "message": "IMPORTANT: Call dispose_result when done with this result_id"
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in calculate_impacts: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_dispose_result(arguments: dict) -> List[TextContent]:
    """Handle dispose_result tool call."""
    try:
        result_id = arguments["result_id"]

        if result_id in _active_results:
            result = _active_results[result_id]
            result.dispose()
            del _active_results[result_id]
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": f"Result {result_id} disposed successfully"
                }, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Result {result_id} not found"
                }, indent=2)
            )]

    except Exception as e:
        logger.error(f"Error in dispose_result: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def handle_test_connection(arguments: dict) -> List[TextContent]:
    """Handle test_connection tool call."""
    try:
        client = get_client()
        is_connected = client.test_connection()

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "connected": is_connected,
                "port": client.port
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error in test_connection: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


# Map tool names to handlers
TOOL_HANDLERS = {
    "search_flows": handle_search_flows,
    "search_processes": handle_search_processes,
    "search_impact_methods": handle_search_impact_methods,
    "find_providers": handle_find_providers,
    "create_product_flow": handle_create_product_flow,
    "create_process": handle_create_process,
    "create_product_system": handle_create_product_system,
    "calculate_impacts": handle_calculate_impacts,
    "dispose_result": handle_dispose_result,
    "test_connection": handle_test_connection,
}


# ============================================================================
# MCP SERVER SETUP
# ============================================================================

# Create server instance
server = Server("openlca-lca-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available LCA tools organized by phase."""
    return [
        # Phase 1: Goal & Scope
        TOOL_TEST_CONNECTION,
        TOOL_SEARCH_FLOWS,
        TOOL_SEARCH_PROCESSES,
        TOOL_SEARCH_IMPACT_METHODS,
        TOOL_FIND_PROVIDERS,
        # Phase 2: LCI
        TOOL_CREATE_PRODUCT_FLOW,
        TOOL_CREATE_PROCESS,
        TOOL_CREATE_PRODUCT_SYSTEM,
        # Phase 3: LCIA
        TOOL_CALCULATE_IMPACTS,
        # Phase 4: Interpretation
        TOOL_CONTRIBUTION_ANALYSIS,
        TOOL_MONTE_CARLO,
        TOOL_EXPORT_RESULTS,
        # Utilities
        TOOL_DISPOSE_RESULT,
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from AI agents."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Unknown tool: {name}"
            }, indent=2)
        )]

    return await handler(arguments)


async def main():
    """Run the MCP server."""
    logger.info("Starting OpenLCA MCP Server...")
    logger.info(f"OpenLCA port: {os.getenv('OPENLCA_PORT', '8080')}")

    # Test connection on startup
    try:
        client = get_client()
        if client.test_connection():
            logger.info("✓ Successfully connected to openLCA")
        else:
            logger.warning("⚠ Could not verify connection to openLCA")
    except Exception as e:
        logger.error(f"✗ Failed to connect to openLCA: {e}")
        logger.error("Make sure openLCA is running with IPC server started")

    # Run server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
