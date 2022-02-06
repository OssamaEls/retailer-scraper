import logging
from math import ceil
from typing import List
# from uuid import uuid4
import os
from pathlib import Path
import re

from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import quote
from urllib.request import urlretrieve

from retailer_scraper.item import Item
from retailer_scraper.util import get_text, parse_html, make_session, to_json
from retailer_scraper.db_model import Product


# logger = logging.getLogger(
#     __name__
# )

# TODO: use multi-threading


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
        self.session = make_session()
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
            logging.info('No result found.')
            return

        if (
                get_text(
                    soup,
                    name='p',
                    attrs={'class': 'results-title'}
                )[:16] ==
                (no_exact_match := 'No exact matches found')
        ):
            logging.warning(f"{no_exact_match} for your query '{self.query}'.")

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

        logging.info(f"Found {num_items} items for your query. Fetching {num_pages} {'pages' if num_pages>1 else 'page'}.")

        for page_number in tqdm(range(1, num_pages + 1)):
            logging.info(f"Fetching page {page_number}...")
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
    def items(self) -> List[Item]:
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
            - category
            - name of the product
            - price
            - price per quantity
            - image url
        """
        # TODO: consider adding nutrition
        # TODO: consider adding review stats

        logging.info('Fetching data from individual pages.')

        individual_page_links = self._individual_page_links()

        float_pattern = "\d+\.\d+"

        for i, detail_page in enumerate(map(parse_html, individual_page_links)):

            logging.info(f'Scraping data from {individual_page_links[i]}')

            try:
                product_id = individual_page_links[i].split('/')[-1]

                category = detail_page.find_all(
                    name='span',
                    attrs={'class': 'styled__Text-sc-1xbujuz-1 ldbwMG beans-link__text'}
                )[-2].text

                name = detail_page.find(
                    name='h1',
                    attrs={'class': 'product-details-tile__title'}
                ).text

                price = float(
                    re.findall(
                        float_pattern,
                        detail_page.find(
                            name='div',
                            attrs={'class': 'price-per-sellable-unit'}
                        ).text
                    )[0]
                )

                price_per_quantity_info = get_text(
                    detail_page,
                    name='div',
                    attrs={'class': 'price-per-quantity-weight'}
                )

                price_per_quantity = float(
                    re.findall(
                        float_pattern,
                        price_per_quantity_info
                    )[0]
                )
                base_quantity = price_per_quantity_info.split('/')[-1]

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
                    # 'GUID': str(guid),
                    'name': name,
                    'category': category,
                    'price': price,
                    'price_per_quantity': price_per_quantity,
                    'base_quantity': base_quantity,
                    'image_link': image_link,
                    # 'nutrition': nutrition
                }
            except AttributeError:
                self._items[i] = None

        logging.info('Scraping finished.')

    def save_to_files_and_db(self, output_directory: Path):
        """
        Save items details in JSON and images.
        Output directory: raw_data/<category>/<item_id>
        """
        if not self._items:
            print('No result found.')
            return

        os.makedirs(output_directory, exist_ok=True)

        logging.info("Saving to files and to the database (if not existing)")

        for item in self.items:
            item_details = item.details

            product = Product(**item_details)
            item_directory = output_directory / f"{item_details['category']}/{item_details['id']}"

            if entry := Product.get_entry_if_exists(
                                product,
                                self.session
                            ):
                # print('found entry')
                # print(entry, type(entry))
                if entry.price != product.price:
                    to_json(item_details, item_directory)
                else:
                    continue
            else:
                to_json(item_details, item_directory)
                urlretrieve(item_details['image_link'], item_directory / f"image.jpg")
            self.session.add(product)

        self.session.commit()
        self.session.close()


# tesco_scraper = TescoScraper('snikers')
# path = Path(__file__).parent.parent / 'raw_data'
# items_details = [item.details for item in tesco_scraper.items]
# tesco_scraper.save_to_files_and_db(path)
