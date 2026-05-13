from collectors.base import BaseCollector, CollectResult


class PlacesCollector(BaseCollector):
    URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    def collect(self, query: str, category: str) -> CollectResult:
        return self._request(
            "GET",
            self.URL,
            params={"query": query, "key": self.api_key},
        )
