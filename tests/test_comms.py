"""
Title: test_comms.py Test
Description: Test suite for comms.
"""

import os
from unittest.mock import patch, MagicMock, call
import pytest
from bithub.bithub_comms import BithubComms
from bithub.bithub_errors import BithubAuthError, BithubNetworkError, BithubRateLimitError, BithubError

def test_rate_limit_handling(comms, mock_requests, mock_sleep):
    """Test handling of 429 Rate Limit responses (success after retry)."""
    # Mock API: 1st call 429 (Retry-After: 2), 2nd call 200 OK
    resp_429 = MagicMock()
    resp_429.ok = False # CRITICAL: Must be False to trigger error handling
    resp_429.status_code = 429
    resp_429.headers = {"Retry-After": "2"}
    
    resp_200 = MagicMock()
    resp_200.ok = True
    resp_200.status_code = 200
    resp_200.json.return_value = {"ok": True}
    
    mock_requests.side_effect = [resp_429, resp_200]
    
    result = comms._request("GET", "/test")
    
    # Verification Steps
    assert mock_requests.call_count == 2
    mock_sleep.assert_called_with(2)
    assert result == {"ok": True}

def test_server_error_retry(comms, mock_requests, mock_sleep):
    """Test retry logic for 500-level server errors."""
    # Mock API: 500 -> 502 -> 200 OK
    resp_500 = MagicMock()
    resp_500.ok = False
    resp_500.status_code = 500
    
    resp_502 = MagicMock()
    resp_502.ok = False
    resp_502.status_code = 502
    
    resp_200 = MagicMock()
    resp_200.ok = True
    resp_200.status_code = 200
    resp_200.json.return_value = {"data": "success"}
    
    mock_requests.side_effect = [resp_500, resp_502, resp_200]
    
    result = comms._request("GET", "/test")
    
    # Verification Steps
    assert mock_requests.call_count == 3
    # Verify backoff: sleep(1) then sleep(2)
    mock_sleep.assert_has_calls([call(1), call(2)])
    assert result == {"data": "success"}

def test_max_retries_exceeded(comms, mock_requests, mock_sleep):
    """Test behavior when max retries are exceeded (Network Error)."""
    # Mock API: Always 503
    resp_503 = MagicMock()
    resp_503.ok = False
    resp_503.status_code = 503
    
    mock_requests.side_effect = [resp_503] * 4
    
    # Expect BithubNetworkError instead of dict return
    with pytest.raises(BithubNetworkError, match="Max retries exceeded"):
        comms._request("GET", "/test", retries=4)
    
    assert mock_requests.call_count == 4

def test_missing_api_key(monkeypatch):
    """Test initialization fails without API key."""
    monkeypatch.delenv("BITHUB_USER_API_KEY", raising=False)
    
    # Expect BithubAuthError instead of ValueError
    with pytest.raises(BithubAuthError, match="BITHUB_USER_API_KEY is required"):
        BithubComms()

def test_auth_failure(comms, mock_requests):
    """Test that 401/403 errors raise BithubAuthError immediately."""
    resp_401 = MagicMock()
    resp_401.ok = False
    resp_401.status_code = 401
    resp_401.text = "Unauthorized"
    
    mock_requests.return_value = resp_401
    
    with pytest.raises(BithubAuthError, match="HTTP 401"):
        comms._request("GET", "/test")
    
    # Should not retry auth errors
    assert mock_requests.call_count == 1

def test_rate_limit_exhausted(comms, mock_requests, mock_sleep):
    """Test that 429 errors raise BithubRateLimitError if retries exhausted."""
    resp_429 = MagicMock()
    resp_429.ok = False
    resp_429.status_code = 429
    resp_429.headers = {"Retry-After": "1"}
    
    mock_requests.return_value = resp_429
    
    with pytest.raises(BithubRateLimitError, match="Rate limit exceeded"):
        comms._request("GET", "/test", retries=2)
    
    assert mock_requests.call_count == 2

