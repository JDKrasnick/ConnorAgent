import time
import httpx
from typing import Any


class CollectResult:
    __slots__ = ("success", "status_code", "data")

    def __init__(self, success: bool, status_code: int, data: str):
        self.success = success
        self.status_code = status_code
        self.data = data


class BaseCollector:
    def __init__(self, api_key: str, rate_limit_delay: float = 1.0, max_retries: int = 3):
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries

    def _request(self, method: str, url: str, **kwargs: Any) -> CollectResult:
        delay = 1.0
        last_status = 0
        last_body = ""

        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=30.0) as client:
                    resp = client.request(method, url, **kwargs)
                last_status = resp.status_code
                last_body = resp.text

                if resp.status_code < 400:
                    return CollectResult(True, resp.status_code, resp.text)

                if resp.status_code in (429, 500, 502, 503, 504):
                    if attempt < self.max_retries - 1:
                        time.sleep(delay)
                        delay *= 2
                        continue

                return CollectResult(False, resp.status_code, resp.text)

            except httpx.RequestError as e:
                last_body = str(e)
                if attempt < self.max_retries - 1:
                    time.sleep(delay)
                    delay *= 2

        return CollectResult(False, last_status, last_body)

    def collect(self, query: str, category: str) -> CollectResult:
        raise NotImplementedError
