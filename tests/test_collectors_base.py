import pytest
from unittest.mock import Mock, patch
from collectors.base import BaseCollector, CollectResult


class TestCollector(BaseCollector):
    def collect(self, query: str, category: str) -> CollectResult:
        return self._request("GET", "http://example.com")


def test_collect_result():
    result = CollectResult(True, 200, "data")
    assert result.success is True
    assert result.status_code == 200
    assert result.data == "data"


def test_base_collector_init():
    collector = TestCollector("key", 2.0, 5)
    assert collector.api_key == "key"
    assert collector.rate_limit_delay == 2.0
    assert collector.max_retries == 5


@patch('httpx.Client')
def test_request_success(mock_client):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = "success"
    mock_client.return_value.__enter__.return_value.request.return_value = mock_resp

    collector = TestCollector("key")
    result = collector._request("GET", "http://example.com")

    assert result.success is True
    assert result.status_code == 200
    assert result.data == "success"


@patch('httpx.Client')
def test_request_failure_no_retry(mock_client):
    mock_resp = Mock()
    mock_resp.status_code = 404
    mock_resp.text = "not found"
    mock_client.return_value.__enter__.return_value.request.return_value = mock_resp

    collector = TestCollector("key")
    result = collector._request("GET", "http://example.com")

    assert result.success is False
    assert result.status_code == 404
    assert result.data == "not found"


@patch('httpx.Client')
@patch('time.sleep')
def test_request_retry_on_429(mock_sleep, mock_client):
    # First call returns 429, second returns 200
    mock_resp_429 = Mock()
    mock_resp_429.status_code = 429
    mock_resp_429.text = "rate limited"

    mock_resp_200 = Mock()
    mock_resp_200.status_code = 200
    mock_resp_200.text = "success"

    mock_client.return_value.__enter__.return_value.request.side_effect = [mock_resp_429, mock_resp_200]

    collector = TestCollector("key", max_retries=2)
    result = collector._request("GET", "http://example.com")

    assert result.success is True
    assert result.status_code == 200
    assert result.data == "success"
    assert mock_sleep.call_count == 1  # One retry delay