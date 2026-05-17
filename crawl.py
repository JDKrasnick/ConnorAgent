"""Crawl relevant domains from cleaned_domains using Firecrawl."""

import argparse
import time

from firecrawl import FirecrawlApp
from firecrawl.v2.types import ScrapeOptions

from config import FIRECRAWL_API_KEY
from db.schema import init_db
from db.store import (
    get_domains_to_crawl,
    get_pending_crawl_jobs,
    insert_crawl_job,
    insert_crawl_pages,
    update_crawl_job,
)

CRAWL_LIMIT = 15
CRAWL_MAX_DEPTH = 2
MAX_CONCURRENT_JOBS = 10
POLL_INTERVAL = 10   # seconds between status checks
FIRE_DELAY = 65      # seconds between job submissions — free plan allows 1/min reliably

SKIP_CATEGORIES = ["golf_clubs"]

# Per-category crawl path configuration.
# include_paths: regex patterns — only URLs matching at least one are crawled.
# exclude_paths: regex patterns — URLs matching any are skipped.
CATEGORY_CRAWL_PATHS: dict[str, dict] = {
    "college_art": {
        "include_paths": [
            ".*faculty.*",
            ".*people.*",
            ".*staff.*",
            ".*directory.*",
            ".*contact.*",
            ".*about.*",
            ".*professors.*",
            ".*instructors.*",
            ".*department.*",
        ],
        "exclude_paths": [
            ".*alumni.*",
            ".*giving.*",
            ".*donate.*",
            ".*news.*",
            ".*event.*",
            ".*blog.*",
            ".*admission.*",
            ".*tuition.*",
            ".*login.*",
            ".*jobs.*",
            ".*careers.*",
            ".*shop.*",
            ".*gallery.*",
        ],
    },
    "college_chinese": {
        "include_paths": [
            ".*faculty.*",
            ".*people.*",
            ".*staff.*",
            ".*directory.*",
            ".*contact.*",
            ".*about.*",
            ".*professors.*",
            ".*instructors.*",
            ".*department.*",
            ".*chinese.*",
            ".*language.*",
        ],
        "exclude_paths": [
            ".*alumni.*",
            ".*giving.*",
            ".*donate.*",
            ".*news.*",
            ".*event.*",
            ".*blog.*",
            ".*admission.*",
            ".*login.*",
            ".*jobs.*",
            ".*careers.*",
            ".*shop.*",
        ],
    },
    "hs_art": {
        # Target the art department page and teacher/staff listings on a single school site.
        # Broad school-wide paths (calendar, athletics, etc.) are noise.
        "include_paths": [
            ".*art.*",
            ".*faculty.*",
            ".*staff.*",
            ".*teachers.*",
            ".*contact.*",
            ".*about.*",
            ".*fine-arts.*",
            ".*visual-arts.*",
        ],
        "exclude_paths": [
            ".*athletics.*",
            ".*sports.*",
            ".*calendar.*",
            ".*event.*",
            ".*lunch.*",
            ".*menu.*",
            ".*enroll.*",
            ".*register.*",
            ".*board.*",
            ".*finance.*",
            ".*budget.*",
            ".*transportation.*",
            ".*library.*",
            ".*counseling.*",
            ".*news.*",
            ".*blog.*",
            ".*announce.*",
            ".*login.*",
            ".*parent.*",
            ".*alumni.*",
        ],
    },
}

# Fallback used if category not in CATEGORY_CRAWL_PATHS
_DEFAULT_CRAWL_PATHS = {
    "include_paths": [".*contact.*", ".*about.*", ".*staff.*", ".*faculty.*", ".*directory.*"],
    "exclude_paths": [".*news.*", ".*event.*", ".*blog.*", ".*login.*", ".*shop.*"],
}

SCRAPE_OPTIONS = ScrapeOptions(
    formats=["markdown"],
    only_main_content=True,
    exclude_tags=["nav", "footer", "header"],
    wait_for=1000,
    timeout=20000,
)


