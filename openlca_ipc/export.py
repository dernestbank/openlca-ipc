# ============================================================================
# FILE: olca_utils/export.py
# ============================================================================

"""
Export utilities for results and data.
"""

import logging
import csv
import json
from pathlib import Path
from typing import List, Dict
import olca_schema as o
import olca_ipc as ipc

logger = logging.getLogger(__name__)


class ExportManager:
    """
    Utilities for exporting results and data.
    
    Supports export to Excel, CSV, JSON, and other formats.
    """
    
    def __init__(self, client: ipc.Client):
        self.client = client
    
    def export_to_excel(
        self,
        result,
        filepath: str
    ) -> bool:
        """
        Export calculation result to Excel.
        
        Args:
            result: Calculation result
            filepath: Output Excel file path
        
        Returns:
            True if successful
        
        Example:
            >>> export.export_to_excel(result, 'lca_results.xlsx')
        """
        try:
            self.client.excel_export(result, filepath)
            logger.info(f"Exported results to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            return False
    
    def export_impacts_to_csv(
        self,
        impacts: List[Dict],
        filepath: str
    ) -> bool:
        """
        Export impact results to CSV.
        
        Args:
            impacts: List of impact dictionaries
            filepath: Output CSV file path
        
        Returns:
            True if successful
        
        Example:
            >>> impacts = results.get_total_impacts(result)
            >>> export.export_impacts_to_csv(impacts, 'impacts.csv')
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if not impacts:
                    return False
                
                writer = csv.DictWriter(f, fieldnames=['name', 'amount', 'unit'])
                writer.writeheader()
                writer.writerows(impacts)
            
            logger.info(f"Exported {len(impacts)} impacts to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return False
    
    def export_comparison_to_csv(
        self,
        comparison_data: Dict[str, Dict],
        filepath: str
    ) -> bool:
        """
        Export comparison results to CSV.
        
        Args:
            comparison_data: Comparison dictionary
            filepath: Output CSV file path
        
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Impact Category', 'System 1', 'System 2', 'Difference', '% Difference'])
                
                for impact, data in comparison_data.items():
                    writer.writerow([
                        impact,
                        f"{data.get('system1', 0):.4e}",
                        f"{data.get('system2', 0):.4e}",
                        f"{data.get('difference', 0):.4e}",
                        f"{data.get('percent_diff', 0):.2f}%"
                    ])
            
            logger.info(f"Exported comparison to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Comparison export failed: {e}")
            return False
