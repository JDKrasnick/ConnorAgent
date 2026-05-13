import sqlite3
import pytest
from db.store import insert_raw_result, insert_domain, get_raw_result_by_query


@pytest.fixture
def conn():
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


def test_insert_raw_result_success(conn):
    raw_id = insert_raw_result(conn, "serper", "test_cat", "test query", '{"data": "test"}', 200)
    assert raw_id is not None

    # Check inserted
    cur = conn.execute("SELECT * FROM raw_results WHERE id=?", (raw_id,))
    row = cur.fetchone()
    assert row[1] == "serper"
    assert row[2] == "test_cat"
    assert row[3] == "test query"
    assert row[4] == '{"data": "test"}'
    assert row[5] == 200
    assert row[6] is None


def test_insert_raw_result_duplicate(conn):
    # Insert first
    raw_id1 = insert_raw_result(conn, "serper", "test_cat", "test query", '{"data": "test"}', 200)
    # Insert duplicate
    raw_id2 = insert_raw_result(conn, "serper", "test_cat", "test query", '{"data": "test2"}', 200)
    assert raw_id2 is None  # Should not insert

    # Check only one row
    cur = conn.execute("SELECT COUNT(*) FROM raw_results")
    assert cur.fetchone()[0] == 1


def test_insert_domain(conn):
    # Insert raw first
    raw_id = insert_raw_result(conn, "serper", "test_cat", "test query", '{"data": "test"}', 200)
    assert raw_id is not None
    # Insert domain
    insert_domain(conn, raw_id, "https://example.com", "example.com", "Example", "serper", "test_cat")

    # Check inserted
    cur = conn.execute("SELECT * FROM domains WHERE raw_result_id=?", (raw_id,))
    row = cur.fetchone()
    assert row[1] == raw_id
    assert row[2] == "https://example.com"
    assert row[3] == "example.com"
    assert row[4] == "Example"
    assert row[5] == "serper"
    assert row[6] == "test_cat"


def test_get_raw_result_by_query_found(conn):
    insert_raw_result(conn, "serper", "test_cat", "test query", '{"data": "test"}', 200, "error")

    result = get_raw_result_by_query(conn, "serper", "test_cat", "test query")
    assert result is not None
    assert result["response_json"] == '{"data": "test"}'
    assert result["status_code"] == 200
    assert result["error_message"] == "error"


def test_get_raw_result_by_query_not_found(conn):
    result = get_raw_result_by_query(conn, "serper", "test_cat", "nonexistent")
    assert result is None