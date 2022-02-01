from pathlib import Path

import boto3
import pytest

from retailer_scraper.tesco import TescoScraper
from retailer_scraper.s3 import upload_directory


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


@pytest.fixture()
def temp_bucket():
    s3 = boto3.resource('s3')
    bucket_name = 'retailer-test-bucket'
    bucket = s3.create_bucket(Bucket=bucket_name)

    s3_client = boto3.client('s3')
    path = Path(__file__).parent / 'files'
    upload_directory(path, s3_client, bucket_name)

    yield bucket

    for key in bucket.objects.all():
        key.delete()
    bucket.delete()


@pytest.fixture
def expected_keys():
    return [
        'dir1/random1',
        'dir1/random2',
        'dir2/random3.py'
    ]


def test_uploaded_dir(temp_bucket, expected_keys):
    actual_keys = [file.key for file in temp_bucket.objects.all()]
    assert set(expected_keys) == set(actual_keys)
