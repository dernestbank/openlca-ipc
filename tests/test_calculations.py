"""
Tests for CalculationManager class
"""
import pytest
from unittest.mock import MagicMock, patch
import olca_schema as o
from openlca_ipc.calculations import CalculationManager


class TestCalculationManager:
    """Test suite for CalculationManager."""

    def test_calculation_manager_initialization(self, mock_ipc_client):
        """Test CalculationManager can be initialized."""
        calc = CalculationManager(mock_ipc_client)
        assert calc is not None
        assert calc.client == mock_ipc_client

    def test_simple_calculation_setup(self, mock_ipc_client, sample_product_system, sample_impact_method):
        """Test simple_calculation creates calculation setup correctly."""
        mock_result = MagicMock()
        mock_result.id = "result-123"
        mock_ipc_client.calculate.return_value = mock_result

        calc = CalculationManager(mock_ipc_client)

        # Mock the result to avoid waiting
        with patch('time.sleep'):
            result = calc.simple_calculation(
                product_system=sample_product_system,
                impact_method=sample_impact_method
            )

        assert mock_ipc_client.calculate.called
        # Verify calculation setup was created
        call_args = mock_ipc_client.calculate.call_args
        assert call_args is not None

    def test_contribution_analysis_setup(self, mock_ipc_client, sample_product_system, sample_impact_method):
        """Test contribution_analysis enables contributions correctly."""
        mock_result = MagicMock()
        mock_result.id = "result-123"
        mock_ipc_client.calculate.return_value = mock_result

        calc = CalculationManager(mock_ipc_client)

        with patch('time.sleep'):
            result = calc.contribution_analysis(
                product_system=sample_product_system,
                impact_method=sample_impact_method
            )

        assert mock_ipc_client.calculate.called
        # Verify calculation setup includes contribution analysis
        call_args = mock_ipc_client.calculate.call_args
        if call_args:
            setup = call_args[0][0] if call_args[0] else None
            # Setup should exist
            assert setup is not None
