import json
from typing import List, Tuple
from urllib.parse import urlparse

DomainRow = Tuple[str, str, str]  # (url, domain, title)


def _netloc(url: str) -> str:
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def _parse_serper(data: dict) -> List[DomainRow]:
    results = []
    for item in data.get("organic", []):
        url = item.get("link", "")
        title = item.get("title", "")
        if url:
            results.append((url, _netloc(url), title))
    return results


def _parse_brave(data: dict) -> List[DomainRow]:
    results = []
    for item in data.get("web", {}).get("results", []):
        url = item.get("url", "")
        title = item.get("title", "")
        if url:
            results.append((url, _netloc(url), title))
    return results


def _parse_places(data: dict) -> List[DomainRow]:
    results = []
    for item in data.get("results", []):
        url = item.get("website", "")
        title = item.get("name", "")
        if url:
            results.append((url, _netloc(url), title))
    return results


def _parse_yelp(data: dict) -> List[DomainRow]:
    results = []
    for item in data.get("businesses", []):
        url = item.get("url", "")
        title = item.get("name", "")
        if url:
            results.append((url, _netloc(url), title))
    return results


_PARSERS = {
    "serper": _parse_serper,
    "brave": _parse_brave,
    "places": _parse_places,
    "yelp": _parse_yelp,
}


def extract_domains(source: str, response_json: str) -> List[DomainRow]:
    parser = _PARSERS.get(source)
    if parser is None:
        raise ValueError(f"Unknown source: {source}")
    try:
        data = json.loads(response_json)
    except json.JSONDecodeError:
        return []
    return [(url, domain, title) for url, domain, title in parser(data) if domain]
