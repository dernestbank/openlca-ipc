# ============================================================================
# FILE: olca_utils/results.py
# ============================================================================

"""
Results analysis and retrieval utilities.
"""

import logging
from typing import List, Dict, Optional
import olca_schema as o
import olca_ipc as ipc

logger = logging.getLogger(__name__)


class ResultsAnalyzer:
    """
    Utilities for analyzing calculation results.
    """
    
    def __init__(self, client: ipc.Client):
        self.client = client
    
    def get_total_impacts(self, result) -> List[Dict]:
        """
        Get all total impact results as dictionaries.
        
        Args:
            result: Calculation result
        
        Returns:
            List of impact dictionaries with keys:
                - name: Impact category name
                - amount: Impact value
                - unit: Impact unit
        
        Example:
            >>> impacts = results.get_total_impacts(result)
            >>> for impact in impacts:
            ...     print(f"{impact['name']}: {impact['amount']}")
        """
        impacts = []
        
        try:
            impact_results = result.get_total_impacts()
            
            for imp in impact_results:
                amount = (imp.amount if hasattr(imp, 'amount') 
                         else imp.value if hasattr(imp, 'value') 
                         else 0)
                
                impacts.append({
                    'name': imp.impact_category.name,
                    'category': imp.impact_category,
                    'amount': amount,
                    'unit': getattr(imp.impact_category, 'ref_unit', '')
                })
        
        except Exception as e:
            logger.error(f"Error getting impacts: {e}")
        
        return impacts
