# ConnorAgent

A multi-source domain discovery and enrichment pipeline. It collects domains from search APIs, cleans them with GPT, filters out noise, and crawls the survivors with Firecrawl.

## Pipeline overview

```
pipeline.py  →  clean.py  →  filter.py  →  crawl.py
(collect)       (GPT tag)    (blocklist/  (Firecrawl)
                              dedup)
```

## Repo structure

```
ConnorAgent/
├── pipeline.py          # Step 1: collect raw domains from search APIs
├── clean.py             # Step 2: classify domains with GPT-4o mini
├── filter.py            # Step 3: apply blocklist + deduplication
├── crawl.py             # Step 4: crawl relevant domains via Firecrawl
├── config.py            # API keys, DB path, category definitions
│
├── collectors/          # Search API clients
│   ├── base.py          # Abstract base collector
│   ├── serper.py        # Google Search via Serper
│   ├── brave.py         # Brave Search
│   ├── places.py        # Google Places
│   └── yelp.py          # Yelp Fusion
│
├── cleaners/            # Domain classification
│   ├── gpt.py           # GPT-4o mini batch classifier
│   ├── blocklist.py     # Known-bad domain filter
│   └── deduper.py       # Cross-category deduplication
│
├── extractors/
│   └── domain.py        # URL → domain extraction
│
├── queries/
│   └── expand.py        # Generate search queries from category keywords
│
├── db/
│   ├── schema.py        # SQLite table definitions + init_db()
│   └── store.py         # Read/write helpers
│
└── tests/               # pytest test suite
```

## Database schema

| Table             | Description                                      |
|-------------------|--------------------------------------------------|
| `raw_results`     | Raw API responses, one row per (source, category, query) |
| `domains`         | URLs extracted from raw results                  |
| `cleaned_domains` | GPT classification output (relevant, name, location, entity_type) |
| `crawl_jobs`      | Firecrawl job tracking (pending → completed)     |
| `crawl_pages`     | Crawled page content (URL + markdown)            |

## Setup

```bash
pip3 install -r requirements.txt
cp .env.example .env   # fill in API keys
```

Required keys in `.env`:

| Key | Source |
|-----|--------|
| `SERPER_API_KEY` | serper.dev |
| `BRAVE_API_KEY` | brave.com/search/api |
| `GOOGLE_PLACES_API_KEY` | Google Cloud Console |
| `YELP_API_KEY` | Yelp Fusion |
| `OPENAI_API_KEY` | OpenAI |
| `FIRECRAWL_API_KEY` | firecrawl.dev |

## Usage

```bash
# Collect domains from all categories
python3 pipeline.py

# Dry-run (print queries, no API calls)
python3 pipeline.py --dry-run

# Single category, capped at 5 queries per source
python3 pipeline.py --category college_art --limit 5

# Classify collected domains with GPT
python3 clean.py

# Apply blocklist + dedup
python3 filter.py

# Crawl relevant domains
python3 crawl.py

# Resume interrupted crawl jobs
python3 crawl.py --resume
```

## Tests

```bash
python3 -m pytest tests/
```
