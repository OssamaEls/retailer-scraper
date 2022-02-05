import logging
import os
from pathlib import Path



def upload_directory(path: Path, s3_client, bucket_name):
    """
    Upload whole directory to an s3 bucket
    Parameters
    ----------
    path : Path
        Path of the directory to upload to s3
    s3_client
    bucket_name
    """
    logging.info('Uploading to s3.')
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = str(Path(root) / file)
            relative_path = os.path.relpath(file_path, path)
            # print('path is ', path)
            # print('file_path is ', file_path)
            # print('relative_path is ', relative_path)
            logging.info(f"Uploading {relative_path}")
            s3_client.upload_file(
                file_path,
                bucket_name,
                relative_path
            )

