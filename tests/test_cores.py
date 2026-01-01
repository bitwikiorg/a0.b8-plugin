"""
WHY: To ensure Core Synapse deployments are validated and monitored correctly.
WHAT: Tests for category validation, deployment payloads, and completion watching.
HOW: Mocks BithubComms and filesystem; asserts strict adherence to the cores_registry.json contract.
"""

import pytest
import json
import os
from unittest.mock import MagicMock, patch, mock_open
from bithub.bithub_cores import BithubCores
from bithub.bithub_errors import BithubError

@pytest.fixture
def cores():
    with patch.dict(os.environ, {"BITHUB_USER_API_KEY": "dummy_key", "BITHUB_URL": "http://test.local"}):
        return BithubCores()

def test_deploy_only_success(cores):
    """Do: Deploy core. Verify: Result structure."""
    with patch.object(cores, 'create_public_topic') as mock_create, \
         patch("builtins.open", mock_open(read_data=json.dumps([{"id": 62}]))):
        mock_create.return_value = {"topic_id": 101, "id": 101}
        result = cores.deploy_only(title="Test", content="Content", category_id=62)
        assert result['topic_id'] == 101
        assert result['status'] == "deployed"

def test_deploy_only_failure(cores):
    """Guard: API failure. Verify: BithubError propagation."""
    with patch.object(cores, 'create_public_topic', side_effect=BithubError("Fail")), \
         patch("builtins.open", mock_open(read_data=json.dumps([{"id": 62}]))):
        with pytest.raises(BithubError):
            cores.deploy_only("T", "C", 62)

def test_watch_topic_success(cores):
    """Do: Watch topic. Verify: Reply returned."""
    with patch.object(cores, 'wait_for_reply', return_value={"id": 202}):
        result = cores.watch_topic(101, 200, timeout=30)
        assert result == {"id": 202}

def test_signal_completion_sanitized(cores):
    """Do: Signal completion. Verify: No private ID leakage."""
    with patch.object(cores, '_request') as mock_req:
        mock_req.return_value = {"id": 303}
        cores.signal_completion_sanitized(50, 999)
        args, kwargs = mock_req.call_args
        assert "999" not in kwargs['json_data']['raw']

def test_deploy_seed(cores):
    """Do: Deploy seed. Verify: Placeholder text."""
    with patch.object(cores, 'create_public_topic') as mock_create, \
         patch("builtins.open", mock_open(read_data=json.dumps([{"id": 62}]))):
        mock_create.return_value = {"topic_id": 100, "id": 101}
        cores.deploy_seed("Seed", 62)
        args, _ = mock_create.call_args
        assert "awaiting payload" in args[1]

def test_sync_cores(cores):
    """Do: Sync cores. Verify: Registry file write."""
    mock_resp = {"category_list": {"categories": [{"id": 10, "name": "Core A", "slug": "a"}]}}
    with patch.object(cores, '_request', return_value=mock_resp), \
         patch("builtins.open", mock_open()) as m:
        result = cores.sync_cores()
        assert len(result) == 1
        m().write.assert_called()
