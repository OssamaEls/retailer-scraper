import pytest
from urllib.parse import quote

from retailer_scraper.tesco import TescoScraper


@pytest.fixture
def fool_query_scraper():
    return TescoScraper('khhkge7943k')


@pytest.fixture
def typo_query_scraper():
    return TescoScraper('snikers')


@pytest.fixture
def normal_query_scraper():
    return TescoScraper('snickers')


@pytest.fixture
def multiple_words_query_scraper():
    return TescoScraper('free_range_eggs')


def test_no_result(fool_query_scraper):
    assert len(fool_query_scraper.items) == 0


def test_result_without_exact_match(typo_query_scraper):
    assert len(typo_query_scraper.items) > 0


def test_result_with_exact_match(normal_query_scraper):
    assert len(normal_query_scraper.items) > 0


def test_compare_queries_results(typo_query_scraper, normal_query_scraper):
    details_left = [
        {
            k: v
            for k, v
            in item.details.items()
            if k != 'GUID'
        }
        for item
        in typo_query_scraper.items
    ]
    details_right = [
        {
            k: v
            for k, v
            in item.details.items()
            if k != 'GUID'
        }
        for item
        in normal_query_scraper.items
    ]

    assert len(details_left) == len(details_right)
    for item_details in details_left:
        assert item_details in details_right
