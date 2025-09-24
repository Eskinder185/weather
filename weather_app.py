"""Simple weather app with CLI output and a tiny web interface.

The application fetches current weather data from the Open-Meteo API for one
or more cities.  When run in CLI mode it prints the latest weather figures in
plain text.  With the ``--serve`` flag it starts a small HTTP server that
exposes a home page, an about page, and a FAQ page.
"""

import argparse
import html
import json
from dataclasses import dataclass
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Iterable, List, Optional
from urllib import error, parse, request


@dataclass
class City:
    """Represents a city and the coordinates to query."""

    name: str
    latitude: float
    longitude: float


def fetch_weather(city: City) -> Optional[Dict[str, float]]:
    """Fetch current temperature and wind speed for a single city."""
    params = parse.urlencode(
        {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "current": "temperature_2m,wind_speed_10m",
        }
    )
    url = f"https://api.open-meteo.com/v1/forecast?{params}"
    try:
        with request.urlopen(url, timeout=10) as response:
            payload = response.read()
    except (error.URLError, TimeoutError):
        return None

    try:
        data = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError:
        return None

    current = data.get("current", {})
    temperature = current.get("temperature_2m")
    wind_speed = current.get("wind_speed_10m")
    if temperature is None or wind_speed is None:
        return None

    return {
        "city": city.name,
        "temperature": float(temperature),
        "wind_speed": float(wind_speed),
    }


def get_weather_for_cities(cities: Iterable[City]) -> List[Optional[Dict[str, float]]]:
    """Retrieve weather information for a collection of cities."""
    return [fetch_weather(city) for city in cities]


def format_cli_output(results: List[Optional[Dict[str, float]]]) -> List[str]:
    lines: List[str] = []
    for result in results:
        if result is None:
            lines.append("Failed to fetch weather data.")
            continue
        lines.append(
            f"{result['city']}: Temperature {result['temperature']:.1f} C, "
            f"Wind Speed {result['wind_speed']:.1f} m/s"
        )
    return lines


def render_html_page(title: str, body: str) -> bytes:
    """Wrap provided body content in a simple HTML template."""
    html_doc = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; max-width: 800px; }}
    nav a {{ margin-right: 1rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; }}
    th {{ background: #f0f0f0; }}
    footer {{ margin-top: 2rem; font-size: 0.9rem; color: #555; }}
  </style>
</head>
<body>
  <nav>
    <a href=\"/\">Home</a>
    <a href=\"/about\">About</a>
    <a href=\"/faq\">FAQ</a>
  </nav>
  {body}
  <footer>Weather data courtesy of <a href=\"https://open-meteo.com/\">Open-Meteo</a>.</footer>
</body>
</html>"""
    return html_doc.encode("utf-8")


class WeatherRequestHandler(BaseHTTPRequestHandler):
    """Serve the home, about, and FAQ pages."""

    def __init__(self, *args, cities: Iterable[City], **kwargs):
        self._cities = list(cities)
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:  # noqa: N802 (match BaseHTTPRequestHandler signature)
        if self.path == "/" or self.path.startswith("/?"):
            self._handle_home()
        elif self.path == "/about":
            self._handle_about()
        elif self.path == "/faq":
            self._handle_faq()
        else:
            self._handle_not_found()

    def _write_response(self, content: bytes, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _handle_home(self) -> None:
        results = get_weather_for_cities(self._cities)
        rows = []
        for result in results:
            if result is None:
                rows.append("<tr><td colspan=\"3\">Failed to fetch weather data.</td></tr>")
            else:
                rows.append(
                    "<tr><td>{city}</td><td>{temp:.1f} C</td><td>{wind:.1f} m/s</td></tr>".format(
                        city=html.escape(result["city"]),
                        temp=result["temperature"],
                        wind=result["wind_speed"],
                    )
                )
        body = """
  <h1>Current Weather</h1>
  <p>The latest readings for the configured cities.</p>
  <table>
    <thead>
      <tr><th>City</th><th>Temperature</th><th>Wind Speed</th></tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
""".format(rows="\n      ".join(rows))
        self._write_response(render_html_page("Weather Home", body))

    def _handle_about(self) -> None:
        body = """
  <h1>About</h1>
  <p>This demo pulls current weather conditions from the Open-Meteo service and
     presents them through a tiny built-in web server.</p>
  <p>Use the command line options to customise which cities are shown.</p>
"""
        self._write_response(render_html_page("About", body))

    def _handle_faq(self) -> None:
        body = """
  <h1>Frequently Asked Questions</h1>
  <h2>Which API do you use?</h2>
  <p>All weather data comes from the free Open-Meteo API.</p>
  <h2>How often is the data updated?</h2>
  <p>The latest values are fetched each time you refresh the page.</p>
  <h2>Can I add more cities?</h2>
  <p>Yes.  Run the script with the command line options shown below to specify a
     different location.</p>
"""
        self._write_response(render_html_page("FAQ", body))

    def _handle_not_found(self) -> None:
        body = """
  <h1>404 - Not Found</h1>
  <p>The page you requested does not exist.  Try one of the links above.</p>
"""
        self._write_response(render_html_page("Not Found", body), status=404)

    def log_message(self, format: str, *args) -> None:  # noqa: A003 (inherit signature)
        """Silence default logging to keep console output tidy."""
        return


def run_server(cities: Iterable[City], host: str = "127.0.0.1", port: int = 8000) -> None:
    handler = partial(WeatherRequestHandler, cities=list(cities))
    with HTTPServer((host, port), handler) as httpd:
        print(f"Serving weather pages on http://{host}:{port}/ (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Weather app using the Open-Meteo API")
    parser.add_argument("--city", help="Name of the city for custom query")
    parser.add_argument("--lat", type=float, help="Latitude for the custom city")
    parser.add_argument("--lon", type=float, help="Longitude for the custom city")
    parser.add_argument("--serve", action="store_true", help="Start the web server instead of the CLI output")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface for the web server")
    parser.add_argument("--port", type=int, default=8000, help="Port for the web server")
    return parser.parse_args()


def build_cities(args: argparse.Namespace) -> List[City]:
    if args.lat is not None and args.lon is not None:
        name = args.city if args.city else "Custom Location"
        return [City(name, args.lat, args.lon)]
    return [
        City("Atlanta", 33.753746, -84.38633),
        City("London", 51.5072, -0.1276),
        City("Tokyo", 35.6762, 139.6503),
    ]


def main() -> None:
    args = parse_args()
    cities = build_cities(args)

    if args.serve:
        run_server(cities, host=args.host, port=args.port)
        return

    results = get_weather_for_cities(cities)
    for line in format_cli_output(results):
        print(line)


if __name__ == "__main__":
    main()
