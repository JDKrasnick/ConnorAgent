import argparse
import sys
import time

from config import (
    CATEGORIES,
    DB_PATH,
    RATE_LIMIT_DELAY,
    MAX_RETRIES,
    SERPER_API_KEY,
    BRAVE_API_KEY,
    GOOGLE_PLACES_API_KEY,
    YELP_API_KEY,
)
from db.schema import init_db
from db.store import insert_raw_result, insert_domain, get_raw_result_by_query
from queries.expand import generate_queries
from collectors.serper import SerperCollector
from collectors.brave import BraveCollector
from collectors.places import PlacesCollector
from collectors.yelp import YelpCollector
from extractors.domain import extract_domains


def build_collectors(rate_limit_delay: float, max_retries: int) -> dict:
    collectors = {}
    if SERPER_API_KEY:
        collectors["serper"] = SerperCollector(SERPER_API_KEY, rate_limit_delay, max_retries)
    if BRAVE_API_KEY:
        collectors["brave"] = BraveCollector(BRAVE_API_KEY, rate_limit_delay, max_retries)
    if GOOGLE_PLACES_API_KEY:
        collectors["places"] = PlacesCollector(GOOGLE_PLACES_API_KEY, rate_limit_delay, max_retries)
    if YELP_API_KEY:
        collectors["yelp"] = YelpCollector(YELP_API_KEY, rate_limit_delay, max_retries)
    return collectors


def run(categories: list[str], dry_run: bool, limit: int = 0) -> None:
    collectors = build_collectors(RATE_LIMIT_DELAY, MAX_RETRIES)

    if not dry_run and not collectors:
        print("No API keys configured. Add keys to .env and retry.", file=sys.stderr)
        sys.exit(1)

    conn = None if dry_run else init_db(DB_PATH)

    try:
        for category in categories:
            queries = generate_queries(category)
            print(f"[{category}] {len(queries)} queries × {len(collectors) if not dry_run else '?'} sources")

            if dry_run:
                for q in queries[:5]:
                    print(f"  {q}")
                if len(queries) > 5:
                    print(f"  ... ({len(queries) - 5} more)")
                continue

            for source, collector in collectors.items():
                fetched = skipped = errors = domains_inserted = 0
                capped_queries = queries[:limit] if limit else queries

                for query in capped_queries:
                    if get_raw_result_by_query(conn, source, category, query):
                        skipped += 1
                        continue

                    result = collector.collect(query, category)

                    error_msg = None if result.success else result.data[:500]
                    raw_id = insert_raw_result(
                        conn,
                        source=source,
                        category=category,
                        query=query,
                        response_json=result.data,
                        status_code=result.status_code,
                        error_message=error_msg,
                    )

                    if result.success and raw_id:
                        rows = extract_domains(source, result.data)
                        for url, domain, title in rows:
                            insert_domain(conn, raw_id, url, domain, title, source, category)
                        domains_inserted += len(rows)
                    else:
                        errors += 1

                    fetched += 1
                    time.sleep(RATE_LIMIT_DELAY)

                print(
                    f"  [{source}] fetched={fetched} skipped={skipped} "
                    f"errors={errors} domains={domains_inserted}"
                )
    finally:
        if conn:
            conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Domain data collection pipeline")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print queries without making API calls",
    )
    parser.add_argument(
        "--category",
        choices=list(CATEGORIES.keys()),
        help="Run a single category (default: all)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        metavar="N",
        help="Cap queries per source at N (0 = no limit)",
    )
    args = parser.parse_args()

    categories = [args.category] if args.category else list(CATEGORIES.keys())
    run(categories, dry_run=args.dry_run, limit=args.limit)


if __name__ == "__main__":
    main()
