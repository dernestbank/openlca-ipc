# ============================================================================
# FILE: olca_utils/data.py
# ============================================================================

"""
Data creation and building utilities.
"""

import logging
from typing import List, Tuple, Optional, Union
import uuid
import olca_schema as o
import olca_ipc as ipc

logger = logging.getLogger(__name__)


class DataBuilder:
    """
    Utilities for creating and managing openLCA data entities.
    
    Provides high-level methods for creating flows, processes, and exchanges
    with automatic linking and validation.
    """
    
    def __init__(self, client: ipc.Client):
        self.client = client
        self._mass_prop = None
        self._kg_unit = None
    
    @property
    def mass_property(self) -> o.FlowProperty:
        """Get or cache the Mass flow property."""
        if not self._mass_prop:
            self._mass_prop = self.client.get(o.FlowProperty, name="Mass")
            if not self._mass_prop:
                raise ValueError("Mass flow property not found in database")
        return self._mass_prop
    
    @property
    def kg_unit(self) -> o.Unit:
        """Get or cache the kg unit."""
        if not self._kg_unit:
            mass_prop = self.mass_property
            unit_group = self.client.get(o.UnitGroup, mass_prop.unit_group.id)
            self._kg_unit = next(
                (u for u in unit_group.units if u.name == "kg"),
                unit_group.units[0]
            )
        return self._kg_unit
    
    def create_product_flow(
        self,
        name: str,
        description: str = ""
    ) -> o.Flow:
        """
        Create a new product flow.
        
        Args:
            name: Flow name
            description: Optional description
        
        Returns:
            Created flow object
        
        Example:
            >>> flow = data.create_product_flow("Steel plate", "1mm thick")
            >>> print(flow.id)
        """
        flow = o.Flow()
        flow.id = str(uuid.uuid4())
        flow.name = name
        flow.description = description
        flow.flow_type = o.FlowType.PRODUCT_FLOW
        
        # Add mass property
        flow.flow_properties = [
            o.FlowPropertyFactor(
                flow_property=o.Ref(
                    id=self.mass_property.id,
                    name=self.mass_property.name,
                    ref_type=o.RefType.FlowProperty
                ),
                conversion_factor=1.0,
                is_ref_flow_property=True
            )
        ]
        
        self.client.put(flow)
        logger.info(f"Created product flow: {name}")
        return flow
    
    def create_exchange(
        self,
        flow: Union[o.Flow, o.Ref],
        amount: float,
        is_input: bool,
        is_quantitative_reference: bool = False,
        provider: Optional[o.Ref] = None
    ) -> o.Exchange:
        """
        Create an exchange for a process.
        
        Args:
            flow: Flow or flow reference
            amount: Amount in kg
            is_input: True for input, False for output
            is_quantitative_reference: True if this is the process output
            provider: Optional provider process reference
        
        Returns:
            Exchange object
        
        Example:
            >>> steel_flow = search.find_flow(['steel'])
            >>> steel_provider = search.find_best_provider(steel_flow)
            >>> exchange = data.create_exchange(
            ...     steel_flow, 
            ...     amount=1.0, 
            ...     is_input=True,
            ...     provider=steel_provider
            ... )
        """
        ex = o.Exchange()
        
        # Handle flow reference
        if isinstance(flow, o.Ref):
            ex.flow = flow
        elif isinstance(flow, o.Flow):
            ex.flow = o.Ref(
                id=flow.id,
                name=flow.name,
                ref_type=o.RefType.Flow
            )
        else:
            raise TypeError(f"Flow must be Flow or Ref, not {type(flow)}")
        
        ex.amount = amount
        ex.unit = o.Ref(
            id=self.kg_unit.id,
            name=self.kg_unit.name,
            ref_type=o.RefType.Unit
        )
        ex.flow_property = o.Ref(
            id=self.mass_property.id,
            name=self.mass_property.name,
            ref_type=o.RefType.FlowProperty
        )
        ex.is_input = is_input
        ex.is_quantitative_reference = is_quantitative_reference
        
        # Link provider
        if provider:
            if isinstance(provider, o.Ref):
                ex.default_provider = provider
            elif hasattr(provider, 'id'):
                ex.default_provider = o.Ref(
                    id=provider.id,
                    name=provider.name,
                    ref_type=o.RefType.Process
                )
        
        return ex
    
    def create_process(
        self,
        name: str,
        description: str = "",
        exchanges: Optional[List[o.Exchange]] = None
    ) -> o.Process:
        """
        Create a unit process.
        
        Args:
            name: Process name
            description: Optional description
            exchanges: List of exchanges (must include exactly one qref)
        
        Returns:
            Created process object
        
        Example:
            >>> process = data.create_process(
            ...     name="Steel production",
            ...     description="Basic oxygen furnace",
            ...     exchanges=[input_ex, output_ex]
            ... )
        """
        process = o.Process()
        process.id = str(uuid.uuid4())
        process.name = name
        process.description = description
        process.process_type = o.ProcessType.UNIT_PROCESS
        
        if exchanges:
            # Set internal IDs
            for i, ex in enumerate(exchanges, start=1):
                ex.internal_id = i
            
            process.exchanges = exchanges
            process.last_internal_id = len(exchanges)
            
            # Validate quantitative reference
            qref_count = sum(1 for ex in exchanges if ex.is_quantitative_reference)
            if qref_count != 1:
                logger.warning(
                    f"Process {name} has {qref_count} qrefs (should be 1)"
                )
        
        self.client.put(process)
        logger.info(f"Created process: {name}")
        return process
