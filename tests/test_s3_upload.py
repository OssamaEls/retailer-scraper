from pathlib import Path

import boto3
import pytest

from retailer_scraper.s3 import upload_directory


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
