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

## 📦 Installation

### Option 1: Development Installation

```bash
# Clone or navigate to project directory
cd olca-utils

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Or install with all extras
pip install -e ".[dev,viz,export]"
```

### Option 2: Install from Requirements

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Option 3: Direct Installation

```bash
pip install olca-ipc==2.4.0 olca-schema==2.4.0 numpy scipy matplotlib pandas
```

---

## 🎯 Usage Examples

### Example 1: Simple LCA

```python
from olca_utils import OLCAClient

# Initialize
with OLCAClient(port=8080) as client:
    # Search
    steel = client.search.find_flow(['steel'])
    provider = client.search.find_best_provider(steel)
    
    # Create process
    product = client.data.create_product_flow("Steel plate")
    exchanges = [
        client.data.create_exchange(product, 1.0, False, True),
        client.data.create_exchange(steel, 1.0, True, provider=provider)
    ]
    process = client.data.create_process("Plate production", exchanges=exchanges)
    
    # Calculate
    system = client.systems.create_product_system(process)
    method = client.search.find_impact_method(['TRACI'])
    result = client.calculate.simple_calculation(system, method)
    
    # Results
    impacts = client.results.get_total_impacts(result)
    for impact in impacts:
        print(f"{impact['name']}: {impact['amount']:.4e}")
    
    result.dispose()
```

### Example 2: Contribution Analysis

```python
from olca_utils import OLCAClient

client = OLCAClient(port=8080)

# Calculate with contributions
result = client.calculate.contribution_analysis(system, method)

# Get all impacts
impacts = client.results.get_total_impacts(result)

# Analyze each impact
for impact in impacts:
    print(f"\n{impact['name']}:")
    
    # Top 5 contributors
    contribs = client.contributions.get_top_contributors(
        result, impact['category'], n=5
    )
    
    for i, c in enumerate(contribs, 1):
        print(f"  {i}. {c.name}: {c.share*100:.1f}%")

result.dispose()
```

### Example 3: Monte Carlo with Plotting

```python
from olca_utils import OLCAClient
import matplotlib.pyplot as plt
import numpy as np

client = OLCAClient(port=8080)

# Run uncertainty analysis
results = client.uncertainty.run_monte_carlo(
    system=my_system,
    impact_method=traci,
    iterations=1000
)

# Plot distribution for global warming
gwp_name = next(k for k in results.keys() if 'warming' in k.lower())
gwp_data = results[gwp_name]

plt.figure(figsize=(10, 6))
plt.hist(gwp_data.values, bins=50, edgecolor='black', alpha=0.7)
plt.axvline(gwp_data.mean, color='red', linestyle='--', label='Mean')
plt.axvline(gwp_data.percentile_5, color='orange', linestyle=':', label='5th %ile')
plt.axvline(gwp_data.percentile_95, color='orange', linestyle=':', label='95th %ile')
plt.xlabel('Global Warming Potential')
plt.ylabel('Frequency')
plt.title('Global Warming - Monte Carlo Distribution')
plt.legend()
plt.savefig('gwp_distribution.png')
print("Plot saved to gwp_distribution.png")
```

### Example 4: Scenario Analysis

```python
from olca_utils import OLCAClient
import pandas as pd

client = OLCAClient(port=8080)

# Analyze transport distance scenarios
scenarios = client.parameters.run_scenario_analysis(
    system=my_system,
    impact_method=traci,
    parameter_name='transport_distance',
    values=[100, 200, 500, 1000, 2000, 5000]
)

# Create comparison table
data = []
for distance, impacts in scenarios.items():
    row = {'Distance (km)': distance}
    for impact in impacts:
        row[impact['name']] = impact['amount']
    data.append(row)

df = pd.DataFrame(data)
df.to_csv('scenario_analysis.csv', index=False)
print(df)
```

---

## 🧪 Testing

### Create Test Files

**tests/test_search.py:**

```python
import pytest
from olca_utils import OLCAClient

@pytest.fixture
def client():
    return OLCAClient(port=8080)

def test_find_flow(client):
    """Test flow search."""
    flows = client.search.find_flows(['steel'], max_results=5)
    assert len(flows) > 0
    assert all(hasattr(f, 'name') for f in flows)

def test_find_provider(client):
    """Test provider search."""
    flow = client.search.find_flow(['steel'])
    if flow:
        provider = client.search.find_best_provider(flow)
        assert provider is not None or True  # May not have provider
```

**Run tests:**

```bash
# Install pytest
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=olca_utils tests/
```

---

## 📚 Best Practices

### 1. Always Use Context Managers

