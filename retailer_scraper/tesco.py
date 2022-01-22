import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


class TescoScraper:
    base_url = 'https://www.tesco.com/groceries/en-GB/search?query='

    def __init__(self, query: str):
        self.query = query
        self._results = None

    def run_query(self):
        url = self.base_url + quote(self.query)
        first_page = requests.get(url)
        first_page_html = first_page.text
        soup = BeautifulSoup(first_page_html, 'html.parser')
        return soup



