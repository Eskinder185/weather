# Async Weather CLI 

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Async](https://img.shields.io/badge/Async-asyncio%20%7C%20aiohttp-5b5)
![Auth](https://img.shields.io/badge/API-No%20API%20key%20required-informational)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A small **command-line** app that fetches **current temperature** and **wind speed** for one or more locations **concurrently** using `asyncio` + `aiohttp`.  
Backed by **Open-Meteo** (free for non-commercial use, no key needed).

---

## ✨ What it does
- Queries Open-Meteo’s **Current Weather** for `temperature_2m` and `wind_speed_10m`
- Runs **many requests at the same time** (configurable connection limit)
- Prints concise, human-readable lines per location
