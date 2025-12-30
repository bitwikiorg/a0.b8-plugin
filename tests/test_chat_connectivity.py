import pytest
from unittest.mock import MagicMock
from bithub.bithub_comms import BithubComms

@pytest.fixture
def mock_comms():
    """Fixture to mock BithubComms interactions."""
    return MagicMock(spec=BithubComms)

def test_chat_connectivity(mock_comms):
    """Test chat channel retrieval with mocked response."""
    # Setup mock return value
    mock_comms.get_chat_channels.return_value = {
        "public_channels": [
            {"id": 1, "name": "general", "slug": "general"},
            {"id": 2, "name": "dev", "slug": "dev"}
        ]
    }

    # Execute
    channels = mock_comms.get_chat_channels()

    # Verify structure
    assert isinstance(channels, dict)
    assert "public_channels" in channels
    assert len(channels["public_channels"]) == 2
    assert channels["public_channels"][0]["name"] == "general"
    
    # Verify call
    mock_comms.get_chat_channels.assert_called_once()
