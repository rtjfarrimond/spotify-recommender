import os


S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", None)
ZIP_FILE_NAME = os.getenv("ZIP_FILE_NAME", None)
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", None)
