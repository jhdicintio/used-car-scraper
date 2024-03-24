import json
import logging
import os
import traceback
import urllib.request
from abc import abstractmethod, ABC
from typing import Any, Dict, List, Tuple

import bs4 as bs
import pandas as pd
from bs4.element import ResultSet, Tag

CARS_DOT_COM_BASE_URL: str = "https://www.cars.com/shopping/results/?"

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


class CarsDotComUrlBuilder:
    def __init__(self, base_url: str = CARS_DOT_COM_BASE_URL):
        self._base_url = base_url

    def build(
            self,
            make: str,
            models: List[str],
            max_distance: int,
            zip_code: int,
            page_size: int
    ) -> List[str]:
        urls = []
        for model in models:
            url = self._base_url \
                  + f"makes[]={make}" \
                  + f"&maximum_distance={max_distance}" \
                  + f"&models[]={make}-{model}" \
                  + "&page={0}" \
                  + f"&page_size={page_size}" \
                  + "&stock_type=all" \
                  + f"&zip={zip_code}"
            urls.append(url)
        return urls


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
                selected_vehicles, should_continue = CarsDotComScraper().run(url_to_process, DEFAULT_PAGE_SIZE)
                for vehicle in selected_vehicles:
                    if vehicle is not None:
                        vehicles.append(vehicle)
                print(f"Collected {len(vehicles)} cars.")
                page += 1
        return vehicles

    def _convert_to_dataframe(self, scraped_data: List[Dict[str, Any]]):
        return pd.DataFrame(scraped_data)

    def run(self, make: str, models: List[str], max_distance: int, zip_code: int):
        urls = self._build_urls(make, models, max_distance, zip_code)
        data = self._collect_data_from_urls(urls)
        dataframe = self._convert_to_dataframe(data)
        return dataframe


class Dataset:
    def __init__(self, name: str, parameters: Tuple):
        self._name = name
        self._parameters = parameters

    def _load_from_source(self, aggregator: CarsDotComDataAggregator) -> pd.DataFrame:
        return aggregator.run(*self._parameters)

    def _cache_exists(self) -> bool:
        return os.path.exists(f"{self._name}.csv")

    def _load_from_disk(self) -> pd.DataFrame:
        return pd.read_csv(f"{self._name}.csv")

    def _write_to_disk(self, dataframe: pd.DataFrame) -> None:
        dataframe.to_csv(f"{self._name}.csv")

    def load(self, aggregator: CarsDotComDataAggregator) -> pd.DataFrame:
        if self._cache_exists():
            return self._load_from_disk()
        else:
            dataframe = self._load_from_source(aggregator)
            self._write_to_disk(dataframe)
            return dataframe


if __name__ == '__main__':
    aggregator = CarsDotComDataAggregator(url_builder=CarsDotComUrlBuilder(), scraper=CarsDotComScraper())

    dataset = Dataset("toyota-mix", ("toyota", ["tacoma", "4runner", "tundra"], 100, 80302))

    dataframe = dataset.load(aggregator)

    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    print(dataframe.head(20))

    colors = {'tacoma': 'orange', '4runner': 'purple', "tundra": "green"}
    color_list = [colors[group] for group in dataframe['model']]

    ax = dataframe.plot.scatter(
        'mileage',
        'price',
        c=color_list,
        grid=True
    )
    legend_handles = [
        mpatches.Patch(color=colors['tacoma'], label='tacoma'),
        mpatches.Patch(color=colors['4runner'], label='4runner'),
        mpatches.Patch(color=colors['tundra'], label='tundra'),

    ]
    ax.legend(handles=legend_handles,
              loc='upper left')
    plt.show()
