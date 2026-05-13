import sqlite3
from config import DB_PATH

CREATE_RAW_RESULTS = """
CREATE TABLE IF NOT EXISTS raw_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT NOT NULL,
    category        TEXT NOT NULL,
    query           TEXT NOT NULL,
    response_json   TEXT NOT NULL,
    status_code     INTEGER,
    error_message   TEXT,
    fetched_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, category, query)
);
"""

CREATE_DOMAINS = """
CREATE TABLE IF NOT EXISTS domains (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_result_id   INTEGER NOT NULL REFERENCES raw_results(id),
    url             TEXT NOT NULL,
    domain          TEXT NOT NULL,
    title           TEXT,
    source          TEXT NOT NULL,
    category        TEXT NOT NULL,
    fetched_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_IDX_DOMAIN = "CREATE INDEX IF NOT EXISTS idx_domains_domain ON domains(domain);"
CREATE_IDX_CATEGORY = "CREATE INDEX IF NOT EXISTS idx_domains_category ON domains(category);"

CREATE_CLEANED_DOMAINS = """
CREATE TABLE IF NOT EXISTS cleaned_domains (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_id     INTEGER NOT NULL REFERENCES domains(id),
    domain        TEXT NOT NULL,
    category      TEXT NOT NULL,
    is_relevant   INTEGER NOT NULL,
    name          TEXT,
    location      TEXT,
    entity_type   TEXT,
    metadata_json TEXT NOT NULL,
    cleaned_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(domain_id)
);
"""

CREATE_IDX_CLEANED_RELEVANT = (
    "CREATE INDEX IF NOT EXISTS idx_cleaned_relevant ON cleaned_domains(category, is_relevant);"
)

CREATE_CRAWL_JOBS = """
CREATE TABLE IF NOT EXISTS crawl_jobs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    cleaned_domain_id   INTEGER NOT NULL REFERENCES cleaned_domains(id),
    domain              TEXT NOT NULL,
    category            TEXT NOT NULL,
    job_id              TEXT NOT NULL UNIQUE,
    status              TEXT NOT NULL DEFAULT 'pending',
    page_count          INTEGER,
    error_message       TEXT,
    started_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at        DATETIME
);
"""

CREATE_CRAWL_PAGES = """
CREATE TABLE IF NOT EXISTS crawl_pages (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    crawl_job_id        INTEGER NOT NULL REFERENCES crawl_jobs(id),
    domain              TEXT NOT NULL,
    url                 TEXT NOT NULL,
    markdown            TEXT,
    crawled_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_IDX_CRAWL_DOMAIN = (
    "CREATE INDEX IF NOT EXISTS idx_crawl_jobs_domain ON crawl_jobs(domain);"
)

CREATE_EXTRACTED_CONTACTS = """
CREATE TABLE IF NOT EXISTS extracted_contacts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    crawl_job_id    INTEGER NOT NULL REFERENCES crawl_jobs(id),
    domain          TEXT NOT NULL,
    category        TEXT NOT NULL,
    email           TEXT NOT NULL,
    name            TEXT,
    title           TEXT,
    role_type       TEXT,
    is_targeted     INTEGER NOT NULL DEFAULT 0,
    confidence      REAL,
    page_url        TEXT,
    extracted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(crawl_job_id, email)
);
"""

CREATE_EXTRACTED_METADATA = """
CREATE TABLE IF NOT EXISTS extracted_metadata (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    crawl_job_id    INTEGER NOT NULL REFERENCES crawl_jobs(id) UNIQUE,
    domain          TEXT NOT NULL,
    category        TEXT NOT NULL,
    org_name        TEXT,
    org_description TEXT,
    sales_notes     TEXT,
    contact_summary TEXT,
    metadata_json   TEXT NOT NULL,
    extracted_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_IDX_CONTACTS_TARGETED = (
    "CREATE INDEX IF NOT EXISTS idx_contacts_targeted ON extracted_contacts(category, is_targeted);"
)


def init_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute(CREATE_RAW_RESULTS)
    conn.execute(CREATE_DOMAINS)
    conn.execute(CREATE_IDX_DOMAIN)
    conn.execute(CREATE_IDX_CATEGORY)
    conn.execute(CREATE_CLEANED_DOMAINS)
    conn.execute(CREATE_IDX_CLEANED_RELEVANT)
    conn.execute(CREATE_CRAWL_JOBS)
    conn.execute(CREATE_CRAWL_PAGES)
    conn.execute(CREATE_IDX_CRAWL_DOMAIN)
    conn.execute(CREATE_EXTRACTED_CONTACTS)
    conn.execute(CREATE_EXTRACTED_METADATA)
    conn.execute(CREATE_IDX_CONTACTS_TARGETED)
    conn.commit()
    return conn
