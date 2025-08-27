Weather App (Asynchronous)
=========================

This repository contains a small command‑line application that fetches current
weather information from the [Open‑Meteo](https://open‑meteo.com) API.  It
demonstrates API consumption and asynchronous programming in Python using the
`asyncio` and `aiohttp` libraries.  Open‑Meteo provides free weather data
worldwide and does **not** require an API key for non‑commercial use【37812235958545†L12-L33】.

What it does
------------

The script (`weather_app.py`) retrieves the current temperature and wind speed
for one or more cities concurrently.  By default it queries a few example
cities—including Atlanta (33.753746° N, –84.386330° W)【284928131702522†L42-L46】—but you can
specify your own city name and coordinates via command‑line arguments.  The
program constructs a URL like

```
https://api.open-meteo.com/v1/forecast?latitude=33.753746&longitude=-84.386330&current=temperature_2m,wind_speed_10m
```

and parses the JSON response to extract the `temperature_2m` and
`wind_speed_10m` fields.  Because the requests are made asynchronously, multiple
cities can be queried in parallel without blocking.

Usage
-----

Ensure you have Python 3.8+ and the `aiohttp` package installed.  Then run:

```sh
python weather_app.py
```

to fetch weather data for the default cities, or:

```sh
python weather_app.py --city "San Francisco" --lat 37.7749 --lon -122.4194
```

to retrieve data for a custom location.  The script prints the city name,
temperature (°C) and wind speed (m/s).

Notes
-----

* **Internet access** is required for the script to contact the Open‑Meteo API.
* The app uses free endpoints of Open‑Meteo, which are unrestricted for
  non‑commercial use and do not require authentication【37812235958545†L12-L33】.
* Coordinates used for Atlanta were sourced from LatLong.net, which lists
  Atlanta’s latitude as 33.753746 and longitude as –84.386330【284928131702522†L42-L46】.

Feel free to extend the script by adding support for additional weather
variables (e.g., humidity or precipitation), or by integrating a geocoding
service to look up coordinates based on user‑provided city names.