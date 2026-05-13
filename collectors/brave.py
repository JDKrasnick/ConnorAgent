from collectors.base import BaseCollector, CollectResult


class BraveCollector(BaseCollector):
    URL = "https://api.search.brave.com/res/v1/web/search"

    def collect(self, query: str, category: str) -> CollectResult:
        return self._request(
            "GET",
            self.URL,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key,
            },
            params={"q": query, "count": 10},
        )
