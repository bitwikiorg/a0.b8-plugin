"""
Title: test_janitor.py Test
Description: Test suite for janitor cleanup operations.
"""

import pytest
import os
from unittest.mock import MagicMock, patch, call
from bithub.bithub_janitor import BithubJanitor

@pytest.fixture
def janitor():
    with patch.dict(os.environ, {"BITHUB_USER_API_KEY": "test_key", "BITHUB_URL": "http://test.local"}):
        return BithubJanitor()

def test_nuke_category(janitor):
    """Test nuke_category deletes all topics with delay."""
    # Mock _request to return a list of topics
    mock_topics = {
        "topic_list": {
            "topics": [
                {"id": 101},
                {"id": 102},
                {"id": 103}
            ]
        }
    }
    
    with patch.object(janitor, '_request', return_value=mock_topics) as mock_req, \
         patch.object(janitor, 'delete_topic') as mock_delete, \
         patch('time.sleep') as mock_sleep:
        
        janitor.nuke_category(category_id=5, delay=2)
        
        # Verify fetch
        mock_req.assert_called_once_with("GET", "/c/5.json")
        
        # Verify deletions
        assert mock_delete.call_count == 3
        mock_delete.assert_has_calls([
            call(101),
            call(102),
            call(103)
        ])
        
        # Verify throttling
        assert mock_sleep.call_count == 3
        mock_sleep.assert_called_with(2)

def test_nuke_category_empty(janitor):
    """Test nuke_category handles empty categories gracefully."""
    mock_topics = {"topic_list": {"topics": []}}
    
    with patch.object(janitor, '_request', return_value=mock_topics) as mock_req, \
         patch.object(janitor, 'delete_topic') as mock_delete:
        
        janitor.nuke_category(category_id=5)
        
        mock_req.assert_called_once()
        mock_delete.assert_not_called()
