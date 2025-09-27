A small command-line app that fetches current temperature and wind speed for one or more cities at the same time using asyncio and aiohttp. Uses Open-Meteo (no API key for non-commercial use).

Quick start

Requirements: Python 3.8+
Install:

python -m venv .venv
# Windows:
# macOS/Linux: source .venv/bin/activate
pip install aiohttp


Run with defaults:

python weather_app.py


Run for a custom location:

python weather_app.py --city "San Francisco" --lat 37.7749 --lon -122.4194


Example output:

San Francisco — temp: 17.2 °C, wind: 4.6 m/s

Options
--city TEXT      Display name (e.g., "Atlanta")
--lat FLOAT      Latitude (e.g., 33.753746)
--lon FLOAT      Longitude (e.g., -84.386330)
--timeout INT    Request timeout in seconds (default 10)
--max-conns INT  Max concurrent connections (default 10)

How it works

Builds an Open-Meteo URL with latitude and longitude and requests current=temperature_2m,wind_speed_10m. Sends requests concurrently and prints results.

Notes

Internet access is required.

Open-Meteo is free for non-commercial use and does not require authentication.

Atlanta coordinates used in examples: 33.753746, −84.386330.

Extend

Add more variables (humidity, precipitation), add geocoding to convert city names to coordinates, or write results to CSV/JSON.
