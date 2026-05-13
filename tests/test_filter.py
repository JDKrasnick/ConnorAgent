import sqlite3
import json
import pytest

from cleaners.blocklist import is_blocked, apply_blocklist
from cleaners.deduper import find_duplicate_ids


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def conn():
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys = ON;")
    db.executescript("""
        CREATE TABLE raw_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL, category TEXT NOT NULL, query TEXT NOT NULL,
            response_json TEXT NOT NULL, status_code INTEGER, error_message TEXT,
            fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source, category, query)
        );
        CREATE TABLE domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_result_id INTEGER NOT NULL REFERENCES raw_results(id),
            url TEXT NOT NULL, domain TEXT NOT NULL, title TEXT,
            source TEXT NOT NULL, category TEXT NOT NULL,
            fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE cleaned_domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_id INTEGER NOT NULL REFERENCES domains(id),
            domain TEXT NOT NULL, category TEXT NOT NULL,
            is_relevant INTEGER NOT NULL,
            name TEXT, location TEXT, entity_type TEXT,
            metadata_json TEXT NOT NULL,
            cleaned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(domain_id)
        );
    """)
    db.commit()
    yield db
    db.close()


def _seed(db, rows):
    """
    rows: list of (domain, category, is_relevant, name)
    Inserts synthetic raw_results, domains, and cleaned_domains entries.
    """
    db.execute(
        "INSERT INTO raw_results (source,category,query,response_json) VALUES ('test','golf_clubs','q','{}') ON CONFLICT DO NOTHING"
    )
    raw_id = db.execute("SELECT id FROM raw_results LIMIT 1").fetchone()[0]
    ids = []
    for domain, cat, relevant, name in rows:
        db.execute(
            "INSERT INTO domains (raw_result_id,url,domain,source,category) VALUES (?,?,?,?,?)",
            (raw_id, f"https://{domain}", domain, "test", cat),
        )
        domain_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.execute(
            "INSERT INTO cleaned_domains (domain_id,domain,category,is_relevant,name,metadata_json) VALUES (?,?,?,?,?,?)",
            (domain_id, domain, cat, int(relevant), name, json.dumps({})),
        )
        ids.append(db.execute("SELECT last_insert_rowid()").fetchone()[0])
    db.commit()
    return ids


# ---------------------------------------------------------------------------
# Blocklist unit tests
# ---------------------------------------------------------------------------

class TestIsBlocked:
    def test_social_media_blocked(self):
        for domain in ["facebook.com", "www.instagram.com", "reddit.com", "www.youtube.com", "tiktok.com"]:
            assert is_blocked(domain), domain

    def test_aggregators_blocked(self):
        for domain in ["www.golfpass.com", "golfnow.com", "www.yelp.com", "m.yelp.com",
                       "www.18birdies.com", "www.chronogolf.com", "www.teeoff.com",
                       "www.greenskeeper.org", "www.1golf.eu"]:
            assert is_blocked(domain), domain

    def test_multi_property_blocked(self):
        for domain in ["troon.com", "www.invitedclubs.com", "clubcorp.com"]:
            assert is_blocked(domain), domain

    def test_job_boards_blocked(self):
        for domain in ["www.indeed.com", "www.glassdoor.com", "www.ziprecruiter.com", "www.hcareers.com"]:
            assert is_blocked(domain), domain

    def test_suffix_pattern_blocked(self):
        assert is_blocked("alto-lakes-golf-country-club.wheree.com")
        assert is_blocked("some-club.wheree.com")
        assert is_blocked("lv.kompass.com")

    def test_www_prefix_stripped(self):
        # Ensure www-prefixed and bare versions are both blocked
        assert is_blocked("www.facebook.com")
        assert is_blocked("facebook.com")
        assert is_blocked("m.yelp.com")
        assert is_blocked("yelp.com")

    def test_true_positive_clubs_not_blocked(self):
        """Real individual club domains must never be flagged."""
        clubs = [
            "www.diamondheadgc.com",
            "albatrossgolf.ca",  # Wait — this IS in the blocklist
        ]
        # albatrossgolf.ca is blocked (golf aggregator from Canada)
        # Only test genuinely good clubs
        good_clubs = [
            "www.diamondheadgc.com",
            "www.yorbalindaclub.com",
            "www.monroegcc.com",
            "www.ccwoodmoor.com",
            "www.countrycluboftherockies.com",
            "grassycreek.com",
            "theclubac.com",
            "ccofcolumbus.com",
            "palmdesertgolf.com",
            "glenn.golf",
            "www.saratogacc.com",
            "www.springcreekcc.com",
            "www.ccnb.golf",
            "www.moodysdiscgolfcountryclub.com",
        ]
        for domain in good_clubs:
            assert not is_blocked(domain), f"False positive: {domain} wrongly blocked"

    def test_apply_blocklist_partitions_correctly(self):
        rows = [
            {"domain": "www.diamondheadgc.com"},
            {"domain": "www.facebook.com"},
            {"domain": "troon.com"},
            {"domain": "grassycreek.com"},
            {"domain": "golfpass.com"},
        ]
        kept, blocked = apply_blocklist(rows)
        assert {r["domain"] for r in kept} == {"www.diamondheadgc.com", "grassycreek.com"}
        assert {r["domain"] for r in blocked} == {"www.facebook.com", "troon.com", "golfpass.com"}


# ---------------------------------------------------------------------------
# Deduper unit tests
# ---------------------------------------------------------------------------

