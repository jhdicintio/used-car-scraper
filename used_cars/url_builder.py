import logging
from typing import List

CARS_DOT_COM_BASE_URL: str = "https://www.cars.com/shopping/results/?"

DEFAULT_PAGE_SIZE: int = 100

logger = logging.getLogger(__name__)


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
