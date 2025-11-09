"""
Pytest configuration and fixtures for openlca_ipc tests
"""
import pytest
from unittest.mock import Mock, MagicMock
import olca_schema as o


@pytest.fixture
def mock_ipc_client():
    """Mock olca.Client for testing without openLCA server."""
    mock_client = MagicMock()

    # Mock basic client methods
    mock_client.get_descriptors.return_value = []
    mock_client.get.return_value = None
    mock_client.put.return_value = o.Ref(id="test-id", name="Test Object")
    mock_client.calculate.return_value = o.Ref(id="result-id", name="Test Result")

    return mock_client


@pytest.fixture
def sample_flow():
    """Create a sample flow for testing."""
    flow = o.Flow()
    flow.id = "flow-123"
    flow.name = "Steel"
    flow.flow_type = o.FlowType.PRODUCT_FLOW
    return flow


@pytest.fixture
def sample_process():
    """Create a sample process for testing."""
    process = o.Process()
    process.id = "process-123"
    process.name = "Steel production"
    process.process_type = o.ProcessType.UNIT_PROCESS
    return process


@pytest.fixture
def sample_product_system():
    """Create a sample product system for testing."""
    system = o.ProductSystem()
    system.id = "system-123"
    system.name = "Steel system"
    return system


@pytest.fixture
def sample_impact_method():
    """Create a sample impact method for testing."""
    method = o.ImpactMethod()
    method.id = "method-123"
    method.name = "TRACI 2.1"
    return method


@pytest.fixture
def sample_result():
    """Create a sample calculation result for testing."""
    result = MagicMock()
    result.id = "result-123"
    return result
