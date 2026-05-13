import argparse
import sys

from config import DB_PATH
from db.schema import init_db
from cleaners.blocklist import is_blocked
from cleaners.deduper import find_duplicate_ids


def _count(conn, category, relevant_only=False):
    conds = []
    params = []
    if category:
        conds.append("category = ?")
        params.append(category)
    if relevant_only:
        conds.append("is_relevant = 1")
    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    return conn.execute(
        f"SELECT COUNT(*), COUNT(DISTINCT domain) FROM cleaned_domains {where}", params
    ).fetchone()


def _run_blocklist(conn, category, dry_run):
    conds = ["is_relevant = 1"]
    params = []
    if category:
        conds.append("category = ?")
        params.append(category)
    where = "WHERE " + " AND ".join(conds)

    rows = conn.execute(
        f"SELECT id, domain FROM cleaned_domains {where}", params
    ).fetchall()

    hits = [(row_id, domain) for row_id, domain in rows if is_blocked(domain)]
    if hits and not dry_run:
        ids = [r[0] for r in hits]
        conn.execute(
            f"UPDATE cleaned_domains SET is_relevant = 0 WHERE id IN ({','.join('?'*len(ids))})",
            ids,
        )
        conn.commit()
    return hits


def _run_deduper(conn, category, dry_run):
    ids = find_duplicate_ids(conn, category)
    if ids and not dry_run:
        conn.execute(
            f"DELETE FROM cleaned_domains WHERE id IN ({','.join('?'*len(ids))})", ids
        )
        conn.commit()
    return ids


def main():
    parser = argparse.ArgumentParser(
        description="Apply blocklist and deduplication to cleaned_domains"
    )
    parser.add_argument("--category", help="Restrict to a single category")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without modifying the database",
    )
    args = parser.parse_args()

    conn = init_db(DB_PATH)

    rows_before, unique_before = _count(conn, args.category)
    rel_before, unique_rel_before = _count(conn, args.category, relevant_only=True)
    print(
        f"Before : {rows_before} rows total | "
        f"{rel_before} relevant ({unique_rel_before} unique domains)"
    )

    blocked = _run_blocklist(conn, args.category, args.dry_run)
    verb = "would mark" if args.dry_run else "marked"
    if blocked:
        for _, domain in blocked:
            print(f"  [blocklist] {domain}")
        print(f"Blocklist: {verb} {len(blocked)} row(s) not relevant")
    else:
        print("Blocklist: nothing to flag")

    deleted = _run_deduper(conn, args.category, args.dry_run)
    verb = "would delete" if args.dry_run else "deleted"
    if deleted:
        print(f"Deduper : {verb} {len(deleted)} duplicate row(s)")
    else:
        print("Deduper : no duplicates")

    rows_after, unique_after = _count(conn, args.category)
    rel_after, unique_rel_after = _count(conn, args.category, relevant_only=True)
    if args.dry_run:
        projected_rel = rel_before - len(blocked)
        projected_rows = rows_before - len(deleted)
        print(
            f"After   : ~{projected_rows} rows total | "
            f"~{projected_rel} relevant (dry run — no changes written)"
        )
    else:
        print(
            f"After   : {rows_after} rows total | "
            f"{rel_after} relevant ({unique_rel_after} unique domains)"
        )

    conn.close()


if __name__ == "__main__":
    main()
