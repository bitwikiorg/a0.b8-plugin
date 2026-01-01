"""
WHY: To verify the reliability and security of the BithubComms transport layer.
WHAT: Unit tests for rate limiting, authentication, synaptic retry logic, and content validation.
HOW: Uses pytest with strict request mocking; follows Guard -> Do -> Verify in every test case.
"""

import os
import pytest
import time
from unittest.mock import patch, MagicMock, call
from bithub.bithub_comms import BithubComms
from bithub.bithub_errors import BithubAuthError, BithubRateLimitError, BithubNetworkError, BithubError

@pytest.fixture
def comms():
    with patch.dict(os.environ, {"BITHUB_USER_API_KEY": "test_key", "BITHUB_URL": "http://test.local"}):
        return BithubComms()

@pytest.fixture
def mock_requests():
    with patch("requests.request") as mock:
        yield mock

@pytest.fixture
def mock_sleep():
    with patch("time.sleep") as mock:
        yield mock

def test_synaptic_rate_limiting(comms, mock_requests):
    """Guard: Ensure rate limiter is active. Do: Execute requests. Verify: Timing and call count."""
    mock_requests.return_value.ok = True
    mock_requests.return_value.json.return_value = {"ok": True}
    start = time.time()
    comms._request("GET", "/test")
    comms._request("GET", "/test")
    duration = time.time() - start
    assert duration >= 0.5
    assert mock_requests.call_count == 2

def test_rate_limit_handling(comms, mock_requests, mock_sleep):
    """Do: Handle 429. Verify: Retry logic and success."""
    resp_429 = MagicMock(ok=False, status_code=429, headers={"Retry-After": "2"})
    resp_200 = MagicMock(ok=True, status_code=200)
    resp_200.json.return_value = {"ok": True}
    mock_requests.side_effect = [resp_429, resp_200]
    result = comms._request("GET", "/test")
    assert mock_requests.call_count == 2
    mock_sleep.assert_called_with(2)
    assert result == {"ok": True}

def test_server_error_retry(comms, mock_requests, mock_sleep):
    """Do: Handle 500/502. Verify: Backoff and success."""
    mock_requests.side_effect = [
        MagicMock(ok=False, status_code=500),
        MagicMock(ok=False, status_code=502),
        MagicMock(ok=True, status_code=200, json=lambda: {"data": "success"})
    ]
    result = comms._request("GET", "/test")
    assert mock_requests.call_count == 3
    mock_sleep.assert_has_calls([call(1), call(2)])
    assert result == {"data": "success"}

def test_max_retries_exceeded(comms, mock_requests, mock_sleep):
    """Guard: Max retries. Verify: BithubNetworkError."""
    mock_requests.side_effect = [MagicMock(ok=False, status_code=503)] * 4
    with pytest.raises(BithubNetworkError, match="Max retries exceeded"):
        comms._request("GET", "/test", retries=4)

def test_missing_api_key(monkeypatch):
    """Guard: Initialization without key. Verify: BithubAuthError."""
    monkeypatch.delenv("BITHUB_USER_API_KEY", raising=False)
    with pytest.raises(BithubAuthError, match="BITHUB_USER_API_KEY is required"):
        BithubComms()

def test_auth_failure(comms, mock_requests):
    """Guard: 401/403. Verify: Immediate BithubAuthError."""
    mock_requests.return_value = MagicMock(ok=False, status_code=401, text="Unauthorized")
    with pytest.raises(BithubAuthError, match="HTTP 401"):
        comms._request("GET", "/test")
    assert mock_requests.call_count == 1

def test_rate_limit_exhausted(comms, mock_requests, mock_sleep):
    """Guard: 429 retries exhausted. Verify: BithubRateLimitError."""
    mock_requests.return_value = MagicMock(ok=False, status_code=429, headers={"Retry-After": "1"})
    with pytest.raises(BithubRateLimitError, match="Rate limit exceeded"):
        comms._request("GET", "/test", retries=2)

def test_audience_enforcement_success(comms):
    """Do: Valid JSON for AI. Verify: Pass-through."""
    valid_json = '{"key": "value"}'
    assert comms._enforce_audience_format(valid_json, 'ai') == valid_json

def test_audience_enforcement_failure(comms):
    """Guard: Invalid JSON for AI. Verify: BithubError."""
    with pytest.raises(BithubError, match="AI audience requires valid JSON"):
        comms._enforce_audience_format("Not JSON", 'ai')

def test_create_topic_sync(comms, mock_requests):
    """Do: Sync topic creation. Verify: wait_for_reply called."""
    mock_requests.return_value = MagicMock(ok=True, json=lambda: {"topic_id": 1, "id": 10})
    with patch.object(comms, 'wait_for_reply') as mock_wait:
        mock_wait.return_value = {"id": 11}
        result = comms.create_topic("Title", "Content", sync=True)
        assert result == {"id": 11}

def test_delete_post(comms, mock_requests):
    """Do: Delete post. Verify: Correct endpoint."""
    mock_requests.return_value.ok = True
    comms.delete_post(123)
    mock_requests.assert_called_with("DELETE", "http://test.local/posts/123.json", headers=comms.headers, params=None, json=None)

def test_delete_topic(comms, mock_requests):
    """Do: Delete topic. Verify: Correct endpoint."""
    mock_requests.return_value.ok = True
    comms.delete_topic(456)
    mock_requests.assert_called_with("DELETE", "http://test.local/t/456.json", headers=comms.headers, params=None, json=None)

def test_delete_user(comms, mock_requests):
    """Do: Delete user. Verify: Payload integrity."""
    mock_requests.return_value.ok = True
    comms.delete_user(789, delete_posts=True)
    expected_payload = {"delete_posts": True, "block_email": False, "block_urls": False, "block_ip": False}
    mock_requests.assert_called_with("DELETE", "http://test.local/admin/users/789.json", headers=comms.headers, params=None, json=expected_payload)
