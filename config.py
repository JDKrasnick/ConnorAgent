import os
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
YELP_API_KEY = os.getenv("YELP_API_KEY", "")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

DB_PATH = "data.db"

CATEGORIES = {
    "college_art": {
        "keywords": ["art department", "college of art", "school of art"]
    },
    "college_chinese": {
        "keywords": ["chinese department", "department of chinese studies"]
    },
    "golf_clubs": {
        "keywords": ["golf country club", "private golf club"]
    },
    "hs_art": {
        "keywords": ["high school art teacher", "high school art department"]
    },
}

US_MAJOR_CITIES = [
    "New York NY", "Los Angeles CA", "Chicago IL", "Houston TX", "Phoenix AZ",
    "Philadelphia PA", "San Antonio TX", "San Diego CA", "Dallas TX", "San Jose CA",
    "Austin TX", "Jacksonville FL", "Fort Worth TX", "Columbus OH", "Charlotte NC",
    "San Francisco CA", "Indianapolis IN", "Seattle WA", "Denver CO", "Nashville TN",
    "Oklahoma City OK", "El Paso TX", "Washington DC", "Boston MA", "Las Vegas NV",
    "Memphis TN", "Louisville KY", "Portland OR", "Baltimore MD", "Milwaukee WI",
    "Albuquerque NM", "Tucson AZ", "Fresno CA", "Sacramento CA", "Atlanta GA",
    "Kansas City MO", "Omaha NE", "Colorado Springs CO", "Raleigh NC", "Miami FL",
    "Long Beach CA", "Virginia Beach VA", "Minneapolis MN", "Tampa FL", "New Orleans LA",
    "Arlington TX", "Bakersfield CA", "Honolulu HI", "Anaheim CA", "Aurora CO",
]

US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

QUERY_MODIFIERS = ["website", "contact", "directory", "staff"]

RATE_LIMIT_DELAY = 1.0  # seconds between requests per collector
MAX_RETRIES = 3
