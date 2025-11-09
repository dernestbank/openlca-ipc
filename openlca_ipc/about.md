olca-utils/
├── olca_utils/
│   ├── __init__.py              # Main package init
│   ├── client.py                # Client wrapper
│   ├── search.py                # Search utilities
│   ├── data.py                  # Data creation
│   ├── systems.py               # Product systems
│   ├── calculations.py          # Calculation management
│   ├── results.py               # Results analysis
│   ├── contributions.py         # Contribution analysis
│   ├── uncertainty.py           # Monte Carlo & uncertainty
│   ├── parameters.py            # Parameter scenarios
│   ├── export.py                # Export utilities
│   └── visualization.py         # Plotting helpers
├── examples/
│   ├── basic_lca.py             # Basic LCA example
│   ├── contribution_analysis.py # Contribution example
│   ├── monte_carlo.py           # Uncertainty example
│   └── scenario_analysis.py     # Scenarios example
├── tests/
│   ├── test_search.py
│   ├── test_data.py
│   └── test_calculations.py
├── docs/
│   ├── api_reference.md
│   ├── tutorials/
│   └── examples/
├── setup.py
├── requirements.txt
├── README.md
└── LICENSE



🔧 API Reference
OLCAClient
Main entry point for all operations.
pythonclient = OLCAClient(port=8080)
Modules:

client.search - SearchUtils
client.data - DataBuilder
client.systems - SystemBuilder
client.calculate - CalculationManager
client.results - ResultsAnalyzer
client.contributions - ContributionAnalyzer
client.uncertainty - UncertaintyAnalyzer
client.parameters - ParameterManager
client.export - ExportManager

SearchUtils
Advanced search and discovery.
Methods:

find_flows(keywords, max_results, flow_type) - Search for flows
find_flow(keywords, flow_type) - Find first matching flow
find_providers(flow) - Get all providers for a flow
find_best_provider(flow) - Get best provider
find_processes(keywords, max_results) - Search for processes
find_impact_method(keywords) - Find impact method

DataBuilder
Create and manage data entities.
Methods:

create_product_flow(name, description) - Create product flow
create_exchange(flow, amount, is_input, is_qref, provider) - Create exchange
create_process(name, description, exchanges) - Create process

ContributionAnalyzer
Analyze contributions to impacts.
Methods:

get_process_contributions(result, impact_category, min_share) - Process contributions
get_flow_contributions(result, impact_category, min_share) - Flow contributions
get_top_contributors(result, impact_category, n, type) - Top N contributors
get_contribution_summary(result, impact_categories) - Summary for all categories

UncertaintyAnalyzer
Monte Carlo and uncertainty analysis.
Methods:

run_monte_carlo(system, method, iterations, amount, callback) - Run MC simulation
compare_with_uncertainty(system1, system2, method, iterations) - Statistical comparison

ParameterManager
Parameter scenarios and sensitivity.
Methods:

create_parameter_redef(name, value, context) - Create parameter redefinition
run_scenario_analysis(system, method, parameter, values, context) - Run scenarios

🤝 Contributing
Contributions are welcome! Please:

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

Development Setup
bash# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Check code style
flake8 olca_utils/
black olca_utils/
📝 Lessons Learned from PET vs PC Example
This library incorporates key lessons from the PET vs PC bottle LCA:

Search Strategy: Use get_descriptors() with partial matching instead of exact names
Provider Linking: Handle TechFlow objects correctly when getting providers
Error Handling: Graceful fallbacks when materials not found
Progress Feedback: User feedback during long operations
Resource Management: Always dispose results and simulators
Validation: Verify quantitative references before saving
Type Safety: Handle multiple result attribute names (amount vs value)

📖 Documentation
Full documentation available at: https://docs.example.com

API Reference
Tutorials
Examples
FAQ

🐛 Troubleshooting
Connection Issues
python# Check if openLCA IPC server is running
if not client.test_connection():
    print("Start IPC server in openLCA: Tools > Developer Tools > IPC Server")
Provider Not Found
python# Search may return None if exact keywords don't match
# Try broader keywords or check database
flows = client.search.find_flows(['polyethylene'], max_results=20)
for flow in flows:
    print(flow.name)  # Review available flows
Result Errors
python# Always use try-except for calculations
try:
    result = client.calculate.simple_calculation(system, method)
    impacts = client.results.get_total_impacts(result)
finally:
    if result:
        result.dispose()  # Always dispose
📄 License
MIT License - see LICENSE file for details.
🙏 Acknowledgments

openLCA team for the excellent LCA software
GreenDelta for olca-ipc and olca-schema libraries
Contributors and users of this library

📧 Contact

Issues: GitHub Issues
Discussions: GitHub Discussions
Email: your.email@example.com
