# API Reference

Complete API documentation for all modules in the openLCA IPC Python library.

## Core Modules

### Client and Connection
- [OLCAClient](client.md) - Main client for IPC connection and module access

### Data Operations
- [SearchUtils](search.md) - Search and discovery of flows, processes, and impact methods
- [DataBuilder](data.md) - Create and modify flows, exchanges, and processes
- [SystemBuilder](systems.md) - Build and configure product systems

### Calculation and Results
- [CalculationManager](calculations.md) - Execute LCA calculations
- [ResultsAnalyzer](results.md) - Extract and format calculation results

### Analysis Tools
- [ContributionAnalyzer](contributions.md) - Analyze contributions by process or flow
- [UncertaintyAnalyzer](uncertainty.md) - Monte Carlo simulations and statistical analysis
- [ParameterManager](parameters.md) - Parameter scenarios and sensitivity analysis

### Utilities
- [ExportManager](export.md) - Export results to CSV, Excel, and other formats

## Quick Navigation

| Module | Primary Use | Key Methods |
|--------|-------------|-------------|
| [OLCAClient](client.md) | Connection management | `__init__()`, `test_connection()` |
| [SearchUtils](search.md) | Finding entities | `find_flow()`, `find_process()`, `find_impact_method()` |
| [DataBuilder](data.md) | Creating data | `create_product_flow()`, `create_process()`, `create_exchange()` |
| [SystemBuilder](systems.md) | Product systems | `create_product_system()`, `auto_complete()` |
| [CalculationManager](calculations.md) | Running calculations | `simple_calculation()`, `contribution_analysis()` |
| [ResultsAnalyzer](results.md) | Extracting results | `get_total_impacts()`, `get_inventory_results()` |
| [ContributionAnalyzer](contributions.md) | Contribution analysis | `get_top_contributors()`, `get_process_contributions()` |
| [UncertaintyAnalyzer](uncertainty.md) | Uncertainty analysis | `run_monte_carlo()`, `compare_with_uncertainty()` |
| [ParameterManager](parameters.md) | Parameter scenarios | `run_scenario_analysis()`, `create_parameter_redef()` |
| [ExportManager](export.md) | Data export | `export_to_csv()`, `export_to_excel()` |

## Common Patterns

### Basic Workflow
```python
from openlca_ipc import OLCAClient

# 1. Connect
with OLCAClient(port=8080) as client:
    # 2. Search
    flow = client.search.find_flow(['material', 'name'])

    # 3. Create
    process = client.data.create_process(name="My Process")

    # 4. Calculate
    system = client.systems.create_product_system(process)
    method = client.search.find_impact_method(['method name'])
    result = client.calculate.simple_calculation(system, method)

    # 5. Analyze
    impacts = client.results.get_total_impacts(result)

    # 6. Cleanup
    result.dispose()
```

### Error Handling
```python
from openlca_ipc import OLCAClient

client = OLCAClient(port=8080)

# Always wrap calculations in try/finally
result = None
try:
    result = client.calculate.simple_calculation(system, method)
    impacts = client.results.get_total_impacts(result)
    # Process impacts...
except Exception as e:
    print(f"Calculation failed: {e}")
finally:
    if result:
        result.dispose()  # Always dispose
```

### Context Manager
```python
# Preferred: automatic cleanup
with OLCAClient(port=8080) as client:
    # Do work...
    pass
# Connection automatically closed
```

## Type Hints

All functions include type hints for better IDE support:

```python
from typing import List, Optional
import olca_schema as o

def find_flow(
    keywords: List[str],
    flow_type: Optional[o.FlowType] = None
) -> Optional[o.Ref]:
    ...
```

## Module Documentation

See individual module pages for detailed API documentation:

1. [OLCAClient](client.md) - Main client and connection management
2. [SearchUtils](search.md) - Search and discovery utilities
3. [DataBuilder](data.md) - Data creation utilities
4. [SystemBuilder](systems.md) - Product system management
5. [CalculationManager](calculations.md) - Calculation execution
6. [ResultsAnalyzer](results.md) - Results extraction and formatting
7. [ContributionAnalyzer](contributions.md) - Contribution analysis tools
8. [UncertaintyAnalyzer](uncertainty.md) - Uncertainty and Monte Carlo analysis
9. [ParameterManager](parameters.md) - Parameter and scenario management
10. [ExportManager](export.md) - Data export utilities
