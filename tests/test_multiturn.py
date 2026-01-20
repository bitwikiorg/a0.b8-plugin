"""
WHY: To verify complex, multi-turn synaptic interactions (Chat/PM sequences).
WHAT: Tests for sequential DM and PM creation and replies.
HOW: Mocks BithubComms; follows Guard -> Do -> Verify to assert interaction flow.
"""

import pytest
from unittest.mock import MagicMock
from bithub.bithub_comms import BithubComms

@pytest.fixture
def mock_comms():
    return MagicMock(spec=BithubComms)

def test_pm_sequence(mock_comms):
    """Do: Send PM and reply. Verify: topic_id propagation."""
    mock_comms.send_private_message.return_value = {"topic_id": 101}
    resp = mock_comms.send_private_message(recipients=["u1"], title="T", raw="R")
    mock_comms.reply_to_post(topic_id=resp["topic_id"], raw="Reply")
    mock_comms.reply_to_post.assert_called_with(topic_id=101, raw="Reply")

def test_dm_sequence(mock_comms):
    """Do: Create DM and send chat. Verify: channel_id propagation."""
    mock_comms.create_dm_channel.return_value = {"chat_channel": {"id": 123}}
    resp = mock_comms.create_dm_channel(usernames=["u1"])
    mock_comms.send_chat_message(channel_id=resp["chat_channel"]["id"], message="Hi")
    mock_comms.send_chat_message.assert_called_with(channel_id=123, message="Hi")
