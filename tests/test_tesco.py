import pytest
from urllib.parse import quote

from retailer_scraper.tesco import TescoScraper


@pytest.fixture
def fool_query():
    return 'khhkge7943k'


@pytest.fixture
def typo_query():
    return 'snikers'


@pytest.fixture
def normal_query():
    return 'snickers'


@pytest.fixture
def multiple_words_query():
    return 'free_range_eggs'


def test_no_result(fool_query):
    tesco_scraper = TescoScraper(fool_query)
    assert len(tesco_scraper.items) == 0


def test_result_without_exact_match(typo_query):
    tesco_scraper = TescoScraper(typo_query)
    assert len(tesco_scraper.items) > 0


def test_result_with_exact_match(normal_query):
    tesco_scraper = TescoScraper(normal_query)
    assert len(tesco_scraper.items) > 0


def test_compare_queries_results(typo_query, normal_query):
    pass




