from uuid import uuid4

from bs4 import BeautifulSoup


class Item:
    def __init__(self, bs: BeautifulSoup):
        self.soup = bs
        self.guid = uuid4()
        self.details = None

    def find(self, *args, **kwargs):
        return self.soup.find(*args, **kwargs)

    @property
    def id(self):
        return self.soup.find(
                name='a',
                href=True
            )['href'][1:]

