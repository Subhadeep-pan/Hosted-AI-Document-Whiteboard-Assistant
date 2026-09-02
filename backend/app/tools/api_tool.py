"""
General external API tool (Section 13 of the upgrade plan).

Kept intentionally small: one working example (weather, via Open-Meteo,
which needs no API key) rather than a pile of stub integrations that
would just make the project look bigger without doing anything real.
Add more APIs here the same way if you need finance/etc. later.
"""

import re
import requests

CITY_PATTERN = re.compile(r"in ([A-Za-z\s]+)")


def get_weather(query):
    match = CITY_PATTERN.search(query)
    city = match.group(1).strip() if match else None

    if not city:
        return "Please specify a city, e.g. 'weather in Kolkata'."

    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=5,
        ).json()

        results = geo.get("results")
        if not results:
            return f"Couldn't find a location called '{city}'."

        lat, lon = results[0]["latitude"], results[0]["longitude"]

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "current_weather": True},
            timeout=5,
        ).json()

        current = weather.get("current_weather", {})

        return (
            f"Current weather in {city}: {current.get('temperature')}°C, "
            f"wind {current.get('windspeed')} km/h."
        )

    except Exception:
        return "Weather lookup failed."


def call_api_tool(query):
    """Entry point live_data_service routes into. Only weather is wired
    up for now; extend this dispatch as more APIs are added."""

    if "weather" in query.lower():
        return get_weather(query)

    return "No matching external API tool for this query."
