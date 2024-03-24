import logging

from used_cars.aggregator import CarsDotComDataAggregator
from used_cars.dataset import Dataset
from used_cars.scraper import CarsDotComScraper
from used_cars.url_builder import CarsDotComUrlBuilder

CARS_DOT_COM_BASE_URL: str = "https://www.cars.com/shopping/results/?"

DEFAULT_PAGE_SIZE: int = 100

logger = logging.getLogger(__name__)

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
