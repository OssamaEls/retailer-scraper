import json
from math import ceil
from typing import List, Dict, Optional
from uuid import uuid4
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from urllib.request import urlretrieve

from headers import headers


def parse_html(url: str) -> BeautifulSoup:
    output = requests.get(url, headers=headers, timeout=5)
    page = output.text
    return BeautifulSoup(page, 'html.parser')


def get_text(
        bs: BeautifulSoup,
        *,
        name: str,
        attrs: Optional[Dict]
) -> str:
    soup = bs.find(name=name, attrs=attrs)
    return soup.text if soup is not None else "Info not available"


class TescoScraper:
    website = 'https://www.tesco.com'
    base_url = 'https://www.tesco.com/groceries/en-GB/search?query='
    num_items_per_page = 48

    def __init__(self, query: str):
        # TODO: create Item class
        self.query = query
        self._items = []
        self._items_details = []

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
        return [item for item in self._items if item is not None]

    def _individual_page_links(self) -> List[str]:
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

    @property
    def items_details(self) -> Optional[List[Dict]]:
        if self._items_details:
            return self._items_details
        # TODO: consider adding nutrition
        individual_page_links = self._individual_page_links()
        for i, detail_page in enumerate(map(parse_html, individual_page_links)):
            print(f'scraping data from {individual_page_links[i]}')
            try:
                product_id = individual_page_links[i].split('/')[-1]
                guid = uuid4()

                name = detail_page.find(
                    name='h1',
                    attrs={'class': 'product-details-tile__title'}
                ).text

                price = detail_page.find(
                    name='div',
                    attrs={'class': 'price-per-sellable-unit'}
                ).text

                price_per_quantity = get_text(
                    detail_page,
                    name='div',
                    attrs={'class': 'price-per-quantity-weight'}
                )

                image_link = detail_page.find(
                    name='div',
                    attrs={'class': 'product-image__container'}
                ).findChild(
                    name='img'
                )['src']

                # nutrition = get_text(
                #     detail_page,
                #     name='div',
                #     attrs={'class': 'gda'}
                # )

                self._items_details.append({
                    'id': str(product_id),
                    'GUID': str(guid),
                    'name': name,
                    'price': price,
                    'price_per_quantity': price_per_quantity,
                    'image_link': image_link,
                    # 'nutrition': nutrition
                })
            except AttributeError:
                self._items[i] = None

        return self._items_details

    def save_results_to_files(self):
        directory = Path(__file__).parent.parent / 'raw_data'
        os.makedirs(directory, exist_ok=True)

        for item_details in self.items_details:
            item_directory = directory / item_details['id']
            os.makedirs(item_directory, exist_ok=True)
            with open(item_directory / 'data.json', 'w', encoding='utf8') as f:
                json.dump(item_details, f, indent=4, ensure_ascii=False)
            urlretrieve(item_details['image_link'], item_directory / 'image.jpg')





# def get_nutrition(
#         bs: BeautifulSoup,
#         *,
#         name: str,
#         attrs: Optional[Dict]
# ):
#     soup = bs.find(name=name, attrs=attrs)
#     for child in soup.findChildren(name='div', attrs=)


tesco_scraper = TescoScraper('free range eggs')
tesco_scraper.run_query()
items = tesco_scraper.items
# links = tesco_scraper._individual_page_links()
items_details = tesco_scraper.items_details
tesco_scraper.save_results_to_files()

