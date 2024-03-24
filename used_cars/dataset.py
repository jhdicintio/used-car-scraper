import os
from typing import Tuple

import pandas as pd

from used_cars.aggregator import CarsDotComDataAggregator


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
