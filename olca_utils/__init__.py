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
"""

__version__ = "0.1.0"
__author__ = "SD2 Lab"

# Import core functionality
try:
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
except ImportError as e:
    print(f"Warning: Could not import OLCAClient or utility classes: {e}")
    OLCAClient = None
    __all__ = []
