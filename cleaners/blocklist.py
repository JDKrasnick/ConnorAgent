import re
from typing import Iterable

# Root domains blocked unconditionally.
# www./m./mobile. prefixes are stripped before matching, so add bare domains only.
BLOCKED_DOMAINS: frozenset[str] = frozenset({
    # Social media
    "facebook.com", "instagram.com", "youtube.com", "tiktok.com",
    "reddit.com", "twitter.com", "x.com", "linkedin.com",
    "pinterest.com", "snapchat.com",
    # Golf tee-time / booking / aggregator platforms
    "golfpass.com", "golfnow.com", "18birdies.com", "chronogolf.com",
    "teeoff.com", "greenskeeper.org", "1golf.eu", "golflink.com",
    "opengolfapi.org", "golftrips.com", "golfpost.de",
    "alwaystimefor9.com", "9holegolfcourses.com", "golf-info-guide.com",
    "golfzongolf.com", "igolfcollective.ca", "albatrossgolf.ca",
    "golfnowchicago.com",
    # Multi-property golf management companies (not a single club's site)
    "invitedclubs.com", "troon.com", "clubcorp.com",
    "arcisgolf.com", "kemper-sports.com",
    # Job boards
    "indeed.com", "ziprecruiter.com", "glassdoor.com", "hcareers.com",
    # Review / rating sites
    "yelp.com", "tripadvisor.com",
    # Maps / navigation
    "mapquest.com",
    # Wedding / event directories
    "weddingwire.com", "wedding-spot.com", "herecomestheguide.com",
    "theknot.com", "eventective.com",
    # Tourism / destination marketing organisations
    "visitmaryland.org", "exploregeorgia.org", "exploresurprise.com",
    "discovergilbert.com", "visitlookoutmountain.com",
    "visitchicagosouthland.com", "sonomacounty.com",
    # Business info / company databases
    "causeiq.com", "bizjournals.com",
    # App stores / e-commerce
    "apps.apple.com", "play.google.com", "ebay.com",
    # Golf news / media
    "golfdigest.com", "golfchannel.com", "alabamagolfnews.com",
    "coloradoavidgolfer.com", "chicagogolfreport.com",
    # Regional golf associations and marketing orgs (not individual clubs)
    "pga.com", "pgaofamerica.com", "usga.org", "msga.org",
    "alabamanwfloridapga.com", "cdgagolf.org", "golfalabama.com",
    "arkansasgolf.com", "texasgolf.com",
    # Weather
    "meteomedia.com", "weather.com",
    # Club travel / aggregated club programs
    "privateclubtravelprogram.com",
    # City / regional destination sites
    "albuquerque.com",
})

# Any domain whose suffix matches one of these strings is blocked.
# Catches aggregator subdomains like alto-lakes-golf-country-club.wheree.com
BLOCKED_SUFFIXES: tuple[str, ...] = (
    ".wheree.com",
    ".kompass.com",
)

_STRIP_PREFIX = re.compile(r"^(?:www\d*|m|mobile)\.")


def _normalize(domain: str) -> str:
    return _STRIP_PREFIX.sub("", domain.lower().strip())


def is_blocked(domain: str) -> bool:
    norm = _normalize(domain)
    if norm in BLOCKED_DOMAINS:
        return True
    for suffix in BLOCKED_SUFFIXES:
        if norm.endswith(suffix):
            return True
    return False


def apply_blocklist(rows: Iterable[dict]) -> tuple[list[dict], list[dict]]:
    """Partition rows into (kept, blocked). Each dict must have a 'domain' key."""
    kept, blocked = [], []
    for row in rows:
        (blocked if is_blocked(row["domain"]) else kept).append(row)
    return kept, blocked
