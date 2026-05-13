"""Extract targeted emails and org metadata from crawled page markdown."""

import json
import os
import re
from typing import Optional

from openai import OpenAI

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
CONTEXT_WINDOW = 350  # chars on each side of an email match

MODEL = "gpt-4o-mini"

# Role targets per category — drives GPT prompting
ROLE_TARGETS: dict[str, str] = {
    "college_art": (
        "art professors, associate/assistant professors of art, studio art instructors, "
        "art department chairs or heads, fine arts faculty"
    ),
    "college_chinese": (
        "Chinese language or Chinese studies professors, lecturers, department chairs or heads"
    ),
    "golf_clubs": (
        "client services representative or director, member services coordinator, "
        "membership director, events coordinator or director"
    ),
    "hs_art": (
        "high school art teachers, art department chairs"
    ),
}

# Domains to skip — generic/shared mailboxes that aren't personal contacts
SKIP_EMAIL_PATTERNS = re.compile(
    r"^(no-?reply|noreply|do-?not-?reply|info|support|help|admin|webmaster|"
    r"postmaster|abuse|privacy|legal|media|press|news|feedback|contact|hello|"
    r"office|general|registrar|admissions|finaid|bursar|hr|jobs|careers)@",
    re.IGNORECASE,
)

CONTACT_SYSTEM = """\
You are an extraction assistant for a B2B sales lead pipeline.
Given webpage text from an organization's website, classify each email found in it.

For EACH email, return:
- email: the email address (lowercase)
- name: person's full name visible near the email, or null
- title: their job title/role visible near the email, or null
- role_type: one short label — "professor", "dept_head", "instructor", "teacher",
  "client_services", "membership", "events", "staff", or "other"
- is_targeted: true ONLY if the email matches the targeted role AND the evidence
  requirements specified for this category are met. When in doubt, mark false.
- confidence: float 0.0–1.0

Return JSON: {"contacts": [...]}
"""

# Per-category evidence requirements injected into the user message.
# GPT must see explicit art/subject evidence before marking is_targeted=true.
CATEGORY_TARGETING_RULES: dict[str, str] = {
    "hs_art": (
        "STRICT EVIDENCE REQUIRED: mark is_targeted=true ONLY when the surrounding context "
        "explicitly links this person to art. Acceptable evidence: their title contains "
        "'art' (e.g. 'Art Teacher', 'Visual Arts Instructor', 'Fine Arts Dept Chair'); "
        "or the nearby text mentions an art class, art room, studio, painting, drawing, "
        "sculpture, ceramics, photography, visual arts, or fine arts in direct association "
        "with this person. A generic 'teacher' or 'staff' label with no art subject context "
        "is NOT sufficient — mark those false. Most staff directory entries will not qualify."
    ),
    "college_art": (
        "Mark is_targeted=true for art/studio art professors, instructors, and department "
        "chairs/heads. Their title or nearby context should reference art, studio art, "
        "graphic design, art history, fine arts, or a specific art medium. "
        "Administrators, advisors, and support staff are not targeted."
    ),
    "college_chinese": (
        "Mark is_targeted=true for professors, lecturers, and department chairs whose "
        "title or nearby context explicitly references Chinese language, Chinese studies, "
        "East Asian languages, or Mandarin. General language dept admin staff are not targeted."
    ),
}

METADATA_SYSTEM = """\
You are a sales intelligence assistant. Given scraped content from an organization's website,
extract information that would help a salesperson sell to this organization.

Return JSON with exactly these keys:
- org_name: official name of the organization
- org_description: 1–2 sentence factual description
- sales_notes: 2–4 concise bullet points (use "• " prefix) of sales-relevant context.
  For colleges/universities: department size, notable programs, any rankings or reputation signals.
  For country/golf clubs: membership exclusivity, amenities, events programs, prestige indicators.
  For high schools: school size, art program strength, budget signals.
- contact_summary: 1-sentence summary of the types of contacts found on the site, or null
"""


def _find_email_contexts(markdown: str) -> list[dict]:
    seen: set[str] = set()
    results = []
    for m in EMAIL_RE.finditer(markdown):
        email = m.group(0).lower()
        if email in seen or SKIP_EMAIL_PATTERNS.match(email):
            continue
        seen.add(email)
        start = max(0, m.start() - CONTEXT_WINDOW)
        end = min(len(markdown), m.end() + CONTEXT_WINDOW)
        results.append({"email": email, "context": markdown[start:end].strip()})
    return results


def extract_contacts_and_metadata(
    domain: str,
    category: str,
    pages: list[dict],
    dry_run: bool = False,
) -> dict:
    """
    Process crawled pages for one domain.
    Returns {"contacts": [...], "metadata": {...}}

    pages: list of {"url": str, "markdown": str|None}
    """
    role_desc = ROLE_TARGETS.get(category, "relevant staff contacts")

    # Collect unique emails + context across all pages, track first-seen URL
    all_contexts: list[dict] = []
    email_to_url: dict[str, str] = {}
    for page in pages:
        md = page.get("markdown") or ""
        for ec in _find_email_contexts(md):
            if ec["email"] not in email_to_url:
                email_to_url[ec["email"]] = page["url"]
                all_contexts.append({**ec, "page_url": page["url"]})

    # Build combined content for metadata extraction (first 5 pages, truncated)
    combined = "\n\n---\n\n".join(
        f"URL: {p['url']}\n\n{(p.get('markdown') or '')[:2000]}"
        for p in pages[:5]
    )[:8000]

    if dry_run:
        print(f"  [dry-run] {domain}: {len(all_contexts)} emails, {len(pages)} pages")
        for ec in all_contexts:
            print(f"    {ec['email']}  ({ec['page_url']})")
        return {"contacts": [], "metadata": {}}

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    contacts: list[dict] = []
    metadata: dict = {}

    # --- Contact classification ---
    if all_contexts:
        items = "\n\n".join(
            f"Email: {ec['email']}\nContext:\n{ec['context']}"
            for ec in all_contexts
        )
        targeting_rule = CATEGORY_TARGETING_RULES.get(category, "")
        user_msg = (
            f"Domain: {domain}\nCategory: {category}\n"
            f"Targeted roles: {role_desc}\n"
            + (f"Targeting rule: {targeting_rule}\n" if targeting_rule else "")
            + f"\n{items}"
        )
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": CONTACT_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0,
            )
            raw = json.loads(resp.choices[0].message.content)
            for c in raw.get("contacts", []):
                email = (c.get("email") or "").lower()
                c["page_url"] = email_to_url.get(email)
            contacts = raw.get("contacts", [])
        except Exception as e:
            print(f"  [warn] contact GPT failed for {domain}: {e}")

    # --- Org metadata ---
    if combined.strip():
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": METADATA_SYSTEM},
                    {
                        "role": "user",
                        "content": (
                            f"Domain: {domain}\nCategory: {category}\n\n"
                            f"Website content:\n{combined}"
                        ),
                    },
                ],
                temperature=0,
            )
            metadata = json.loads(resp.choices[0].message.content)
        except Exception as e:
            print(f"  [warn] metadata GPT failed for {domain}: {e}")

    return {"contacts": contacts, "metadata": metadata}
