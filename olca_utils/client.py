
# ============================================================================
# FILE: olca_utils/client.py
# ============================================================================

"""
Client management and connection utilities.
"""

import logging
from typing import Optional
import olca_schema as o
import olca_ipc as ipc

from .search import SearchUtils
from .data import DataBuilder
from .systems import SystemBuilder
from .calculations import CalculationManager
from .results import ResultsAnalyzer
from .contributions import ContributionAnalyzer
from .uncertainty import UncertaintyAnalyzer
from .parameters import ParameterManager
from .export import ExportManager

logger = logging.getLogger(__name__)


class OLCAClient:
    """
    Main client wrapper for openLCA IPC operations.
    
    Provides organized access to all utility modules through a single interface.
    
    Attributes:
        client (ipc.Client): Underlying IPC client
        search (SearchUtils): Search utilities
        data (DataBuilder): Data creation utilities
        systems (SystemBuilder): Product system utilities
        calculate (CalculationManager): Calculation utilities
        results (ResultsAnalyzer): Results analysis utilities
        contributions (ContributionAnalyzer): Contribution analysis
        uncertainty (UncertaintyAnalyzer): Uncertainty analysis
        parameters (ParameterManager): Parameter management
        export (ExportManager): Export utilities
    
    Example:
        >>> client = OLCAClient(port=8080)
        >>> client.test_connection()
        True
        >>> flows = client.search.find_flows(['steel'])
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
            
            # Initialize utility modules
            self.search = SearchUtils(self.client)
            self.data = DataBuilder(self.client)
            self.systems = SystemBuilder(self.client)
            self.calculate = CalculationManager(self.client)
            self.results = ResultsAnalyzer(self.client)
            self.contributions = ContributionAnalyzer(self.client)
            self.uncertainty = UncertaintyAnalyzer(self.client)
            self.parameters = ParameterManager(self.client)
            self.export = ExportManager(self.client)
            
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
        self.client.close()

