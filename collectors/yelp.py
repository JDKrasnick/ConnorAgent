from collectors.base import BaseCollector, CollectResult


class YelpCollector(BaseCollector):
    URL = "https://api.yelp.com/v3/businesses/search"

    def collect(self, query: str, category: str) -> CollectResult:
        return self._request(
            "GET",
            self.URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            params={"term": query, "location": "United States", "limit": 20},
        )
