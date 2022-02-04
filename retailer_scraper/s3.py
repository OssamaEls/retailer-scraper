import os
from pathlib import Path
import shutil

import boto3


def upload_directory(path: Path, s3_client, bucket_name):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = str(Path(root) / file)
            relative_path = os.path.relpath(file_path, path)
            print('path is ', path)
            print('file_path is ', file_path)
            print('relative_path is ', relative_path)
            s3_client.upload_file(
                file_path,
                bucket_name,
                relative_path
            )


s3_client = boto3.client('s3')
path = Path(__file__).parent.parent / 'raw_data'
upload_directory(path, s3_client, 'retailer-scraper')

shutil.rmtree(path)
