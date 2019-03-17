import boto3
import json
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_CODE = "spot-rec"


def get_parameter(param_name):
    name = f"/{SYSTEM_CODE}/{param_name}"
    if not name or name == "":
        raise ValueError("name not passed.")

    client = boto3.client('ssm')
    response = client.get_parameter(Name=name)
    return response ['Parameter']['Value']


JOB_NAME_PREFIX = get_parameter('job_name_prefix')
JOB_QUEUE = get_parameter("extractor_job_queue")
JOB_DEFINITION = get_parameter("extractor_job_definition")
DYNAMODB_TABLE = get_parameter("dynamodb")


def submit_job(event, context):
    logger.info(f"Event:\n{event}")

    client = boto3.client('batch')

    for record in event['Records']:
        s3 = record['s3']
        bucket_name = s3['bucket']['name']
        zip_file_name = s3['object']['key']

        logger.info(f"Bucket name: {bucket_name}")
        logger.info(f"Zip file name: {zip_file_name}")

        job_name = JOB_NAME_PREFIX + zip_file_name.replace('.zip', '')

        client.submit_job(
            jobName=job_name,
            jobQueue=JOB_QUEUE,
            jobDefinition=JOB_DEFINITION,
            containerOverrides={
                'environment': [
                    {
                        "name": "DYNAMODB_TABLE",
                        "value": DYNAMODB_TABLE
                    },
                    {
                        "name": "ZIP_FILE_NAME",
                        "value": zip_file_name
                    },
                    {
                        "name": "S3_BUCKET_NAME",
                        "value": bucket_name
                    },
                ]
            }
        )

        logger.info(f"Submitted job {job_name} to queue {JOB_QUEUE} using " +
                    f"definition {JOB_DEFINITION}.")
