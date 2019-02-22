from core.playlist_crawler import PlaylistCrawler
from zipfile import ZipFile
import boto3
import glob
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    playlist = os.getenv('SPOTIFY_PLAYLIST', None)

    # TODO: Make this work without these if possible
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID', '')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    aws_s3_bucket_name = os.getenv('AWS_S3_BUCKET_NAME', '')

    if aws_access_key == '':
        logger.critical("aws access key id not set, cannot continue.")
        exit(1)

    if aws_secret_key == '':
        logger.critical("aws secret access key not set, cannot continue.")
        exit(1)

    if aws_s3_bucket_name == '':
        logger.critical("aws ws3 bucket name not set, cannot continue.")
        exit(1)

    logger.info("Downloading previews...")
    crawler = PlaylistCrawler(playlist)
    crawler.download_previews()

    playlist_id = os.path.basename(playlist)
    zip_file_name = f"/tmp/{playlist_id }.zip"
    logger.info(f"Zipping mp3 payload to zip at {zip_file_name}...")
    with ZipFile(zip_file_name, 'w') as zf:
        for f in glob.glob("/tmp/*.mp3"):
            zf.write(f)

    logger.info(f"Uploading payload to S3 {aws_s3_bucket_name}...")
    s3 = boto3.resource('s3')
    with open(zip_file_name, 'rb') as f:
        s3.Bucket(aws_s3_bucket_name).put_object(
            Key=f"{playlist_id}.zip", Body=f)

    logger.info("Process complete!")


if __name__ == '__main__':
    main()
