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

from retailer_scraper.headers import headers
from retailer_scraper.item import Item


# TODO: use logging
# TODO: use multi-threading

def parse_html(url: str) -> BeautifulSoup:
    """
    Routine to get a BeautifulSoup object from an url.
    Parameters
    ----------
    url
    Returns
    -------
        BeautifulSoup object wrapping the html content of the web page
    """
    output = requests.get(url, headers=headers, timeout=5)
    page = output.text
    return BeautifulSoup(page, 'html.parser')


def get_text(
        bs: BeautifulSoup,
        *,
        name: str,
        attrs: Optional[Dict]
) -> str:
    """
    Parameters
    ----------
    bs : BeautifulSoup
        Object wrapping some html content
    name
    attrs
        Parameters to bs
    Returns
    -------
    str
        Text wrapped by the soup request or a default string if soup is None
    """
    soup = bs.find(name=name, attrs=attrs)
    return soup.text if soup is not None else "Info not available"


class TescoScraper:
    website = 'https://www.tesco.com'
    base_url = f'{website}/groceries/en-GB/search?query='
    num_items_per_page = 48

    def __init__(self, query: str):
        """
        Scraper to extract all relevant data to the query
        Parameters
        ----------
        query : str
            Any input a user would normally type in the website search bar
        """
        self.query = query
        self._items = []
        self.run_query()

    def run_query(self):
        """
        - Fetch all results from the query
        - Extract data from detailed pages
        """
        self.get_all_page_results()
        if self._items:
            self.get_items_details()

    def get_url(self, page_number: int):
        """
        Parameters
        ----------
        page_number : int
            Page number of the search results
        Returns
        -------
        str
            The url of that page
        """
        return f'{self.base_url}{quote(self.query)}&page={page_number}&count={self.num_items_per_page}'

    def get_all_page_results(self):
        """
        Save all Item objects in self._items
        """
        soup = self.parse_page(1)
        found_items = soup.find(name='div', attrs={'class': 'product-list-container'})

        if not found_items:
            return

        if (
                get_text(
                    soup,
                    name='p',
                    attrs={'class': 'results-title'}
                )[:16] ==
                (no_exact_match := 'No exact matches found')
        ):
            print(f'Warning: {no_exact_match} for your query {self.query}.')

        # second <strong> tag under the div tag with class 'pagination__items-displayed' has text: 'xxx items'
        num_items = soup.find(
            name='div',
            attrs={'class': 'pagination__items-displayed'}
        ).findChildren(
            name='strong'
        )[
            1
        ].text.split()[0]

        num_pages = ceil(int(num_items)/self.num_items_per_page)

        for page_number in range(1, num_pages + 1):
            if page_number != 1:
                soup = self.parse_page(page_number)
            self._items += [
                Item(bs)
                for bs
                in soup.find_all(
                        name='li',
                        attrs={'class': 'product-list--list-item'}
                    )[:self.num_items_per_page]
            ]

    @property
    def items(self):
        return [item for item in self._items if item is not None]

    def _individual_page_links(self) -> List[str]:
        return [
            f'{self.website}{item.href}'
            for item in self.items
        ]

    def parse_page(self, page_number: int) -> BeautifulSoup:
        """
        Parse html content of the search result page
        Parameters
        ----------
        page_number
            Page number of the search results
        Returns
        -------
            BeautifulSoup object wrapping the html content of the page
        """
        return parse_html(
            self.get_url(page_number)
        )

    def get_items_details(self):
        """
        Extract data from the details page:
            - name of the product
            - price
            - price per quantity
            - image url
        """
        # TODO: consider adding nutrition
        # TODO: consider adding review stats
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

                self._items[i].details = {
                    'id': str(product_id),
                    'GUID': str(guid),
                    'name': name,
                    'price': price,
                    'price_per_quantity': price_per_quantity,
                    'image_link': image_link,
                    # 'nutrition': nutrition
                }
            except AttributeError:
                self._items[i] = None

    def save_results_to_files(self):
        """
        Save items details in JSON and images.
        Output directory: raw_data/<query>/<item_id>
        """
        # TODO: symlinks for existing items
        if not self._items:
            print('No result found.')
            return
        directory = Path(__file__).parent.parent / f'raw_data/{self.query}'
        os.makedirs(directory, exist_ok=True)

        for item in self.items:
            item_details = item.details
            item_directory = directory / item_details['id']
            os.makedirs(item_directory, exist_ok=True)
            with open(item_directory / 'data.json', 'w', encoding='utf8') as f:
                json.dump(item_details, f, indent=4, ensure_ascii=False)
            urlretrieve(item_details['image_link'], item_directory / f"{item_details['id']}.jpg")


tesco_scraper = TescoScraper('snickers')
items = tesco_scraper.items
items_details = [item.details for item in items]
tesco_scraper.save_results_to_files()

