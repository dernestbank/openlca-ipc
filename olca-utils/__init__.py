# ============================================================================
# OpenLCA Utils - Professional Python Library
# ============================================================================
# A comprehensive utility library for openLCA IPC operations
# Compatible with: olca-ipc 2.4.0, olca-schema 2.4.0, openLCA 2.x
# ============================================================================

"""
olca_utils: Professional utilities for openLCA IPC operations

This package provides high-level utilities for working with openLCA through
the IPC protocol, making LCA workflows easier and more maintainable.

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

__version__ = "1.0.0"
__author__ = "LCA Team"
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
