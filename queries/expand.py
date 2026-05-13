from typing import List
from config import CATEGORIES, US_MAJOR_CITIES, US_STATES, QUERY_MODIFIERS


def generate_queries(category: str) -> List[str]:
    if category not in CATEGORIES:
        raise ValueError(f"Unknown category: {category}")

    keywords = CATEGORIES[category]["keywords"]
    queries: set[str] = set()

    for keyword in keywords:
        # keyword × city
        for city in US_MAJOR_CITIES:
            queries.add(f'"{keyword}" {city}')

        # keyword × state
        for state in US_STATES:
            queries.add(f'"{keyword}" {state}')

        # keyword × modifier
        for modifier in QUERY_MODIFIERS:
            queries.add(f'"{keyword}" {modifier}')

    return sorted(queries)
