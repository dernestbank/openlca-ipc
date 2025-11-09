# ============================================================================
# FILE: olca_utils/simple_client.py
# ============================================================================

"""
Simple client management for openLCA IPC operations.
"""

import logging
from typing import Optional
import olca_schema as o
import olca_ipc as ipc

logger = logging.getLogger(__name__)


class OLCAClient:
    """
    Simplified client wrapper for openLCA IPC operations.
    
    Provides basic connection functionality without dependencies on 
    problematic utility modules.
    """
    
    def __init__(self, port: int = 8080):
        """
        Initialize the openLCA client.
        
        Args:
            port: IPC server port (default: 8080)
        
        Raises:
            ConnectionError: If unable to connect to server
        """
        try:
            self.client = ipc.Client(port)
            self.port = port
            logger.info(f"Connected to openLCA IPC server on port {port}")
            
            # Initialize empty placeholders for utility modules
            # These will be implemented later
            self.search = None
            self.data = None
            self.systems = None
            self.calculate = None
            self.results = None
            self.contributions = None
            self.uncertainty = None
            self.parameters = None
            self.export = None
            
        except Exception as e:
            logger.error(f"Failed to connect to openLCA: {e}")
            raise ConnectionError(f"Could not connect to openLCA IPC server on port {port}")
    
    def test_connection(self) -> bool:
        """
        Test if connection to openLCA is working.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get Mass property as a connection test
            mass = self.client.get(o.FlowProperty, name="Mass")
            return mass is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # olca_ipc Client doesn't have a close method
        pass