# ============================================================================
# FILE: olca_utils/contributions.py
# ============================================================================

"""
Contribution analysis utilities.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Optional
import olca_schema as o
import olca_ipc as ipc

logger = logging.getLogger(__name__)


@dataclass
class ContributionItem:
    """
    Represents a contribution to an impact.
    
    Attributes:
        name: Contributor name (process, flow, or location)
        amount: Absolute contribution value
        share: Relative share (0-1)
        ref: Reference to the contributor
    """
    name: str
    amount: float
    share: float
    ref: Optional[o.Ref] = None


class ContributionAnalyzer:
    """
    Utilities for detailed contribution analysis.
    
    Provides methods to identify top contributors to impacts at
    process, flow, and location levels.
    """
    
    def __init__(self, client: ipc.Client):
        self.client = client
    
    def get_process_contributions(
        self,
        result,
        impact_category: o.Ref,
        min_share: float = 0.01
    ) -> List[ContributionItem]:
        """
        Get process contributions to an impact category.
        
        Args:
            result: Calculation result (must be CONTRIBUTION_ANALYSIS or higher)
            impact_category: Impact category reference
            min_share: Minimum share to include (default: 1%)
        
        Returns:
            List of contribution items, sorted by amount (descending)
        
        Example:
            >>> contribs = contributions.get_process_contributions(
            ...     result, 
            ...     global_warming_ref,
            ...     min_share=0.05  # Only show >5%
            ... )
            >>> for c in contribs[:5]:
            ...     print(f"{c.name}: {c.share*100:.1f}%")
        """
        try:
            raw_contributions = self.client.lcia_process_contributions(
                result, 
                impact_category
            )
            
            contributions = []
            for item in raw_contributions:
                if item.share >= min_share:
                    contributions.append(ContributionItem(
                        name=item.item.name if hasattr(item, 'item') else str(item),
                        amount=item.amount,
                        share=item.share,
                        ref=item.item if hasattr(item, 'item') else None
                    ))
            
            # Sort by absolute amount
            contributions.sort(key=lambda x: abs(x.amount), reverse=True)
            return contributions
            
        except Exception as e:
            logger.error(f"Error getting process contributions: {e}")
            return []
    
    def get_flow_contributions(
        self,
        result,
        impact_category: o.Ref,
        min_share: float = 0.01
    ) -> List[ContributionItem]:
        """
        Get flow contributions to an impact category.
        
        Args:
            result: Calculation result
            impact_category: Impact category reference
            min_share: Minimum share to include
        
        Returns:
            List of flow contribution items
        
        Example:
            >>> flows = contributions.get_flow_contributions(result, gwp_ref)
            >>> top_flow = flows[0]
            >>> print(f"Top contributor: {top_flow.name} ({top_flow.share*100:.1f}%)")
        """
        try:
            raw_contributions = self.client.lcia_flow_contributions(
                result,
                impact_category
            )
            
            contributions = []
            for item in raw_contributions:
                if item.share >= min_share:
                    contributions.append(ContributionItem(
                        name=item.item.name if hasattr(item, 'item') else str(item),
                        amount=item.amount,
                        share=item.share,
                        ref=item.item if hasattr(item, 'item') else None
                    ))
            
            contributions.sort(key=lambda x: abs(x.amount), reverse=True)
            return contributions
            
        except Exception as e:
            logger.error(f"Error getting flow contributions: {e}")
            return []
    
    def get_top_contributors(
        self,
        result,
        impact_category: o.Ref,
        n: int = 5,
        contribution_type: str = 'process'
    ) -> List[ContributionItem]:
        """
        Get top N contributors to an impact.
        
        Args:
            result: Calculation result
            impact_category: Impact category reference
            n: Number of top contributors to return
            contribution_type: 'process' or 'flow'
        
        Returns:
            List of top N contributors
        
        Example:
            >>> top5 = contributions.get_top_contributors(result, gwp_ref, n=5)
            >>> print("Top 5 contributors to Global Warming:")
            >>> for i, c in enumerate(top5, 1):
            ...     print(f"  {i}. {c.name}: {c.share*100:.1f}%")
        """
        if contribution_type == 'process':
            all_contribs = self.get_process_contributions(result, impact_category, min_share=0)
        else:
            all_contribs = self.get_flow_contributions(result, impact_category, min_share=0)
        
        return all_contribs[:n]
    
    def get_contribution_summary(
        self,
        result,
        impact_categories: Optional[List[o.Ref]] = None
    ) -> Dict[str, List[ContributionItem]]:
        """
        Get contribution summary for multiple impact categories.
        
        Args:
            result: Calculation result
            impact_categories: List of impact categories (or None for all)
        
        Returns:
            Dictionary mapping category names to contribution lists
        
        Example:
            >>> summary = contributions.get_contribution_summary(result)
            >>> for category, contribs in summary.items():
            ...     print(f"\n{category}:")
            ...     for c in contribs[:3]:
            ...         print(f"  - {c.name}: {c.share*100:.1f}%")
        """
        summary = {}
        
        try:
            # Get all impacts if not specified
            if not impact_categories:
                impacts = result.get_total_impacts()
                impact_categories = [imp.impact_category for imp in impacts]
            
            for cat_ref in impact_categories:
                contribs = self.get_top_contributors(result, cat_ref, n=10)
                summary[cat_ref.name] = contribs
        
        except Exception as e:
            logger.error(f"Error getting contribution summary: {e}")
        
        return summary

