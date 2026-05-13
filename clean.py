import argparse
import sys

from cleaners.gpt import clean_batch
from db.schema import init_db
from db.store import get_uncleaned_domains, insert_cleaned_domain


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean raw domains via GPT-4o mini")
    parser.add_argument("--category", help="Only clean domains for this category")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print batches without making API calls",
    )
    args = parser.parse_args()

    conn = init_db()
    domains = get_uncleaned_domains(conn, category=args.category)

    if not domains:
        print("No uncleaned domains found.")
        sys.exit(0)

    print(f"Found {len(domains)} uncleaned domain(s).")

    results = clean_batch(domains, dry_run=args.dry_run)

    if args.dry_run:
        sys.exit(0)

    stored = 0
    for r in results:
        insert_cleaned_domain(
            conn,
            domain_id=r["domain_id"],
            domain=r["domain"],
            category=r["category"],
            is_relevant=r["is_relevant"],
            name=r["name"],
            location=r["location"],
            entity_type=r["entity_type"],
            metadata_json=r["metadata_json"],
        )
        stored += 1

    print(f"Stored {stored} cleaned domain(s).")


if __name__ == "__main__":
    main()