def _pages_from_status(status) -> list[dict]:
    """Convert v2 CrawlJob data into [{url, markdown}] dicts."""
    pages = []
    for doc in status.data or []:
        url = (doc.metadata.url if doc.metadata else None) or ""
        pages.append({"url": url, "markdown": doc.markdown})
    return pages


def fire_jobs(app: FirecrawlApp, domains: list[dict], conn, dry_run: bool) -> list[dict]:
    """Submit crawl jobs and return list of {crawl_job_id, job_id, domain}."""
    in_flight = []
    for d in domains:
        url = f"https://{d['domain']}"
        paths = CATEGORY_CRAWL_PATHS.get(d["category"], _DEFAULT_CRAWL_PATHS)
        if dry_run:
            print(f"  [dry-run] would crawl {url}  [{d['category']}]")
            continue
        try:
            result = app.start_crawl(
                url,
                include_paths=paths["include_paths"],
                exclude_paths=paths["exclude_paths"],
                max_discovery_depth=CRAWL_MAX_DEPTH,
                limit=CRAWL_LIMIT,
                ignore_sitemap=False,
                allow_external_links=False,
                scrape_options=SCRAPE_OPTIONS,
            )
            job_id = result.id
            if not job_id:
                print(f"  [warn] no job_id for {url}: {result}")
                continue
            crawl_job_id = insert_crawl_job(conn, d["id"], d["domain"], d["category"], job_id)
            in_flight.append({"crawl_job_id": crawl_job_id, "job_id": job_id, "domain": d["domain"]})
            print(f"  fired {url} → {job_id}")
            time.sleep(FIRE_DELAY)
        except Exception as e:
            print(f"  [error] failed to start crawl for {url}: {e}")
    return in_flight


def poll_until_done(app: FirecrawlApp, in_flight: list[dict], conn) -> None:
    """Poll pending jobs until all complete or fail."""
    pending = {j["job_id"]: j for j in in_flight}
    while pending:
        time.sleep(POLL_INTERVAL)
        for job_id in list(pending.keys()):
            try:
                status = app.get_crawl_status(job_id)
            except Exception as e:
                print(f"  [error] status check failed for {job_id}: {e}")
                continue

            crawl_state = status.status
            job = pending[job_id]

            if crawl_state == "completed":
                pages = _pages_from_status(status)
                insert_crawl_pages(conn, job["crawl_job_id"], job["domain"], pages)
                update_crawl_job(conn, job["crawl_job_id"], "completed", page_count=len(pages))
                print(f"  done  {job['domain']} ({len(pages)} pages)")
                del pending[job_id]

            elif crawl_state == "failed":
                update_crawl_job(conn, job["crawl_job_id"], "failed", error_message=crawl_state)
                print(f"  failed {job['domain']}")
                del pending[job_id]

            else:
                print(f"  ...{job['domain']} {crawl_state} ({status.completed}/{status.total})")

        print(f"  {len(pending)} job(s) still pending")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", help="Limit to a specific category")
    parser.add_argument("--limit", type=int, help="Max number of domains to crawl this run")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Resume pending jobs from DB without firing new ones")
    args = parser.parse_args()

    conn = init_db()
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    if args.resume:
        pending = get_pending_crawl_jobs(conn)
        if not pending:
            print("No pending jobs to resume.")
            return
        print(f"Resuming {len(pending)} pending jobs...")
        poll_until_done(app, pending, conn)
        return

    domains = get_domains_to_crawl(conn, category=args.category, skip_categories=SKIP_CATEGORIES)
    if not domains:
        print("No uncrawled domains found.")
        return

    if args.limit:
        domains = domains[: args.limit]

    print(f"Crawling {len(domains)} domain(s)")

    for batch_start in range(0, len(domains), MAX_CONCURRENT_JOBS):
        batch = domains[batch_start: batch_start + MAX_CONCURRENT_JOBS]
        print(f"\nBatch {batch_start // MAX_CONCURRENT_JOBS + 1}: firing {len(batch)} jobs")
        in_flight = fire_jobs(app, batch, conn, dry_run=args.dry_run)
        if in_flight:
            poll_until_done(app, in_flight, conn)

    print("\nCrawl complete.")


if __name__ == "__main__":
    main()
