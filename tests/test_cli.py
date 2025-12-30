"""
Title: test_cli.py Test
Description: Test suite for cli.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
import sys
import json
import argparse
from bithub.bithub import handle_agent
from bithub.bithub_errors import BithubAuthError

@pytest.fixture
def mock_comms_class():
    """Patches BithubComms in the bithub module."""
    with patch.dict(os.environ, {"BITHUB_USER_API_KEY": "test_key"}), patch("bithub.bithub.BithubComms") as mock:
        yield mock

def test_agent_success(mock_comms_class, capsys):
    """Test successful agent interaction flow."""
    # Setup Mock Comms Instance
    mock_instance = mock_comms_class.return_value
    
    # 1. Mock send_private_message success
    mock_instance.send_private_message.return_value = {
        "topic_id": 123,
        "id": 456
    }
    
    # 2. Mock wait_for_reply success
    mock_instance.wait_for_reply.return_value = {
        "id": 457,
        "cooked": "<p>Mission Accomplished</p>"
    }
    
    # 3. Mock sanitize_html
    mock_instance.sanitize_html.return_value = "Mission Accomplished"
    
    # Prepare Args
    args = argparse.Namespace(
        bot_username="@testbot",
        message="Do the thing",
        timeout=60
    )
    
    # Execute
    handle_agent(args)
    
    # Verification Steps
    # 1. Verify send called with correct args
    mock_instance.send_private_message.assert_called_once()
    call_args = mock_instance.send_private_message.call_args
    assert call_args[0][0] == ["@testbot"]
    assert "Do the thing" in call_args[0][2]
    
    # 2. Verify wait called with correct topic_id
    mock_instance.wait_for_reply.assert_called_once_with(123, 456, timeout=60)
    
    # 3. Verify stdout output
    captured = capsys.readouterr()
    assert "Mission Accomplished" in captured.out

def test_agent_send_failure(mock_comms_class, capsys):
    """Test failure during message sending."""
    mock_instance = mock_comms_class.return_value
    
    # Mock send failure (Raise Exception instead of return dict)
    mock_instance.send_private_message.side_effect = BithubAuthError("Forbidden")
    
    args = argparse.Namespace(
        bot_username="@testbot",
        message="Fail me",
        timeout=60
    )
    
    # Expect sys.exit(1)
    with pytest.raises(SystemExit) as excinfo:
        handle_agent(args)
    
    assert excinfo.value.code == 1
    
    # Verification Steps
    # 1. Verify wait was NOT called
    mock_instance.wait_for_reply.assert_not_called()
    
    # 2. Verify error output
    captured = capsys.readouterr()
    # The new handler prints JSON with "type": "AuthError" and "message": "Forbidden"
    assert "AuthError" in captured.out
    assert "Forbidden" in captured.out
