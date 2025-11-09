"""
Tests for OLCAClient class
"""
import pytest
from unittest.mock import patch, MagicMock
from openlca_ipc import OLCAClient


class TestOLCAClient:
    """Test suite for OLCAClient."""

    def test_client_initialization(self):
        """Test client can be initialized with default parameters."""
        with patch('openlca_ipc.client.olca.Client'):
            client = OLCAClient(port=8080)
            assert client is not None
            assert hasattr(client, 'search')
            assert hasattr(client, 'data')
            assert hasattr(client, 'systems')
            assert hasattr(client, 'calculate')
            assert hasattr(client, 'results')
            assert hasattr(client, 'contributions')
            assert hasattr(client, 'uncertainty')
            assert hasattr(client, 'parameters')
            assert hasattr(client, 'export')

    def test_client_has_utility_modules(self):
        """Test client has all expected utility modules."""
        with patch('openlca_ipc.client.olca.Client'):
            client = OLCAClient(port=8080)

            # Check all utility modules are present
            from openlca_ipc.search import SearchUtils
            from openlca_ipc.data import DataBuilder
            from openlca_ipc.systems import SystemBuilder
            from openlca_ipc.calculations import CalculationManager
            from openlca_ipc.results import ResultsAnalyzer
            from openlca_ipc.contributions import ContributionAnalyzer
            from openlca_ipc.uncertainty import UncertaintyAnalyzer
            from openlca_ipc.parameters import ParameterManager
            from openlca_ipc.export import ExportManager

            assert isinstance(client.search, SearchUtils)
            assert isinstance(client.data, DataBuilder)
            assert isinstance(client.systems, SystemBuilder)
            assert isinstance(client.calculate, CalculationManager)
            assert isinstance(client.results, ResultsAnalyzer)
            assert isinstance(client.contributions, ContributionAnalyzer)
            assert isinstance(client.uncertainty, UncertaintyAnalyzer)
            assert isinstance(client.parameters, ParameterManager)
            assert isinstance(client.export, ExportManager)

    def test_context_manager(self):
        """Test client works as context manager."""
        with patch('openlca_ipc.client.olca.Client'):
            with OLCAClient(port=8080) as client:
                assert client is not None
                assert hasattr(client, 'search')

    def test_client_custom_port(self):
        """Test client accepts custom port."""
        with patch('openlca_ipc.client.olca.Client') as mock_client_class:
            client = OLCAClient(port=9090)
            assert client is not None

    @patch('openlca_ipc.client.olca.Client')
    def test_test_connection_success(self, mock_client_class):
        """Test connection test method when successful."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client = OLCAClient(port=8080)
        # Mock successful connection
        result = client.test_connection()
        # Should return True or not raise exception
        assert result is not None
