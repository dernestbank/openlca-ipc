

# ============================================================================
# FILE: olca_utils/calculations.py
# ============================================================================

"""
Calculation execution and management.
"""

import logging
from typing import Optional
import olca_schema as o
import olca_ipc as ipc

logger = logging.getLogger(__name__)


class CalculationManager:
    """
    Utilities for setting up and executing calculations.
    """
    
    def __init__(self, client: ipc.Client):
        self.client = client
    
    def simple_calculation(
        self,
        system: o.Ref,
        impact_method: Optional[o.ImpactMethod] = None,
        amount: float = 1.0
    ):
        """
        Perform a simple calculation.
        
        Args:
            system: Product system reference
            impact_method: Optional impact method
            amount: Reference amount (default: 1.0)
        
        Returns:
            Calculation result
        
        Example:
            >>> result = calculate.simple_calculation(
            ...     system=my_system,
            ...     impact_method=traci_method,
            ...     amount=1.0
            ... )
            >>> # Don't forget to dispose!
            >>> result.dispose()
        """
        setup = o.CalculationSetup()
        setup.target = system
        setup.amount = amount
        
        if impact_method:
            setup.impact_method = impact_method.to_ref()
        
        result = self.client.calculate(setup)
        result.wait_until_ready()
        
        logger.info(f"Calculation complete for {system.name}")
        return result
    
    def contribution_analysis(
        self,
        system: o.Ref,
        impact_method: o.ImpactMethod,
        amount: float = 1.0
    ):
        """Perform contribution analysis."""
        setup = o.CalculationSetup()
        setup.target = system
        setup.impact_method = impact_method.to_ref()
        setup.amount = amount
        
        result = self.client.calculate(setup)
        result.wait_until_ready()
        return result

