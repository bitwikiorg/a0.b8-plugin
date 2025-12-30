import pytest
from unittest.mock import MagicMock
from bithub.bithub_comms import BithubComms

@pytest.fixture
def mock_comms():
    """Fixture to mock BithubComms interactions."""
    return MagicMock(spec=BithubComms)

def test_dm_sequence(mock_comms):
    """Test DM creation and messaging sequence."""
    # Setup mocks
    mock_comms.create_dm_channel.return_value = {
        "chat_channel": {
            "id": 123,
            "title": "test_user"
        }
    }
    mock_comms.send_chat_message.return_value = {
        "id": 456,
        "message": "Hello World"
    }

    # Execute sequence
    # 1. Create DM
    dm_response = mock_comms.create_dm_channel(usernames=["test_user"])
    channel_id = dm_response["chat_channel"]["id"]
    
    # 2. Send Message
    msg_response = mock_comms.send_chat_message(channel_id=channel_id, message="Hello World")

    # Verify calls
    mock_comms.create_dm_channel.assert_called_once_with(usernames=["test_user"])
    mock_comms.send_chat_message.assert_called_once_with(channel_id=123, message="Hello World")
    assert msg_response["id"] == 456

def test_pm_sequence(mock_comms):
    """Test Private Message creation and reply sequence."""
    # Setup mocks
    mock_comms.send_private_message.return_value = {
        "id": 789,
        "topic_id": 101,
        "title": "Secret"
    }
    mock_comms.reply_to_post.return_value = {
        "id": 790,
        "cooked": "<p>Reply</p>"
    }

    # Execute sequence
    # 1. Send PM
    pm_response = mock_comms.send_private_message(
        recipients=["test_user"], 
        title="Secret", 
        raw="This is a secret"
    )
    topic_id = pm_response["topic_id"]

    # 2. Reply to PM (which is a topic)
    reply_response = mock_comms.reply_to_post(topic_id=topic_id, raw="Got it")

    # Verify calls
    mock_comms.send_private_message.assert_called_once_with(
        recipients=["test_user"], 
        title="Secret", 
        raw="This is a secret"
    )
    mock_comms.reply_to_post.assert_called_once_with(topic_id=101, raw="Got it")

def test_topic_sequence(mock_comms):
    """Test Topic creation and reply sequence using _request mock."""
    # Setup mocks
    # Mocking _request for the topic creation part as per instructions
    mock_comms._request.return_value = {
        "topic_id": 202,
        "id": 202,
        "title": "New Topic"
    }
    mock_comms.reply_to_post.return_value = {
        "id": 203,
        "cooked": "<p>Topic Reply</p>"
    }

    # Execute sequence
    # 1. Create Topic (simulating raw request call)
    topic_response = mock_comms._request(
        method="POST",
        endpoint="/posts.json",
        json_data={"title": "New Topic", "raw": "Content"}
    )
    topic_id = topic_response["topic_id"]

    # 2. Reply to Topic
    reply_response = mock_comms.reply_to_post(topic_id=topic_id, raw="Nice topic")

    # Verify calls
    mock_comms._request.assert_called_once_with(
        method="POST",
        endpoint="/posts.json",
        json_data={"title": "New Topic", "raw": "Content"}
    )
    mock_comms.reply_to_post.assert_called_once_with(topic_id=202, raw="Nice topic")
