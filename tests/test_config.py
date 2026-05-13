import os
import pytest
from config import CATEGORIES, US_MAJOR_CITIES, US_STATES, QUERY_MODIFIERS


def test_categories_structure():
    expected_keys = {"college_art", "college_chinese", "golf_clubs", "hs_art"}
    assert set(CATEGORIES.keys()) == expected_keys

    for cat, data in CATEGORIES.items():
        assert "keywords" in data
        assert isinstance(data["keywords"], list)
        assert len(data["keywords"]) > 0


def test_us_major_cities():
    assert len(US_MAJOR_CITIES) == 50
    assert "New York NY" in US_MAJOR_CITIES
    assert "Los Angeles CA" in US_MAJOR_CITIES


def test_us_states():
    assert len(US_STATES) == 50
    assert "CA" in US_STATES
    assert "NY" in US_STATES


def test_query_modifiers():
    assert QUERY_MODIFIERS == ["website", "contact", "directory", "staff"]