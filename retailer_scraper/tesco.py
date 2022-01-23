import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from math import ceil

from headers import headers


class TescoScraper:
    base_url = 'https://www.tesco.com/groceries/en-GB/search?query='

    def __init__(self, query: str):
        self.query = query
        self._results = None

    def run_query(self):
        url = self.base_url + quote(self.query)
        output = requests.get(url, headers=headers, timeout=5)
        first_page = output.text
        soup = BeautifulSoup(first_page, 'html.parser')
        found_items = soup.find(name='div', attrs={'class': 'product-list-container'})
        if not found_items:
            self._results = []
            return
        # second <strong> tag under the div tag with class 'pagination__items-displayed' has text: 'xxx items'
        number_of_items = soup.find(
            name='div',
            attrs={'class': 'pagination__items-displayed'}
        ).findChildren(
            name='strong'
        )[
            1
        ].text.split()[0]
        number_of_pages = ceil(int(number_of_items)/50)
        # for page in number_of_pages:
        #     item = soup.find(
        #         name='li',
        #         attrs={'class': 'product-list--list-item'}
        #     )

        return soup

    @property
    def found_exact_match(self):
        assert self._results is not None, 'You have not run any query yet.'



tesco_scraper = TescoScraper('eggs')
soup = tesco_scraper.run_query()
# result = soup.find(name='p', attrs={'class': 'results-title'})
result = soup.find_all(
                name='li',
                attrs={'class': 'product-list--list-item'}
            )