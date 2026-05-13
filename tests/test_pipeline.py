import sqlite3
import pytest
from unittest.mock import Mock, patch
from pipeline import build_collectors, run
from config import CATEGORIES


@pytest.fixture
def mock_conn():
    conn = sqlite3.connect(":memory:")
    # Create tables
    conn.execute("""
    CREATE TABLE raw_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        category TEXT NOT NULL,
        query TEXT NOT NULL,
        response_json TEXT NOT NULL,
        status_code INTEGER,
        error_message TEXT,
        fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(source, category, query)
    );
    """)
    conn.execute("""
    CREATE TABLE domains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_result_id INTEGER NOT NULL REFERENCES raw_results(id),
        url TEXT NOT NULL,
        domain TEXT NOT NULL,
        title TEXT,
        source TEXT NOT NULL,
        category TEXT NOT NULL,
        fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.execute("PRAGMA foreign_keys = ON;")
    yield conn
    conn.close()


def test_build_collectors():
    with patch('pipeline.SERPER_API_KEY', 'key1'), \
         patch('pipeline.BRAVE_API_KEY', 'key2'), \
         patch('pipeline.GOOGLE_PLACES_API_KEY', ''), \
         patch('pipeline.YELP_API_KEY', ''):
        collectors = build_collectors(1.0, 3)
        assert 'serper' in collectors
        assert 'brave' in collectors
        assert 'places' not in collectors
        assert 'yelp' not in collectors


@patch('time.sleep')
@patch('pipeline.init_db')
@patch('pipeline.get_raw_result_by_query')
@patch('pipeline.insert_raw_result')
@patch('pipeline.insert_domain')
@patch('pipeline.extract_domains')
def test_run_integration(mock_extract, mock_insert_domain, mock_insert_raw, mock_get_raw,
                        mock_init_db, mock_sleep, mock_conn):
    # Mock db
    mock_init_db.return_value = mock_conn

    # Mock collector
    mock_collector = Mock()
    mock_result = Mock()
    mock_result.success = True
    mock_result.status_code = 200
    mock_result.data = '{"organic": [{"link": "https://example.com", "title": "Example"}]}'
    mock_collector.collect.return_value = mock_result

    # Mock get_raw_result_by_query to return None (not fetched yet)
    mock_get_raw.return_value = None

    # Mock insert_raw_result to return id
    mock_insert_raw.return_value = 1

    # Mock extract_domains
    mock_extract.return_value = [("https://example.com", "example.com", "Example")]

    with patch('pipeline.build_collectors', return_value={'serper': mock_collector}):
        run(['college_art'], dry_run=False)

    # Verify calls
    assert mock_get_raw.call_count > 0
    assert mock_insert_raw.call_count > 0
    assert mock_extract.call_count > 0
    assert mock_insert_domain.call_count > 0


def test_run_dry_run():
    # Should not fail
    run(['college_art'], dry_run=True)