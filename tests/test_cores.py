"""
Title: test_cores.py Test
Description: Test suite for cores.
"""

import pytest
import os
from unittest.mock import MagicMock, patch
from bithub.bithub_cores import BithubCores
from bithub.bithub_errors import BithubError

@pytest.fixture
def mock_cores():
    """
    Fixture to create a BithubCores instance with mocked methods.
    We mock create_public_topic and wait_for_reply because deploy_only and watch_topic
    are expected to wrap these inherited methods.
    We also mock _request to satisfy the requirement of mocking the base communication layer.
    """
    # Fixed: Use BITHUB_URL instead of BITHUB_API_URL
    with (
        patch.dict(os.environ, {"BITHUB_USER_API_KEY": "dummy_key", "BITHUB_URL": "http://test.local"}),
        patch('bithub.bithub_cores.BithubCores.create_public_topic') as mock_create,
        patch('bithub.bithub_cores.BithubCores.wait_for_reply') as mock_wait,
        patch('bithub.bithub_cores.BithubCores._request') as mock_req
    ):

        # Initialize without arguments as per BithubComms definition
        cores = BithubCores()

        # Attach mocks to the instance for easy access in tests
        cores.create_public_topic = mock_create
        cores.wait_for_reply = mock_wait
        cores._request = mock_req

        yield cores, mock_create, mock_wait, mock_req

def test_deploy_only_success(mock_cores):
    """
    Test that deploy_only returns the correct dict structure when create_public_topic succeeds.
    """
    cores, mock_create, _, _ = mock_cores

    # Setup expected success response
    expected_response = {
        'id': 101,
        'topic_slug': 'test-topic',
        'title': 'Test Title',
        'topic_id': 101
    }
    mock_create.return_value = expected_response

    # Execute
    result = cores.deploy_only(
        title="Test Title",
        content="Test Content",
        category_id=5,
        tags=["test"]
    )

    # Verify
    assert result['topic_id'] == 101
    assert result['post_id'] == 101
    assert result['status'] == "deployed"

    # UPDATED ASSERTION: Tags should NOT be prepended to content anymore
    mock_create.assert_called_once_with(
        "Test Title",
        "Test Content",
        5
    )

def test_deploy_only_failure(mock_cores):
    """
    Test that deploy_only raises BithubError when create_public_topic fails.
    """
    cores, mock_create, _, _ = mock_cores

    # Setup failure scenario
    mock_create.side_effect = BithubError("Failed to create topic")

    # Execute & Verify
    with pytest.raises(BithubError) as excinfo:
        cores.deploy_only("Title", "Content", 1, [])

    assert "Failed to create topic" in str(excinfo.value)

def test_watch_topic_success(mock_cores):
    """
    Test that watch_topic returns the reply when wait_for_reply succeeds.
    """
    cores, _, mock_wait, _ = mock_cores

    # Setup expected reply
    expected_reply = {
        'id': 202,
        'raw': 'This is a reply',
        'topic_id': 101
    }
    mock_wait.return_value = expected_reply

    # Execute
    result = cores.watch_topic(topic_id=101, last_post_id=200, timeout=30)

    # Verify
    assert result == expected_reply
    mock_wait.assert_called_once_with(101, 200, timeout=30)

def test_watch_topic_timeout(mock_cores):
    """
    Test that watch_topic returns None when wait_for_reply returns None (timeout).
    """
    cores, _, mock_wait, _ = mock_cores

    # Setup timeout scenario (returns None)
    mock_wait.return_value = None

    # Execute
    result = cores.watch_topic(topic_id=101, last_post_id=200, timeout=10)

    # Verify
    assert result is None
    mock_wait.assert_called_once_with(101, 200, timeout=10)

def test_signal_completion_sanitized(mock_cores):
    """
    Test that signal_completion_sanitized posts the correct message without leaking private IDs.
    """
    cores, _, _, mock_req = mock_cores

    # Setup mock response
    mock_req.return_value = {'id': 303, 'topic_id': 50}

    # Execute
    public_channel_id = 50
    private_topic_id = 999
    result = cores.signal_completion_sanitized(public_channel_id, private_topic_id)

    # Verify
    assert result['id'] == 303

    # Check that _request was called with the correct payload
    # The message MUST NOT contain the private_topic_id (999)
    expected_payload = {
        "topic_id": public_channel_id,
        "raw": "✅ Core Task Completed. [Private Context]"
    }
    mock_req.assert_called_once_with("POST", "/posts.json", json_data=expected_payload)

