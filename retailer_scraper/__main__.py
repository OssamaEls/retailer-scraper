import shutil
from pathlib import Path

import boto3

from tesco import TescoScraper
from s3 import upload_directory
from analysis import print_results


def main():
    print('Thank you for using this command-line scraper.')
    query = input('Please enter your query (groceries): ')

    tesco_scraper = TescoScraper(query)
    path = Path(__file__).parent.parent / 'raw_data'
    tesco_scraper.save_to_files_and_db(path)

    s3_client = boto3.client('s3')
    upload_directory(path, s3_client, 'retailer-scraper')
    shutil.rmtree(path)

    items_details = [item.details for item in tesco_scraper.items]
    print_results(items_details)


if __name__ == '__main__':
    import logging.config

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)                  # to not show "Found aws credentials..."
    main()
