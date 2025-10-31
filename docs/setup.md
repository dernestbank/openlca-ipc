
"""

Example Usage:
    >>> from olca_utils import OLCAClient
    >>> 
    >>> # Initialize client
    >>> client = OLCAClient(port=8080)
    >>> 
    >>> # Search for materials
    >>> pet_flow = client.search.find_flow(['polyethylene', 'terephthalate'])
    >>> 
    >>> # Create process
    >>> process = client.data.create_process(
    ...     name="PET Production",
    ...     inputs=[(pet_flow, 0.06)],
    ...     outputs=[('PET granulate', 0.065)]
    ... )
    >>> 
    >>> # Calculate and analyze
    >>> result = client.calculate.simple_calculation(process)
    >>> contributions = client.results.get_top_contributors(result, n=5)

Modules:
    client: Client connection and session management
    search: Advanced search and discovery
    data: Data creation utilities
    systems: Product system management
    calculations: Calculation execution
    results: Results analysis
    contributions: Contribution analysis
    uncertainty: Monte Carlo simulations
    parameters: Parameter scenarios
    export: Export utilities
    visualization: Basic plotting
"""

# 🚀 OpenLCA Utils - Complete Implementation Guide

## 📋 Table of Contents

1. [Project Setup](#project-setup)
2. [File Organization](#file-organization)
3. [Installation](#installation)
4. [Usage Examples](#usage-examples)
5. [Testing](#testing)
6. [Best Practices](#best-practices)

---

## 🗂️ Project Setup

### Step 1: Create Project Structure

```bash
mkdir olca-utils
cd olca-utils

# Create directory structure
mkdir -p olca_utils tests examples docs
touch README.md setup.py requirements.txt
touch olca_utils/__init__.py
```

### Step 2: Create All Module Files

Save each artifact content to the corresponding files:

```
olca-utils/
├── olca_utils/
│   ├── __init__.py           # From Artifact 1
│   ├── client.py             # From Artifact 1
│   ├── search.py             # From Artifact 1
│   ├── data.py               # From Artifact 1
│   ├── systems.py            # From Artifact 1
│   ├── calculations.py       # From Artifact 1
│   ├── results.py            # From Artifact 1
│   ├── contributions.py      # From Artifact 2
│   ├── uncertainty.py        # From Artifact 2
│   ├── parameters.py         # From Artifact 2
│   ├── export.py             # From Artifact 2
│   └── visualization.py      # (Optional - create if needed)
├── examples/
│   └── complete_workflow.py  # From Artifact 4
├── tests/
│   └── (test files)
├── docs/
│   └── (documentation)
├── setup.py                  # From Artifact 4
├── requirements.txt          # From Artifact 4
├── README.md                 # From Artifact 3
├── .gitignore               # From Artifact 4
└── LICENSE
```

---

## 💾 File Organization

### 1. Main Package (`olca_utils/__init__.py`)

```python
"""OpenLCA Utils - Professional Python library for openLCA IPC."""

__version__ = "1.0.0"

from .client import OLCAClient
from .search import SearchUtils
from .data import DataBuilder
from .systems import SystemBuilder
from .calculations import CalculationManager
from .results import ResultsAnalyzer
from .contributions import ContributionAnalyzer
from .uncertainty import UncertaintyAnalyzer
from .parameters import ParameterManager
from .export import ExportManager

__all__ = [
    'OLCAClient',
    'SearchUtils',
    'DataBuilder',
    'SystemBuilder',
    'CalculationManager',
    'ResultsAnalyzer',
    'ContributionAnalyzer',
    'UncertaintyAnalyzer',
    'ParameterManager',
    'ExportManager'
]
```

### 2. Split the Artifacts into Individual Files

**From Artifact 1**, extract and save to separate files:
- Lines for `client.py` → `olca_utils/client.py`
- Lines for `search.py` → `olca_utils/search.py`
- Lines for `data.py` → `olca_utils/data.py`
- etc.

**From Artifact 2**, extract:
- Lines for `contributions.py` → `olca_utils/contributions.py`
- Lines for `uncertainty.py` → `olca_utils/uncertainty.py`
- etc.

---


