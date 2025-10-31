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
    from .simple_client import OLCAClient
    __all__ = ['OLCAClient']
except ImportError as e:
    print(f"Warning: Could not import OLCAClient: {e}")
    OLCAClient = None
    __all__ = []
