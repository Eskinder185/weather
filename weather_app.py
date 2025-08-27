"""
Simple asynchronous weather app
================================

This module defines a small command‐line application that fetches the current
temperature and wind speed for a handful of cities.  It uses the public
`Open‑Meteo` API, which does not require an API key for non‑commercial use.  By
default the script queries the weather for a few example cities, but you can
specify your own coordinates via command‑line arguments.  The program is
written using Python's `asyncio` and `aiohttp` libraries to perform
HTTP requests concurrently, showcasing asynchronous programming techniques.

The underlying API returns weather forecast data in JSON format.  We call
`https://api.open-meteo.com/v1/forecast` with the ``latitude`` and
``longitude`` query parameters and request current temperature and wind speed
via the ``current`` query parameter.  According to Open‑Meteo, the service
offers free access without an API key and provides accurate weather
forecasts for any location around the world【37812235958545†L12-L33】【37812235958545†L121-L132】.

Example usage::

    python weather_app.py

    # or specifying custom coordinates for San Francisco
    python weather_app.py --city "San Francisco" --lat 37.7749 --lon -122.4194

The script will display the current temperature and wind speed for the
requested locations.  It can easily be extended to fetch additional weather
variables such as humidity or precipitation.
"""

import argparse
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional

import aiohttp


@dataclass
class City:
    """Data class representing a city and its geographic coordinates."""

    name: str
    latitude: float
    longitude: float


async def fetch_weather(session: aiohttp.ClientSession, city: City) -> Optional[Dict[str, float]]:
    """Fetch current temperature and wind speed for a given city.

    Args:
        session: The ``aiohttp`` client session used to make HTTP requests.
        city: A ``City`` instance with a name and coordinates.

    Returns:
        A dictionary containing the city's name, temperature and wind speed
        in metric units, or ``None`` if the request fails.
    """
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={city.latitude}&longitude={city.longitude}&"
        "current=temperature_2m,wind_speed_10m"
    )
    try:
        async with session.get(url) as response:
            data = await response.json()
            current = data.get("current", {})
            temperature = current.get("temperature_2m")
            wind_speed = current.get("wind_speed_10m")
            if temperature is None or wind_speed is None:
                return None
            return {
                "city": city.name,
                "temperature": temperature,
                "wind_speed": wind_speed,
            }
    except Exception:
        return None


async def gather_weather(cities: List[City]) -> List[Optional[Dict[str, float]]]:
    """Concurrently fetch weather data for multiple cities."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_weather(session, city) for city in cities]
        return await asyncio.gather(*tasks)


def parse_args() -> argparse.Namespace:
    """Parse command‑line arguments.  Users may specify a single city via
    ``--city``, ``--lat`` and ``--lon`` or rely on default example cities.
    """
    parser = argparse.ArgumentParser(description="Asynchronous weather app using Open‑Meteo API")
    parser.add_argument(
        "--city",
        help="Name of the city for custom query (used in the output only)",
    )
    parser.add_argument(
        "--lat",
        type=float,
        help="Latitude of the city for custom query",
    )
    parser.add_argument(
        "--lon",
        type=float,
        help="Longitude of the city for custom query",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the script."""
    args = parse_args()
    # Default cities include the user's home city Atlanta (33.753746, -84.386330)【284928131702522†L9-L12】
    # and a few international examples.  These values can be updated or
    # extended as desired.
    default_cities: List[City] = [
        City("Atlanta", 33.753746, -84.386330),
        City("London", 51.5072, -0.1276),
        City("Tokyo", 35.6762, 139.6503),
    ]
    cities_to_query: List[City]
    # If the user specifies custom coordinates, override the default list
    if args.lat is not None and args.lon is not None and args.city:
        cities_to_query = [City(args.city, args.lat, args.lon)]
    else:
        cities_to_query = default_cities

    # Run the asynchronous tasks
    results = asyncio.run(gather_weather(cities_to_query))

    # Display the results
    for result in results:
        if result is None:
            print("Failed to fetch weather data.")
            continue
        print(
            f"{result['city']}: Temperature {result['temperature']}°C, "
            f"Wind Speed {result['wind_speed']} m/s"
        )


if __name__ == "__main__":
    main()