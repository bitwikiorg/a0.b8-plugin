"""
WHY: To ensure the BithubJanitor correctly executes 'apoptosis' (cleanup) tasks.
WHAT: Tests for sequential topic deletion and rate-limited cleanup.
HOW: Mocks BithubComms requests; follows Guard -> Do -> Verify to assert deletion sequence.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from bithub.bithub_janitor import BithubJanitor

@pytest.fixture
def janitor():
    with patch.dict('os.environ', {"BITHUB_USER_API_KEY": "test_key"}):
        return BithubJanitor()

def test_nuke_category_execution(janitor):
    """Do: Execute nuke on category. Verify: Sequential deletions and throttling."""
    mock_topics = {"topic_list": {"topics": [{"id": 1}, {"id": 2}]}}
    with patch.object(janitor, '_request', return_value=mock_topics) as mock_req, \
         patch.object(janitor, 'delete_topic') as mock_delete, \
         patch('time.sleep') as mock_sleep:
        janitor.nuke_category(category_id=5, delay=1)
        assert mock_delete.call_count == 2
        mock_delete.assert_has_calls([call(1), call(2)])
        assert mock_sleep.call_count == 2

def test_nuke_category_empty(janitor):
    """Do: Nuke empty category. Verify: No deletions."""
    with patch.object(janitor, '_request', return_value={"topic_list": {"topics": []}}), \
         patch.object(janitor, 'delete_topic') as mock_delete:
        janitor.nuke_category(category_id=5)
        mock_delete.assert_not_called()
