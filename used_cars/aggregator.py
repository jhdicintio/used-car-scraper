import logging
from typing import Any, Dict, List

import pandas as pd

from used_cars.scraper import CarsDotComScraper
from used_cars.url_builder import CarsDotComUrlBuilder

CARS_DOT_COM_BASE_URL: str = "https://www.cars.com/shopping/results/?"

DEFAULT_PAGE_SIZE: int = 100

logger = logging.getLogger(__name__)


class CarsDotComDataAggregator:
    def __init__(self, url_builder: CarsDotComUrlBuilder, scraper: CarsDotComScraper):
        self._url_builder = url_builder
        self._scraper = scraper

    def _build_urls(self, make: str, models: List[str], max_distance: int, zip_code: int) -> List[str]:
        return self._url_builder.build(
            make=make,
            models=models,
            max_distance=max_distance,
            zip_code=zip_code,
            page_size=DEFAULT_PAGE_SIZE
        )

    def _collect_data_from_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        vehicles = []
        for url in urls:
            page = 1
            should_continue = True
            while should_continue:
                url_to_process = url.format(str(page))
                selected_vehicles, should_continue = self._scraper.run(url_to_process, DEFAULT_PAGE_SIZE)
                for vehicle in selected_vehicles:
                    if vehicle is not None:
                        vehicles.append(vehicle)
                print(f"Collected {len(vehicles)} cars.")
                page += 1
        return vehicles

    @staticmethod
    def _convert_to_dataframe(scraped_data: List[Dict[str, Any]]):
        return pd.DataFrame(scraped_data)

    def run(self, make: str, models: List[str], max_distance: int, zip_code: int):
        urls = self._build_urls(make, models, max_distance, zip_code)
        data = self._collect_data_from_urls(urls)
        dataframe = self._convert_to_dataframe(data)
        return dataframe
