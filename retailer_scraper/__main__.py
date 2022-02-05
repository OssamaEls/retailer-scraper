import shutil
from pathlib import Path

import boto3

from retailer_scraper.tesco import TescoScraper
from retailer_scraper.s3 import upload_directory


def main():
    print('Thank you for using this command-line scraper.')
    query = input('Please enter your query (groceries). The results will be saved in our database.')

    tesco_scraper = TescoScraper(query)
    path = Path(__file__).parent.parent / 'raw_data'
    tesco_scraper.save_to_files_and_db(path)

    s3_client = boto3.client('s3')

    upload_directory(path, s3_client, 'retailer-scraper')

    shutil.rmtree(path)