class TestFindDuplicateIds:
    def test_no_duplicates(self, conn):
        _seed(conn, [
            ("clubA.com", "golf_clubs", True, "Club A"),
            ("clubB.com", "golf_clubs", True, "Club B"),
        ])
        assert find_duplicate_ids(conn) == []

    def test_removes_lower_priority_duplicate(self, conn):
        """When a domain appears twice, the is_relevant=0 row is the duplicate."""
        _seed(conn, [
            ("clubA.com", "golf_clubs", False, None),
            ("clubA.com", "golf_clubs", True, "Club A"),
        ])
        ids = find_duplicate_ids(conn)
        assert len(ids) == 1
        # The kept row should be the is_relevant=1 one
        kept = conn.execute(
            "SELECT is_relevant FROM cleaned_domains WHERE id NOT IN (?)", (ids[0],)
        ).fetchone()
        assert kept[0] == 1

    def test_all_irrelevant_keeps_one(self, conn):
        _seed(conn, [
            ("bad.com", "golf_clubs", False, None),
            ("bad.com", "golf_clubs", False, None),
            ("bad.com", "golf_clubs", False, None),
        ])
        ids = find_duplicate_ids(conn)
        assert len(ids) == 2

    def test_prefers_enriched_row(self, conn):
        """Among two is_relevant=1 rows, keeps the one with more filled fields."""
        _seed(conn, [
            ("club.com", "golf_clubs", True, None),      # no name
            ("club.com", "golf_clubs", True, "Club X"),  # has name — should be kept
        ])
        ids = find_duplicate_ids(conn)
        assert len(ids) == 1
        kept = conn.execute(
            "SELECT name FROM cleaned_domains WHERE id NOT IN (?)", (ids[0],)
        ).fetchone()
        assert kept[0] == "Club X"

    def test_category_filter(self, conn):
        _seed(conn, [
            ("dup.com", "golf_clubs", True, "Club"),
            ("dup.com", "golf_clubs", True, "Club"),
            ("dup.com", "college_art", True, "Art Dept"),
            ("dup.com", "college_art", True, "Art Dept"),
        ])
        ids_golf = find_duplicate_ids(conn, category="golf_clubs")
        assert len(ids_golf) == 1
        ids_art = find_duplicate_ids(conn, category="college_art")
        assert len(ids_art) == 1
        ids_all = find_duplicate_ids(conn)
        assert len(ids_all) == 2

    def test_different_categories_not_merged(self, conn):
        """Same domain in two categories → two canonical rows, no deletions."""
        _seed(conn, [
            ("shared.com", "golf_clubs", True, "Golf"),
            ("shared.com", "college_art", True, "Art"),
        ])
        assert find_duplicate_ids(conn) == []


# ---------------------------------------------------------------------------
# End-to-end filter tests (no DB writes — validate logic only)
# ---------------------------------------------------------------------------

class TestFilterEndToEnd:
    def test_blocklist_catches_gpt_false_positive(self, conn):
        """Simulate GPT incorrectly marking troon.com as relevant=1."""
        _seed(conn, [
            ("troon.com", "golf_clubs", True, "Troon Golf"),        # GPT mistake
            ("www.diamondheadgc.com", "golf_clubs", True, "DHGCC"), # correct true positive
        ])
        # Apply blocklist
        rows = conn.execute(
            "SELECT id, domain FROM cleaned_domains WHERE is_relevant=1"
        ).fetchall()
        from cleaners.blocklist import is_blocked
        hits = [r for r in rows if is_blocked(r[1])]
        assert len(hits) == 1
        assert hits[0][1] == "troon.com"

    def test_no_true_positives_removed(self, conn):
        """None of the 14 known good clubs should be flagged by the blocklist."""
        good_clubs = [
            "www.diamondheadgc.com", "www.yorbalindaclub.com", "www.monroegcc.com",
            "www.ccwoodmoor.com", "www.countrycluboftherockies.com", "grassycreek.com",
            "theclubac.com", "ccofcolumbus.com", "palmdesertgolf.com", "glenn.golf",
            "www.saratogacc.com", "www.springcreekcc.com", "www.ccnb.golf",
            "www.moodysdiscgolfcountryclub.com",
        ]
        _seed(conn, [(d, "golf_clubs", True, "Club") for d in good_clubs])
        rows = conn.execute(
            "SELECT id, domain FROM cleaned_domains WHERE is_relevant=1"
        ).fetchall()
        blocked = [r[1] for r in rows if is_blocked(r[1])]
        assert blocked == [], f"True positives wrongly blocked: {blocked}"

    def test_deduper_reduces_rows_preserves_relevant(self, conn):
        """After dedup, each domain appears once and relevant status is preserved."""
        _seed(conn, [
            # Two rows for diamondheadgc — both relevant
            ("www.diamondheadgc.com", "golf_clubs", True, "DHGCC"),
            ("www.diamondheadgc.com", "golf_clubs", True, "DHGCC"),
            # Three rows for facebook — all irrelevant
            ("www.facebook.com", "golf_clubs", False, None),
            ("www.facebook.com", "golf_clubs", False, None),
            ("www.facebook.com", "golf_clubs", False, None),
            # One unique good club
            ("grassycreek.com", "golf_clubs", True, "Grassy Creek"),
        ])
        ids = find_duplicate_ids(conn)
        assert len(ids) == 3  # 1 dup for diamondhead + 2 dups for facebook

        conn.execute(
            f"DELETE FROM cleaned_domains WHERE id IN ({','.join('?'*len(ids))})", ids
        )
        conn.commit()

        remaining = conn.execute(
            "SELECT domain, is_relevant FROM cleaned_domains ORDER BY domain"
        ).fetchall()
        assert len(remaining) == 3
        domain_map = {d: r for d, r in remaining}
        assert domain_map["www.diamondheadgc.com"] == 1
        assert domain_map["www.facebook.com"] == 0
        assert domain_map["grassycreek.com"] == 1
