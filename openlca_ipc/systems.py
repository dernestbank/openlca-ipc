# ============================================================================
# FILE: olca_utils/systems.py
# ============================================================================

"""
Product system creation and management.
"""

from typing import Optional, Union
import logging
import olca_schema as o
import olca_ipc as ipc

logger = logging.getLogger(__name__)


class SystemBuilder:
    """
    Utilities for creating and managing product systems.
    """
    
    def __init__(self, client: ipc.Client):
        self.client = client
    
    def create_product_system(
        self,
        process: Union[o.Process, o.Ref],
        name: Optional[str] = None,
        default_providers: str = 'prefer',
        preferred_type: str = 'LCI_RESULT'
    ) -> Optional[o.Ref]:
        """
        Create a product system from a process.
        
        Args:
            process: Process object or reference
            name: Optional custom name
            default_providers: 'prefer', 'only', or 'ignore'
            preferred_type: 'LCI_RESULT' or 'UNIT_PROCESS'
        
        Returns:
            Product system reference
        
        Example:
            >>> system = systems.create_product_system(
            ...     process=my_process,
            ...     default_providers='prefer'
            ... )
        """
        try:
            # Pass the process object directly
            system_ref = self.client.create_product_system(process)
            
            if system_ref and name:
                # Update name if provided
                system = self.client.get(o.ProductSystem, system_ref.id)
                system.name = name
                self.client.update(system)
            
            logger.info(f"Created product system: {system_ref.name if system_ref else 'Unknown'}")
            return system_ref
            
        except Exception as e:
            logger.error(f"Failed to create product system: {e}")
            return None

