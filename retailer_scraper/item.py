from typing import Dict

from bs4 import BeautifulSoup


class Item:
    def __init__(self, bs: BeautifulSoup):
        """
        Wrapper for a product.
        Parameters
        ----------
        bs: BeautifulSoup
            Object wrapping the product html content in the search results
        """
        self.soup = bs
        self.name = self.get_name()
        self._details = None

    def get_name(self) -> str:
        return self.soup.find(
            name='div',
            attrs={'class': 'product-details--wrapper'}
        ).find(name='h3').text

    @property
    def href(self):
        """
        Partial url of the product detail page
        """
        return self.soup.find(
                name='a',
                href=True
            )['href']

    @property
    def id(self):
        """
        Unique ID of the product
        """
        return self.href.split('/')[-1]

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, details_: Dict):
        self._details = details_

    def __repr__(self):
        return f'Item("{self.name}")'

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.details == other.details

    def __hash__(self):
        return hash(self.name)