def test_audience_enforcement_success(comms):
    """Test that valid JSON content passes audience enforcement for 'ai'."""
    # 1. Pure JSON
    valid_json = '{"key": "value"}'
    assert comms._enforce_audience_format(valid_json, 'ai') == valid_json

    # 2. Markdown JSON
    markdown_json = '```json\n{"key": "value"}\n```'
    expected = '{"key": "value"}'
    assert comms._enforce_audience_format(markdown_json, 'ai') == expected

    # 3. Human audience (pass-through)
    raw_text = "Just some text"
    assert comms._enforce_audience_format(raw_text, 'human') == raw_text

def test_audience_enforcement_failure(comms):
    """Test that invalid content raises BithubError for 'ai' audience."""
    invalid_json = "Not JSON"
    with pytest.raises(BithubError, match="Content validation failed"):
        comms._enforce_audience_format(invalid_json, 'ai')

def test_create_topic_sync(comms, mock_requests):
    """Test create_topic with sync=True waits for reply."""
    # Mock create response
    mock_requests.return_value.ok = True
    mock_requests.return_value.json.return_value = {"topic_id": 1, "id": 10}
    
    # Mock wait_for_reply
    with patch.object(comms, 'wait_for_reply') as mock_wait:
        mock_wait.return_value = {"id": 11, "raw": "Reply"}
        
        result = comms.create_topic("Title", "Content", sync=True)
        
        assert result == {"id": 11, "raw": "Reply"}
        mock_wait.assert_called_once()

def test_create_topic_async(comms, mock_requests):
    """Test create_topic with sync=False returns immediately."""
    # Mock create response
    mock_requests.return_value.ok = True
    mock_requests.return_value.json.return_value = {"topic_id": 1, "id": 10}
    
    with patch.object(comms, 'wait_for_reply') as mock_wait:
        result = comms.create_topic("Title", "Content", sync=False)
        
        assert result == {"topic_id": 1, "id": 10}
        mock_wait.assert_not_called()

# --- NEW DELETION TESTS ---

def test_delete_post(comms, mock_requests):
    """Test delete_post calls correct endpoint."""
    mock_requests.return_value.ok = True
    mock_requests.return_value.json.return_value = {"success": "OK"}
    
    comms.delete_post(123)
    
    mock_requests.assert_called_with(
        "DELETE", 
        "http://test.local/posts/123.json", 
        headers=comms.headers, 
        params=None, 
        json=None
    )

def test_delete_topic(comms, mock_requests):
    """Test delete_topic calls correct endpoint."""
    mock_requests.return_value.ok = True
    
    comms.delete_topic(456)
    
    mock_requests.assert_called_with(
        "DELETE", 
        "http://test.local/t/456.json", 
        headers=comms.headers, 
        params=None, 
        json=None
    )

def test_delete_user(comms, mock_requests):
    """Test delete_user calls correct endpoint with payload."""
    mock_requests.return_value.ok = True
    
    comms.delete_user(789, delete_posts=True)
    
    expected_payload = {
        "delete_posts": True,
        "block_email": False,
        "block_urls": False,
        "block_ip": False
    }
    
    mock_requests.assert_called_with(
        "DELETE", 
        "http://test.local/admin/users/789.json", 
        headers=comms.headers, 
        params=None, 
        json=expected_payload
    )

@pytest.fixture
def comms(mock_requests, mock_sleep):
    # Fixed: Use BITHUB_URL instead of BITHUB_API_URL to match implementation
    with patch.dict(os.environ, {"BITHUB_USER_API_KEY": os.getenv("BITHUB_USER_API_KEY", "test_key"), "BITHUB_URL": "http://test.local"}):
        return BithubComms()

@pytest.fixture
def mock_requests():
    with patch("requests.request") as mock:
        yield mock

@pytest.fixture
def mock_sleep():
    with patch("time.sleep") as mock:
        yield mock