def test_deploy_seed(mock_cores):
    """Test deploy_seed creates a topic with placeholder text."""
    cores, mock_create, _, _ = mock_cores
    
    mock_create.return_value = {'topic_id': 100, 'id': 101}
    
    result = cores.deploy_seed("Seed Title", category_id=5)
    
    assert result == {"topic_id": 100, "post_id": 101}
    mock_create.assert_called_once()
    # Verify placeholder text was used
    args, _ = mock_create.call_args
    assert "awaiting payload" in args[1]

def test_refine_seed(mock_cores):
    """Test refine_seed calls update_post."""
    cores, _, _, mock_req = mock_cores
    
    mock_req.return_value = {"success": True}
    
    cores.refine_seed(101, "Actual Content")
    
    mock_req.assert_called_with("PUT", "/posts/101.json", json_data={"post": {"raw": "Actual Content"}})

def test_deploy_core_sync(mock_cores):
    """Test deploy_core with sync=True calls watch_topic."""
    cores, mock_create, _, _ = mock_cores
    
    with patch.object(cores, 'deploy_only') as mock_deploy, \
         patch.object(cores, 'watch_topic') as mock_watch:
        
        mock_deploy.return_value = {'topic_id': 1, 'post_id': 10, 'status': 'deployed'}
        mock_watch.return_value = {'id': 11, 'raw': 'Result'}
        
        # FIX: Explicitly pass timeout=45 to match assertion
        result = cores.deploy_core("Title", "Content", sync=True, timeout=45)
        
        assert result == {'id': 11, 'raw': 'Result'}
        mock_watch.assert_called_once_with(1, 10, 45) # Default timeout

def test_deploy_core_async(mock_cores):
    """Test deploy_core with sync=False does not call watch_topic."""
    cores, _, _, _ = mock_cores
    
    with patch.object(cores, 'deploy_only') as mock_deploy, \
         patch.object(cores, 'watch_topic') as mock_watch:
        
        mock_deploy.return_value = {'topic_id': 1, 'post_id': 10, 'status': 'deployed'}
        
        result = cores.deploy_core("Title", "Content", sync=False)
        
        assert result == {'topic_id': 1, 'post_id': 10, 'status': 'deployed'}
        mock_watch.assert_not_called()

# --- NEW BURN TESTS ---

def test_deploy_core_burn_success(mock_cores):
    """Test deploy_core with burn=True deletes topic after sync."""
    cores, _, _, _ = mock_cores
    
    with patch.object(cores, 'deploy_only') as mock_deploy, \
         patch.object(cores, 'watch_topic') as mock_watch, \
         patch.object(cores, 'delete_topic') as mock_delete:
        
        mock_deploy.return_value = {'topic_id': 100, 'post_id': 10, 'status': 'deployed'}
        mock_watch.return_value = {'id': 11, 'raw': 'Result'}
        
        result = cores.deploy_core("Title", "Content", sync=True, burn=True)
        
        assert result == {'id': 11, 'raw': 'Result'}
        mock_delete.assert_called_once_with(100)

def test_deploy_core_burn_no_sync(mock_cores):
    """Test deploy_core with burn=True but sync=False does NOT delete topic."""
    cores, _, _, _ = mock_cores
    
    with patch.object(cores, 'deploy_only') as mock_deploy, \
         patch.object(cores, 'watch_topic') as mock_watch, \
         patch.object(cores, 'delete_topic') as mock_delete:
        
        mock_deploy.return_value = {'topic_id': 100, 'post_id': 10, 'status': 'deployed'}
        
        result = cores.deploy_core("Title", "Content", sync=False, burn=True)
        
        assert result['status'] == 'deployed'
        mock_watch.assert_not_called()
        mock_delete.assert_not_called()
