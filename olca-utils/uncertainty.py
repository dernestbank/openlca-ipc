# ============================================================================
# FILE: olca_utils/uncertainty.py
# ============================================================================

"""
Monte Carlo simulation and uncertainty analysis.
"""

import numpy as np
from typing import List, Dict, Optional


@dataclass
class UncertaintyResult:
    """
    Results of uncertainty analysis.
    
    Attributes:
        impact_name: Impact category name
        values: Array of simulation values
        mean: Mean value
        std: Standard deviation
        median: Median value
        percentile_5: 5th percentile
        percentile_95: 95th percentile
        cv: Coefficient of variation (std/mean)
    """
    impact_name: str
    values: np.ndarray
    mean: float
    std: float
    median: float
    percentile_5: float
    percentile_95: float
    cv: float


class UncertaintyAnalyzer:
    """
    Utilities for Monte Carlo simulation and uncertainty analysis.
    
    Provides methods for running simulations, analyzing distributions,
    and quantifying uncertainty in LCA results.
    """
    
    def __init__(self, client: ipc.Client):
        self.client = client
    
    def run_monte_carlo(
        self,
        system: o.Ref,
        impact_method: o.ImpactMethod,
        iterations: int = 1000,
        amount: float = 1.0,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, UncertaintyResult]:
        """
        Run Monte Carlo simulation.
        
        Args:
            system: Product system reference
            impact_method: Impact method
            iterations: Number of simulation runs
            amount: Reference amount
            progress_callback: Optional callback(current, total)
        
        Returns:
            Dictionary mapping impact names to uncertainty results
        
        Example:
            >>> def progress(current, total):
            ...     print(f"Progress: {current}/{total}")
            >>> 
            >>> results = uncertainty.run_monte_carlo(
            ...     system=my_system,
            ...     impact_method=traci,
            ...     iterations=1000,
            ...     progress_callback=progress
            ... )
            >>> 
            >>> for name, result in results.items():
            ...     print(f"{name}:")
            ...     print(f"  Mean: {result.mean:.4e}")
            ...     print(f"  95% CI: [{result.percentile_5:.4e}, {result.percentile_95:.4e}]")
        """
        # Create simulation setup
        setup = o.CalculationSetup()
        setup.calculation_type = o.CalculationType.MONTE_CARLO_SIMULATION
        setup.target = system
        setup.impact_method = impact_method.to_ref()
        setup.amount = amount
        
        # Create simulator
        simulator = self.client.simulator(setup)
        logger.info(f"Starting Monte Carlo simulation with {iterations} iterations")
        
        # Store results for each impact category
        impact_values = {}
        
        try:
            for i in range(iterations):
                # Run simulation
                result = self.client.next_simulation(simulator)
                
                # Collect impact values
                for impact_result in result.impact_results:
                    cat_name = impact_result.impact_category.name
                    value = (impact_result.amount if hasattr(impact_result, 'amount')
                            else impact_result.value if hasattr(impact_result, 'value')
                            else 0)
                    
                    if cat_name not in impact_values:
                        impact_values[cat_name] = []
                    impact_values[cat_name].append(value)
                
                # Progress callback
                if progress_callback and (i + 1) % 100 == 0:
                    progress_callback(i + 1, iterations)
            
            # Analyze results
            uncertainty_results = {}
            for impact_name, values in impact_values.items():
                arr = np.array(values)
                
                uncertainty_results[impact_name] = UncertaintyResult(
                    impact_name=impact_name,
                    values=arr,
                    mean=np.mean(arr),
                    std=np.std(arr),
                    median=np.median(arr),
                    percentile_5=np.percentile(arr, 5),
                    percentile_95=np.percentile(arr, 95),
                    cv=np.std(arr) / np.mean(arr) if np.mean(arr) != 0 else 0
                )
            
            logger.info(f"Monte Carlo simulation complete")
            return uncertainty_results
            
        finally:
            # Always dispose simulator
            self.client.dispose(simulator)
    
    def compare_with_uncertainty(
        self,
        system1: o.Ref,
        system2: o.Ref,
        impact_method: o.ImpactMethod,
        iterations: int = 1000
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare two systems with uncertainty analysis.
        
        Args:
            system1: First product system
            system2: Second product system
            impact_method: Impact method
            iterations: Number of Monte Carlo iterations
        
        Returns:
            Dictionary with comparison statistics
        
        Example:
            >>> comparison = uncertainty.compare_with_uncertainty(
            ...     pet_system, pc_system, traci, iterations=1000
            ... )
            >>> 
            >>> for impact, stats in comparison.items():
            ...     print(f"{impact}:")
            ...     print(f"  System 1 mean: {stats['system1_mean']:.4e}")
            ...     print(f"  System 2 mean: {stats['system2_mean']:.4e}")
            ...     print(f"  Significant difference: {stats['significantly_different']}")
        """
        # Run simulations for both systems
        results1 = self.run_monte_carlo(system1, impact_method, iterations)
        results2 = self.run_monte_carlo(system2, impact_method, iterations)
        
        comparison = {}
        
        for impact_name in results1.keys():
            if impact_name in results2:
                r1 = results1[impact_name]
                r2 = results2[impact_name]
                
                # Perform t-test
                from scipy import stats
                t_stat, p_value = stats.ttest_ind(r1.values, r2.values)
                
                comparison[impact_name] = {
                    'system1_mean': r1.mean,
                    'system1_std': r1.std,
                    'system1_ci_95': (r1.percentile_5, r1.percentile_95),
                    'system2_mean': r2.mean,
                    'system2_std': r2.std,
                    'system2_ci_95': (r2.percentile_5, r2.percentile_95),
                    'difference': r2.mean - r1.mean,
                    'percent_difference': ((r2.mean - r1.mean) / abs(r1.mean) * 100 
                                          if r1.mean != 0 else 0),
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significantly_different': p_value < 0.05
                }
        
        return comparison

