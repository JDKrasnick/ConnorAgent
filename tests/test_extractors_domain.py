import json
import pytest
from extractors.domain import extract_domains


def test_extract_domains_serper():
    data = {
        "organic": [
            {"link": "https://example.com", "title": "Example"},
            {"link": "https://test.org", "title": "Test"},
        ]
    }
    result = extract_domains("serper", json.dumps(data))
    assert len(result) == 2
    assert result[0] == ("https://example.com", "example.com", "Example")
    assert result[1] == ("https://test.org", "test.org", "Test")


def test_extract_domains_brave():
    data = {
        "web": {
            "results": [
                {"url": "https://brave.com", "title": "Brave"},
                {"url": "https://search.com", "title": "Search"},
            ]
        }
    }
    result = extract_domains("brave", json.dumps(data))
    assert len(result) == 2
    assert result[0] == ("https://brave.com", "brave.com", "Brave")


def test_extract_domains_places():
    data = {
        "results": [
            {"website": "https://place.com", "name": "Place"},
            {"website": "https://another.com", "name": "Another"},
        ]
    }
    result = extract_domains("places", json.dumps(data))
    assert len(result) == 2
    assert result[0] == ("https://place.com", "place.com", "Place")


def test_extract_domains_yelp():
    data = {
        "businesses": [
            {"url": "https://yelp.com/biz/example", "name": "Example Biz"},
            {"url": "https://yelp.com/biz/test", "name": "Test Biz"},
        ]
    }
    result = extract_domains("yelp", json.dumps(data))
    assert len(result) == 2
    assert result[0] == ("https://yelp.com/biz/example", "yelp.com", "Example Biz")


def test_extract_domains_unknown_source():
    with pytest.raises(ValueError, match="Unknown source"):
        extract_domains("unknown", "{}")


def test_extract_domains_invalid_json():
    result = extract_domains("serper", "invalid json")
    assert result == []


def test_extract_domains_empty_data():
    result = extract_domains("serper", "{}")
    assert result == []


def test_extract_domains_missing_fields():
    data = {"organic": [{"title": "No link"}]}
    result = extract_domains("serper", json.dumps(data))
    assert result == []  # No url, so filtered out


def test_extract_domains_invalid_url():
    data = {"organic": [{"link": "not-a-url", "title": "Invalid"}]}
    result = extract_domains("serper", json.dumps(data))
    assert len(result) == 0  # Invalid url gives empty domain, filtered out