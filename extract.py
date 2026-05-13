"""Extract targeted contacts and org metadata from completed crawl jobs."""

import argparse

from db.schema import init_db
from db.store import (
    get_completed_crawl_jobs,
    get_pages_for_job,
    insert_extracted_contacts,
    insert_extracted_metadata,
)
from extractors.contacts import extract_contacts_and_metadata


def main():
    parser = argparse.ArgumentParser(description="Extract emails and metadata from crawled pages.")
    parser.add_argument("--category", help="Limit to a specific category")
    parser.add_argument("--domain", help="Limit to a specific domain")
    parser.add_argument("--dry-run", action="store_true", help="Print findings without writing to DB")
    args = parser.parse_args()

    conn = init_db()
    jobs = get_completed_crawl_jobs(conn, category=args.category, domain=args.domain)

    if not jobs:
        print("No completed crawl jobs pending extraction.")
        return

    print(f"Extracting from {len(jobs)} crawl job(s)...\n")

    total_contacts = 0
    total_targeted = 0

    for job in jobs:
        domain = job["domain"]
        category = job["category"]
        crawl_job_id = job["id"]

        pages = get_pages_for_job(conn, crawl_job_id)
        if not pages:
            print(f"  skip {domain} (no pages stored)")
            continue

        print(f"  {domain}  [{category}]  {len(pages)} page(s)")

        result = extract_contacts_and_metadata(
            domain, category, pages, dry_run=args.dry_run
        )

        if args.dry_run:
            continue

        contacts = result.get("contacts", [])
        metadata = result.get("metadata", {})

        targeted = [c for c in contacts if c.get("is_targeted")]
        total_contacts += len(contacts)
        total_targeted += len(targeted)

        print(f"    emails={len(contacts)}  targeted={len(targeted)}", end="")
        if targeted:
            roles = ", ".join(
                f"{c.get('name') or c['email']} ({c.get('title') or c.get('role_type')})"
                for c in targeted[:3]
            )
            print(f"  →  {roles}", end="")
        print()

        if contacts:
            insert_extracted_contacts(conn, crawl_job_id, domain, category, contacts)
        # Always write metadata record so the job isn't re-processed
        insert_extracted_metadata(conn, crawl_job_id, domain, category, metadata)

    if not args.dry_run:
        print(f"\nDone. {total_contacts} emails extracted, {total_targeted} targeted.")


if __name__ == "__main__":
    main()
