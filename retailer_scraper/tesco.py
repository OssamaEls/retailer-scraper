import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from math import ceil
from typing import List, Dict

from headers import headers


def parse_html(url: str) -> BeautifulSoup:
    output = requests.get(url, headers=headers, timeout=5)
    page = output.text
    return BeautifulSoup(page, 'html.parser')


class TescoScraper:
    website = 'https://www.tesco.com'
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
            self.website +
            item.find(
                name='a',
                href=True
            )['href']
            for item in self.items
        ]

    def parse_page(self, page_number: int) -> BeautifulSoup:
        return parse_html(
            self.get_url(page_number)
        )

    def items_details(self) -> List[Dict]:
        items_details_ = []
        individual_page_links = self.individual_page_links()
        for i, detail_page in enumerate(map(parse_html, individual_page_links)):
            print(f'scraping data from {individual_page_links[i]}')
            try:
                name = detail_page.find(
                    name='h1',
                    attrs={'class': 'product-details-tile__title'}
                ).text
                price = detail_page.find(
                    name='div',
                    attrs={'class': 'price-per-sellable-unit'}
                ).text
                price_per_quantity = detail_page.find(
                    name='div',
                    attrs={'class': 'price-per-quantity-weight'}
                ).text
                items_details_.append({
                    'name': name,
                    'price': price,
                    'price_per_quantity': price_per_quantity
                })
            except AttributeError:
                self._items.pop(i)

        return items_details_


tesco_scraper = TescoScraper('free range eggs')
tesco_scraper.run_query()
items = tesco_scraper.items
links = tesco_scraper.individual_page_links
items_details = tesco_scraper.items_details()

