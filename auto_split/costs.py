import time
from functools import lru_cache

import requests
from bs4 import BeautifulSoup


@lru_cache()
def get_gas_price(ttl_hash=None):
    del ttl_hash
    return fetch_gas_price()


def fetch_gas_price():
    url = "https://www.bensinstation.nu/Malmö/"
    result = requests.get(url)
    if not result.status_code == 200:
        return

    try:
        soup = BeautifulSoup(result.text, "html.parser")
        cells = [c.text for c in soup.find_all("td") if c is not None]
        gas_costs_cells = [c for n, c in enumerate(cells) if n % 5 == 1]
        print(gas_costs_cells)
        gas_costs = [float(c) for c in gas_costs_cells if c != ""]
    except Exception as e:
        print("Error: could not parse gas price", e)
        return None

    if len(gas_costs) == 0:
        return 0
    return sum(gas_costs) / len(gas_costs)


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)
