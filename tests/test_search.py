"""
Tests for SearchUtils class
"""
import pytest
from unittest.mock import MagicMock
import olca_schema as o
from openlca_ipc.search import SearchUtils


class TestSearchUtils:
    """Test suite for SearchUtils."""

    def test_search_utils_initialization(self, mock_ipc_client):
        """Test SearchUtils can be initialized."""
        search = SearchUtils(mock_ipc_client)
        assert search is not None
        assert search.client == mock_ipc_client

    def test_find_flows_with_results(self, mock_ipc_client):
        """Test find_flows returns matching flows."""
        # Mock flow descriptors
        flow_refs = [
            o.Ref(id="f1", name="Steel plate"),
            o.Ref(id="f2", name="Steel rod"),
        ]
        mock_ipc_client.get_descriptors.return_value = flow_refs

        search = SearchUtils(mock_ipc_client)
        results = search.find_flows(['steel'], max_results=5)

        assert len(results) == 2
        assert results[0].name == "Steel plate"

    def test_find_flow_single_result(self, mock_ipc_client):
        """Test find_flow returns single flow."""
        flow_ref = o.Ref(id="f1", name="Steel plate")
        mock_ipc_client.get_descriptors.return_value = [flow_ref]

        search = SearchUtils(mock_ipc_client)
        result = search.find_flow(['steel'])

        assert result is not None
        assert result.name == "Steel plate"

    def test_find_flow_no_results(self, mock_ipc_client):
        """Test find_flow returns None when no matches."""
        mock_ipc_client.get_descriptors.return_value = []

        search = SearchUtils(mock_ipc_client)
        result = search.find_flow(['nonexistent'])

        assert result is None

    def test_find_processes(self, mock_ipc_client):
        """Test find_processes returns matching processes."""
        process_refs = [
            o.Ref(id="p1", name="Steel production"),
            o.Ref(id="p2", name="Steel processing"),
        ]
        mock_ipc_client.get_descriptors.return_value = process_refs

        search = SearchUtils(mock_ipc_client)
        results = search.find_processes(['steel'], max_results=5)

        assert len(results) == 2
        assert results[0].name == "Steel production"

    def test_find_impact_method(self, mock_ipc_client):
        """Test find_impact_method returns matching method."""
        method_ref = o.Ref(id="m1", name="TRACI 2.1")
        mock_ipc_client.get_descriptors.return_value = [method_ref]

        search = SearchUtils(mock_ipc_client)
        result = search.find_impact_method(['TRACI'])

        assert result is not None
        assert result.name == "TRACI 2.1"

    def test_find_best_provider(self, mock_ipc_client, sample_flow):
        """Test find_best_provider returns provider process."""
        # Mock flow with default provider
        flow_with_provider = o.Flow()
        flow_with_provider.id = "flow-123"
        flow_with_provider.name = "Steel"

        provider_ref = o.Ref(id="p1", name="Steel producer")

        # Mock process search
        mock_ipc_client.get_descriptors.return_value = [provider_ref]

        search = SearchUtils(mock_ipc_client)
        provider = search.find_best_provider(sample_flow)

        # Should attempt to find a provider
        assert mock_ipc_client.get_descriptors.called
