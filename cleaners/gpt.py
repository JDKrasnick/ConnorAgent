import json
import os
from typing import Any

from openai import OpenAI

BATCH_SIZE = 25
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """\
You are a domain classifier for a lead-generation pipeline. You will receive a batch of domains \
found via search queries and must determine whether each one is a legitimate match for its category.

CRITICAL RULE: is_relevant must be true ONLY if the domain itself is the single organization's \
own official website. Two types of domains must always be marked false:
1. Third-party sites (directories, aggregators, review sites, social media, job boards, mapping \
services, wedding directories, news articles, tourism sites, etc.) that merely mention or list \
the organization.
2. Multi-property management companies or networks that operate many clubs/schools/departments \
under one domain (e.g. invitedclubs.com, troon.com, clubcorp.com). These are not a single \
club's own site.

Examples of domains that must be marked false regardless of content:
  yelp.com, golfpass.com, golfnow.com, 18birdies.com, 1golf.eu, chronogolf.com, golflink.com, \
  teeoff.com, greenskeeper.org, mapquest.com, facebook.com, instagram.com, reddit.com, \
  youtube.com, tiktok.com, indeed.com, ziprecruiter.com, glassdoor.com, hcareers.com, \
  weddingwire.com, wedding-spot.com, herecomestheguide.com, pga.com, golfdigest.com, \
  visitmaryland.org, exploregeorgia.org, apps.apple.com, ebay.com, bizjournals.com, \
  causeiq.com, eventective.com, kompass.com

Naming convention hint: domains following the pattern ccof[city/state].com or ccof[city/state].org \
(e.g. ccofcolumbus.com, ccofmd.com, ccofmobile.org) are almost always a single private club's \
own official site — mark them true unless there is clear evidence to the contrary.

Categories and what counts as relevant:
- college_art: Official site of a US college/university art department or school of art/design. \
  Exclude k12, high schools, community programs, and standalone art studios.
- college_chinese: Official site of a US accredited college/university Chinese language or \
  studies department. Exclude community Chinese schools, foreign universities, and military \
  language programs (e.g. DLIFLC).
- golf_clubs: Official site of a single private golf or country club. Exclude disc golf, \
  public courses, and driving ranges.
- hs_art: Official site of a single US high school's art department or art teacher page. \
  The domain must belong to one specific high school, not a school district, network, or \
  multi-school organization. District homepages (e.g. midlothianisd.org, bcps.org, lausd.net) \
  must be marked false even if they mention art programs — they serve dozens of schools and \
  will not yield individual teacher contact info. Accept: a single school's subdomain \
  (e.g. dundalkhs.bcps.org, bhs.rfsd.k12.co.us) or a dedicated hs art teacher site. \
  Exclude colleges, private art studios, and any domain that is a district or multi-school parent site.

Return a JSON object with a "results" array, one entry per input item, in the same order. \
Each entry must have:
  domain (string), is_relevant (boolean), name (string|null), location (string|null), \
  entity_type (string|null), notes (string)

entity_type examples: "university_dept", "high_school", "country_club", "art_school"
"""


def _build_user_message(batch: list[dict]) -> str:
    items = []
    for i, row in enumerate(batch):
        items.append(
            f"{i + 1}. url={row['url']} | domain={row['domain']} | "
            f"title={row.get('title') or 'N/A'} | category={row['category']} | "
            f"query={row.get('query') or 'N/A'}"
        )
    return "\n".join(items)


def _call_api(client: OpenAI, user_message: str) -> dict[str, Any]:
    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)


def clean_batch(domains: list[dict], dry_run: bool = False) -> list[dict]:
    """
    Process a list of domain dicts through GPT-4o mini in batches of BATCH_SIZE.
    Deduplicates by domain before calling the API; all domain_ids sharing the same
    domain inherit the result from the single API call.
    Returns a list of result dicts with keys matching the cleaned_domains schema.
    """
    if not domains:
        return []

    # Dedupe: one representative row per domain, track all ids that share it
    seen: dict[str, dict] = {}
    domain_to_ids: dict[str, list[int]] = {}
    for row in domains:
        d = row["domain"]
        if d not in seen:
            seen[d] = row
            domain_to_ids[d] = []
        domain_to_ids[d].append(row["id"])
    unique_domains = list(seen.values())
    deduped = len(domains) - len(unique_domains)
    if deduped:
        print(f"Deduped {deduped} duplicate domain(s) ({len(unique_domains)} unique).")

    if dry_run:
        for i in range(0, len(unique_domains), BATCH_SIZE):
            batch = unique_domains[i : i + BATCH_SIZE]
            print(f"--- Batch {i // BATCH_SIZE + 1} ({len(batch)} items) ---")
            print(_build_user_message(batch))
            print()
        return []

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    results = []

    for i in range(0, len(unique_domains), BATCH_SIZE):
        batch = unique_domains[i : i + BATCH_SIZE]
        user_message = _build_user_message(batch)

        parsed = None
        for attempt in range(2):
            try:
                parsed = _call_api(client, user_message)
                break
            except Exception as exc:
                if attempt == 1:
                    error_note = f"API error after retry: {exc}"
                    for row in batch:
                        for domain_id in domain_to_ids[row["domain"]]:
                            results.append(
                                {
                                    "domain_id": domain_id,
                                    "domain": row["domain"],
                                    "category": row["category"],
                                    "is_relevant": False,
                                    "name": None,
                                    "location": None,
                                    "entity_type": None,
                                    "metadata_json": json.dumps({"error": error_note}),
                                }
                            )

        if parsed is None:
            continue

        gpt_results = parsed.get("results", [])

        for j, row in enumerate(batch):
            if j < len(gpt_results):
                r = gpt_results[j]
                base = {
                    "domain": row["domain"],
                    "category": row["category"],
                    "is_relevant": bool(r.get("is_relevant", False)),
                    "name": r.get("name"),
                    "location": r.get("location"),
                    "entity_type": r.get("entity_type"),
                    "metadata_json": json.dumps(r),
                }
            else:
                base = {
                    "domain": row["domain"],
                    "category": row["category"],
                    "is_relevant": False,
                    "name": None,
                    "location": None,
                    "entity_type": None,
                    "metadata_json": json.dumps({"error": "missing from GPT response"}),
                }
            for domain_id in domain_to_ids[row["domain"]]:
                results.append({"domain_id": domain_id, **base})

    return results
