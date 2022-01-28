from uuid import uuid4

from bs4 import BeautifulSoup


class Item:
    def __init__(self, id: int):
        self.id = id
        self.guid = uuid4()
        self.details = None



