"""
WHY: To ensure the Flash Synapse (Realtime Chat) connectivity is functional.
WHAT: Tests for chat channel retrieval and message transmission.
HOW: Mocks BithubComms chat methods; follows Guard -> Do -> Verify.
"""

import pytest
from unittest.mock import MagicMock
from bithub.bithub_comms import BithubComms

@pytest.fixture
def mock_comms():
    return MagicMock(spec=BithubComms)

def test_flash_synapse_connectivity(mock_comms):
    """Do: Fetch channels and send message. Verify: Correct channel_id usage."""
    mock_comms.get_chat_channels.return_value = {"chat_channels": [{"id": 1, "title": "General"}]}
    channels = mock_comms.get_chat_channels()
    mock_comms.send_chat_message(channel_id=channels["chat_channels"][0]["id"], message="Ping")
    mock_comms.send_chat_message.assert_called_with(channel_id=1, message="Ping")