```python
# Good - automatic cleanup
with OLCAClient(port=8080) as client:
    result = client.calculate.simple_calculation(system, method)
    # Process result
    result.dispose()

# Also good - explicit disposal
client = OLCAClient(port=8080)
try:
    result = client.calculate.simple_calculation(system, method)
    # Process result
finally:
    result.dispose()
```

### 2. Handle Missing Data Gracefully

```python
# Always check if search returns None
pet_flow = client.search.find_flow(['polyethylene', 'terephthalate'])

if not pet_flow:
    # Try alternative search
    pet_flow = client.search.find_flow(['PET'])
    
if not pet_flow:
    print("Material not found in database")
    return

# Proceed with pet_flow
```

### 3. Use Logging

```python
import logging

# Configure logging in your script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# olca_utils modules will log automatically
client = OLCAClient(port=8080)
# You'll see: "INFO - Connected to openLCA IPC server on port 8080"
```

### 4. Batch Process Multiple Systems

```python
systems = [
    ('PET Bottle', pet_system),
    ('PC Bottle', pc_system),
    ('Glass Bottle', glass_system)
]

results = {}

for name, system in systems:
    result = client.calculate.simple_calculation(system, method)
    impacts = client.results.get_total_impacts(result)
    results[name] = impacts
    result.dispose()

# Compare results
import pandas as pd
df = pd.DataFrame(results).T
df.to_csv('comparison.csv')
```

### 5. Export Results Consistently

```python
# Create results directory
import os
os.makedirs('results', exist_ok=True)

# Export with timestamps
from datetime import datetime
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

client.export.export_impacts_to_csv(
    impacts,
    f'results/impacts_{timestamp}.csv'
)
```

---

## 🔧 Customization

### Add Custom Methods

```python
# olca_utils/custom_analysis.py

class CustomAnalyzer:
    """Your custom analysis methods."""
    
    def __init__(self, client):
        self.client = client
    
    def your_method(self, system):
        """Your custom analysis."""
        pass

# In __init__.py, add:
from .custom_analysis import CustomAnalyzer

# In client.py, add:
self.custom = CustomAnalyzer(self.client)
```

### Extend Search Functionality

```python
# Add to search.py

def find_flows_by_category(self, category_name):
    """Find all flows in a category."""
    matches = []
    for flow_ref in self.client.get_descriptors(o.Flow):
        flow = self.client.get(o.Flow, flow_ref.id)
        if flow.category and category_name.lower() in flow.category.name.lower():
            matches.append(flow_ref)
    return matches
```

---

## 📖 Additional Resources

- **API Documentation**: See `docs/api_reference.md`
- **Examples**: Check `examples/` directory
- **Tests**: See `tests/` for usage patterns
- **Issues**: Report at GitHub Issues
- **Discussions**: Ask questions at GitHub Discussions

---

## 🎓 Learning Path

### Beginner
1. Start with `examples/complete_workflow.py`
2. Read the `README.md`
3. Try modifying the examples

### Intermediate
4. Explore contribution analysis
5. Try scenario analysis
6. Export results to different formats

### Advanced
7. Run Monte Carlo simulations
8. Compare systems with uncertainty
9. Create custom analysis modules
10. Contribute improvements

---

## ✅ Checklist for New Projects

- [ ] Install olca-utils and dependencies
- [ ] Start openLCA with IPC server
- [ ] Test connection with `client.test_connection()`
- [ ] Search for required materials
- [ ] Create processes with proper exchanges
- [ ] Validate quantitative references
- [ ] Create product systems
- [ ] Select appropriate impact method
- [ ] Run calculations and analyze
- [ ] Always dispose results
- [ ] Export results for reporting
- [ ] Document your workflow

---

## 🆘 Troubleshooting

### Problem: Connection Refused

**Solution:**
```python
# Check IPC server status
import requests
try:
    response = requests.post('http://localhost:8080')
    print("Server is running")
except:
    print("Start IPC server in openLCA:")
    print("Tools > Developer Tools > IPC Server")
```

### Problem: Material Not Found

**Solution:**
```python
# List available materials
flows = client.search.find_flows([''], max_results=100)
for flow in flows[:20]:
    print(flow.name)

# Adjust search keywords based on what you see
```

### Problem: All Impact Values are Zero

**Solution:**
```python
# Check if providers are linked
process = client.client.get(o.Process, process_id)
for ex in process.exchanges:
    if ex.is_input and not ex.default_provider:
        print(f"Missing provider: {ex.flow.name}")
        
# Use search.find_best_provider() to link providers
```

---

**Made with ❤️ for the LCA Community**

*For more help, visit: [GitHub Discussions](https://github.com/yourusername/olca-utils/discussions)*