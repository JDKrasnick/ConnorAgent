import json
from collectors.base import BaseCollector, CollectResult


class SerperCollector(BaseCollector):
    URL = "https://google.serper.dev/search"

    def collect(self, query: str, category: str) -> CollectResult:
        return self._request(
            "POST",
            self.URL,
            headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
            content=json.dumps({"q": query, "num": 10}),
        )
