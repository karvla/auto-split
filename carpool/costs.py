from bs4 import BeautifulSoup
import requests
from functools import lru_cache
import time


@lru_cache()
def get_gas_price(ttl_hash=None):
    del ttl_hash
    return fetch_gas_price()


def fetch_gas_price():
    url = "https://www.bensinstation.nu/Malmö/"
    result = requests.get(url)
    if not result.status_code == 200:
        return

    soup = BeautifulSoup(result.text, "html.parser")
    cells = [c.text for c in soup.find_all("td")]
    gas_costs = [float(c) for n, c in enumerate(cells[1:]) if n % 5 == 0]
    return sum(gas_costs) / len(gas_costs)


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)
