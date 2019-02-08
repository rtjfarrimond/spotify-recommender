from core.playlist_crawler import PlaylistCrawler
import boto3
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    username = os.getenv('SPOTIFY_USERNAME', None)
    playlist = os.getenv('SPOTIFY_PLAYLIST', None)
    audio_path = os.getenv('AUDIO_PATH', './audio')

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

    if not os.path.exists(audio_path):
        os.mkdir(audio_path)
    logger.info(f"main method: {aws_s3_bucket_name}")
    crawler = PlaylistCrawler(
        username, playlist, audio_path, aws_s3_bucket_name)
    crawler.download_previews()


if __name__ == '__main__':
    main()
