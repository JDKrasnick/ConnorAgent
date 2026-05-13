import pytest
from queries.expand import generate_queries
from config import CATEGORIES


def test_generate_queries_valid_category():
    queries = generate_queries("college_art")
    assert isinstance(queries, list)
    assert len(queries) > 0
    assert all(isinstance(q, str) for q in queries)
    # Check deduplication
    assert len(queries) == len(set(queries))


def test_generate_queries_invalid_category():
    with pytest.raises(ValueError, match="Unknown category"):
        generate_queries("invalid")


def test_generate_queries_content():
    queries = generate_queries("college_art")
    # Should have keyword × cities, keyword × states, keyword × modifiers
    keywords = CATEGORIES["college_art"]["keywords"]
    expected_count = len(keywords) * (50 + 50 + 4)  # cities + states + modifiers
    assert len(queries) == expected_count

    # Check some examples
    assert '"art department" New York NY' in queries
    assert '"art department" CA' in queries
    assert '"art department" website' in queries


def test_generate_queries_sorted():
    queries = generate_queries("college_art")
    assert queries == sorted(queries)