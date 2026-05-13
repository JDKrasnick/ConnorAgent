import sqlite3
from typing import List, Optional


def insert_raw_result(
    conn: sqlite3.Connection,
    source: str,
    category: str,
    query: str,
    response_json: str,
    status_code: Optional[int] = None,
    error_message: Optional[str] = None,
) -> Optional[int]:
    try:
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO raw_results
                (source, category, query, response_json, status_code, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (source, category, query, response_json, status_code, error_message),
        )
        conn.commit()
        return cur.lastrowid if cur.rowcount else None
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"insert_raw_result failed: {e}") from e


def insert_domain(
    conn: sqlite3.Connection,
    raw_result_id: int,
    url: str,
    domain: str,
    title: Optional[str],
    source: str,
    category: str,
) -> None:
    try:
        conn.execute(
            """
            INSERT INTO domains (raw_result_id, url, domain, title, source, category)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (raw_result_id, url, domain, title, source, category),
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"insert_domain failed: {e}") from e


def insert_cleaned_domain(
    conn: sqlite3.Connection,
    domain_id: int,
    domain: str,
    category: str,
    is_relevant: bool,
    name: Optional[str],
    location: Optional[str],
    entity_type: Optional[str],
    metadata_json: str,
) -> None:
    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO cleaned_domains
                (domain_id, domain, category, is_relevant, name, location, entity_type, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (domain_id, domain, category, int(is_relevant), name, location, entity_type, metadata_json),
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"insert_cleaned_domain failed: {e}") from e


def get_uncleaned_domains(
    conn: sqlite3.Connection, category: Optional[str] = None
) -> List[dict]:
    query = """
        SELECT d.id, d.url, d.domain, d.title, d.category, d.source,
               rr.query
        FROM domains d
        JOIN raw_results rr ON d.raw_result_id = rr.id
        LEFT JOIN cleaned_domains cd ON cd.domain_id = d.id
        WHERE cd.id IS NULL
    """
    params: list = []
    if category is not None:
        query += " AND d.category = ?"
        params.append(category)
    cur = conn.execute(query, params)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_domains_to_crawl(
    conn: sqlite3.Connection,
    category: Optional[str] = None,
    skip_categories: Optional[List[str]] = None,
) -> List[dict]:
    where_clauses = ["cd.is_relevant = 1", "cj.id IS NULL"]
    params: list = []

    if category is not None:
        where_clauses.append("cd.category = ?")
        params.append(category)
    if skip_categories:
        placeholders = ",".join("?" * len(skip_categories))
        where_clauses.append(f"cd.category NOT IN ({placeholders})")
        params.extend(skip_categories)

    where = " AND ".join(where_clauses)
    query = f"""
        SELECT MIN(cd.id) as id, cd.domain, cd.category,
               MAX(cd.name) as name, MAX(cd.location) as location
        FROM cleaned_domains cd
        LEFT JOIN crawl_jobs cj ON cj.cleaned_domain_id = cd.id
        WHERE {where}
        GROUP BY cd.domain, cd.category
    """
    cur = conn.execute(query, params)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def insert_crawl_job(
    conn: sqlite3.Connection,
    cleaned_domain_id: int,
    domain: str,
    category: str,
    job_id: str,
) -> int:
    try:
        cur = conn.execute(
            """
            INSERT INTO crawl_jobs (cleaned_domain_id, domain, category, job_id, status)
            VALUES (?, ?, ?, ?, 'pending')
            """,
            (cleaned_domain_id, domain, category, job_id),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"insert_crawl_job failed: {e}") from e


def update_crawl_job(
    conn: sqlite3.Connection,
    crawl_job_id: int,
    status: str,
    page_count: Optional[int] = None,
    error_message: Optional[str] = None,
) -> None:
    try:
        conn.execute(
            """
            UPDATE crawl_jobs
            SET status = ?, page_count = ?, error_message = ?,
                completed_at = CASE WHEN ? IN ('completed', 'failed') THEN CURRENT_TIMESTAMP END
            WHERE id = ?
            """,
            (status, page_count, error_message, status, crawl_job_id),
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"update_crawl_job failed: {e}") from e


def insert_crawl_pages(
    conn: sqlite3.Connection,
    crawl_job_id: int,
    domain: str,
    pages: List[dict],
) -> None:
    try:
        conn.executemany(
            """
            INSERT INTO crawl_pages (crawl_job_id, domain, url, markdown)
            VALUES (?, ?, ?, ?)
            """,
            [(crawl_job_id, domain, p["url"], p.get("markdown")) for p in pages],
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"insert_crawl_pages failed: {e}") from e


def get_pending_crawl_jobs(conn: sqlite3.Connection) -> List[dict]:
    cur = conn.execute(
        "SELECT id, job_id, domain, category FROM crawl_jobs WHERE status = 'pending'"
    )
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_completed_crawl_jobs(
    conn: sqlite3.Connection,
    category: Optional[str] = None,
    domain: Optional[str] = None,
) -> List[dict]:
    """Return completed crawl jobs that have not yet been extracted."""
    query = """
        SELECT cj.id, cj.domain, cj.category, cj.page_count
        FROM crawl_jobs cj
        LEFT JOIN extracted_metadata em ON em.crawl_job_id = cj.id
        WHERE cj.status = 'completed'
        AND em.id IS NULL
    """
    params: list = []
    if category is not None:
        query += " AND cj.category = ?"
        params.append(category)
    if domain is not None:
        query += " AND cj.domain = ?"
        params.append(domain)
    cur = conn.execute(query, params)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_pages_for_job(conn: sqlite3.Connection, crawl_job_id: int) -> List[dict]:
    cur = conn.execute(
        "SELECT id, url, markdown FROM crawl_pages WHERE crawl_job_id = ?",
        (crawl_job_id,),
    )
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def insert_extracted_contacts(
    conn: sqlite3.Connection,
    crawl_job_id: int,
    domain: str,
    category: str,
    contacts: List[dict],
) -> None:
    try:
        conn.executemany(
            """
            INSERT OR IGNORE INTO extracted_contacts
                (crawl_job_id, domain, category, email, name, title, role_type,
                 is_targeted, confidence, page_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    crawl_job_id,
                    domain,
                    category,
                    c.get("email", "").lower(),
                    c.get("name"),
                    c.get("title"),
                    c.get("role_type"),
                    int(bool(c.get("is_targeted", False))),
                    c.get("confidence"),
                    c.get("page_url"),
                )
                for c in contacts
                if c.get("email")
            ],
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"insert_extracted_contacts failed: {e}") from e


def insert_extracted_metadata(
    conn: sqlite3.Connection,
    crawl_job_id: int,
    domain: str,
    category: str,
    metadata: dict,
) -> None:
    import json

    def _to_str(v) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, list):
            return "\n".join(str(i) for i in v)
        return str(v)

    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO extracted_metadata
                (crawl_job_id, domain, category, org_name, org_description,
                 sales_notes, contact_summary, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                crawl_job_id,
                domain,
                category,
                _to_str(metadata.get("org_name")),
                _to_str(metadata.get("org_description")),
                _to_str(metadata.get("sales_notes")),
                _to_str(metadata.get("contact_summary")),
                json.dumps(metadata),
            ),
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"insert_extracted_metadata failed: {e}") from e


def get_raw_result_by_query(
    conn: sqlite3.Connection, source: str, category: str, query: str
) -> Optional[dict]:
    cur = conn.execute(
        "SELECT id, response_json, status_code, error_message FROM raw_results "
        "WHERE source=? AND category=? AND query=?",
        (source, category, query),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "response_json": row[1],
        "status_code": row[2],
        "error_message": row[3],
    }
