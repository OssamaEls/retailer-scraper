import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

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
        results = BeautifulSoup(first_page, 'html.parser')
        return results

    @property
    def found_exact_match(self):
        assert self._results is not None, 'You have not run any query yet.'



tesco_scraper = TescoScraper('kfdsgfbskdhbd')
soup = tesco_scraper.run_query()
result = soup.find(name='p', attrs={'class': 'results-title'})
