import json
import logging
import traceback
import urllib.request
from abc import abstractmethod, ABC
from typing import Any, Dict, List, Tuple

import bs4 as bs
from bs4.element import ResultSet, Tag

DEFAULT_PAGE_SIZE: int = 100

logger = logging.getLogger(__name__)


class UsedCarScraper(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _collect_html(self, url) -> ResultSet:
        raise NotImplementedError

    @abstractmethod
    def _parse_div(self, div: Tag) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def run(self, url: str) -> List[Dict[str, Any]]:
        pass


class CarsDotComScraper:
    def __init__(self):
        pass

    def _collect_html(self, url) -> ResultSet:
        html = urllib.request.urlopen(url).read()
        parsed_html = bs.BeautifulSoup(html, 'lxml')
        vehicle_divs = parsed_html.find_all('div', class_='vehicle-details')
        return vehicle_divs

    @staticmethod
    def _parse_mileage(mileage: str) -> int:
        return int(mileage.split(" ")[0].replace(",", ""))

    def _parse_div(self, div: Tag) -> Dict[str, Any]:
        vehicle = {}
        mileage_div = div.find_all('div', class_='mileage')
        vehicle["mileage"] = self._parse_mileage(mileage_div[0].string) if mileage_div else 0

        listing_info_div = div.find_all(
            'button', class_='vehicle-badging has-miles-from ep-theme-hubcap'
        )
        if listing_info_div:
            listing_info = json.loads(listing_info_div[0]['data-override-payload'])
            vehicle["trim"] = listing_info["trim"]
            vehicle["make"] = listing_info["make"]
            vehicle["model"] = listing_info["model"]
            vehicle["year"] = listing_info["model_year"]
            vehicle["used_or_new"] = listing_info["stock_type"]
            vehicle["price"] = listing_info["price"]
            vehicle["listing_id"] = listing_info["listing_id"]
            vehicle["source"] = "cars.com"
            return vehicle
        else:
            pass

    def run(self, url: str, expected_page_length: int) -> Tuple[List[Dict[str, Any]], bool]:
        vehicle_divs = self._collect_html(url)
        should_continue = len(vehicle_divs) == expected_page_length

        vehicles = []
        for div in vehicle_divs:
            try:
                vehicle = self._parse_div(div)
                vehicles.append(vehicle)
            except IndexError as e:
                print(div)
                traceback.print_exc()
                continue
        return vehicles, should_continue
