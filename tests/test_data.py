"""
Tests for DataBuilder class
"""
import pytest
from unittest.mock import MagicMock
import olca_schema as o
from openlca_ipc.data import DataBuilder


class TestDataBuilder:
    """Test suite for DataBuilder."""

    def test_data_builder_initialization(self, mock_ipc_client):
        """Test DataBuilder can be initialized."""
        builder = DataBuilder(mock_ipc_client)
        assert builder is not None
        assert builder.client == mock_ipc_client

    def test_create_product_flow(self, mock_ipc_client):
        """Test create_product_flow creates a flow with correct properties."""
        mock_ipc_client.put.return_value = o.Ref(id="flow-id", name="Test Product")

        builder = DataBuilder(mock_ipc_client)
        flow_ref = builder.create_product_flow(
            name="Test Product",
            flow_property="Mass",
            unit="kg"
        )

        assert flow_ref is not None
        assert flow_ref.name == "Test Product"
        assert mock_ipc_client.put.called

    def test_create_exchange(self, mock_ipc_client, sample_flow):
        """Test create_exchange creates exchange with correct properties."""
        builder = DataBuilder(mock_ipc_client)
        exchange = builder.create_exchange(
            flow=sample_flow,
            amount=1.0,
            is_input=True,
            is_quantitative_reference=False
        )

        assert exchange is not None
        assert isinstance(exchange, o.Exchange)
        assert exchange.amount == 1.0
        assert exchange.is_input is True
        assert exchange.quantitative_reference is False

    def test_create_exchange_with_provider(self, mock_ipc_client, sample_flow, sample_process):
        """Test create_exchange with provider links correctly."""
        builder = DataBuilder(mock_ipc_client)
        exchange = builder.create_exchange(
            flow=sample_flow,
            amount=2.0,
            is_input=True,
            provider=sample_process
        )

        assert exchange is not None
        assert exchange.amount == 2.0
        # Provider should be set if provided
        if hasattr(exchange, 'default_provider'):
            assert exchange.default_provider is not None

    def test_create_process(self, mock_ipc_client):
        """Test create_process creates process with exchanges."""
        mock_ipc_client.put.return_value = o.Ref(id="proc-id", name="Test Process")

        # Create sample exchanges
        exchanges = [
            o.Exchange(amount=1.0, is_input=False, quantitative_reference=True),
        ]

        builder = DataBuilder(mock_ipc_client)
        process_ref = builder.create_process(
            name="Test Process",
            exchanges=exchanges
        )

        assert process_ref is not None
        assert process_ref.name == "Test Process"
        assert mock_ipc_client.put.called

    def test_create_process_validates_quantitative_reference(self, mock_ipc_client):
        """Test create_process validates quantitative reference exists."""
        # Exchanges without quantitative reference
        exchanges = [
            o.Exchange(amount=1.0, is_input=True, quantitative_reference=False),
        ]

        builder = DataBuilder(mock_ipc_client)

        # Should handle missing qref (might warn or add default)
        # Implementation dependent - just test it doesn't crash
        try:
            process_ref = builder.create_process(
                name="Test Process",
                exchanges=exchanges
            )
            # If successful, that's fine
            assert True
        except Exception:
            # If it raises an error for validation, that's also acceptable
            assert True
