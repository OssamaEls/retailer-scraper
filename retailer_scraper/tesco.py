import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from math import ceil
from typing import List

from headers import headers


class TescoScraper:
    base_url = 'https://www.tesco.com/groceries/en-GB/search?query='
    num_items_per_page = 48

    def __init__(self, query: str):
        self.query = query
        self._items = []

    def get_url(self, page_number: int):
        return f'{self.base_url}{quote(self.query)}&page={page_number}&count={self.num_items_per_page}'

    def run_query(self):
        soup = self.parse_page(1)
        found_items = soup.find(name='div', attrs={'class': 'product-list-container'})
        if not found_items:
            return
        # second <strong> tag under the div tag with class 'pagination__items-displayed' has text: 'xxx items'
        num_items = soup.find(
            name='div',
            attrs={'class': 'pagination__items-displayed'}
        ).findChildren(
            name='strong'
        )[
            1
        ].text.split()[0]
        number_of_pages = ceil(int(num_items)/self.num_items_per_page)
        for page_number in range(1, number_of_pages + 1):
            if page_number != 1:
                soup = self.parse_page(page_number)
            self._items += soup.find_all(
                name='li',
                attrs={'class': 'product-list--list-item'}
            )[:self.num_items_per_page]

    @property
    def found_exact_match(self):
        assert self._items is not None, 'You have not run any query yet.'

    @property
    def items(self):
        return self._items

    def individual_page_links(self) -> List[str]:
        return [
            item.find(
                name='a',
                href=True
            )['href']
            for item in self.items
        ]

    def parse_page(self, page_number: int) -> BeautifulSoup:
        url = self.get_url(page_number)
        output = requests.get(url, headers=headers, timeout=5)
        page = output.text
        return BeautifulSoup(page, 'html.parser')


tesco_scraper = TescoScraper('eggs')
tesco_scraper.run_query()
items = tesco_scraper.items
links = tesco_scraper.individual_page_links()

