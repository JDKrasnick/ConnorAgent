import sqlite3
from typing import Optional


def find_duplicate_ids(
    conn: sqlite3.Connection, category: Optional[str] = None
) -> list[int]:
    """
    For each (domain, category) group in cleaned_domains, identify every row
    that is NOT the canonical representative.

    Canonical selection priority (first wins):
      1. is_relevant=1 over is_relevant=0
      2. More non-null enrichment fields (name, location, entity_type)
      3. Lower id (earliest inserted)

    Returns the list of non-canonical row IDs that should be deleted.
    """
    where = "WHERE category = ?" if category else ""
    params = [category] if category else []

    cur = conn.execute(
        f"""
        SELECT id, domain, category
        FROM cleaned_domains
        {where}
        ORDER BY
            domain,
            category,
            is_relevant DESC,
            (name IS NOT NULL) + (location IS NOT NULL) + (entity_type IS NOT NULL) DESC,
            id ASC
        """,
        params,
    )

    canonical: dict[tuple[str, str], int] = {}
    ids_to_delete: list[int] = []

    for row_id, domain, cat in cur.fetchall():
        key = (domain, cat)
        if key not in canonical:
            canonical[key] = row_id
        else:
            ids_to_delete.append(row_id)

    return ids_to_delete
