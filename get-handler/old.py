# import boto3
# import json
# import logging
# 
# 
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# 
# 
# def get_table_name():
#     ssm = boto3.client('ssm')
#     dynamo_db_json = ssm.get_parameter(
#         Name='/spot-rec/dynamodb-table', WithDecryption=True)
#     return dynamo_db_json['Parameter']['Value']

def get_request_handler(event, context):
    # table_name = get_table_name()
    # dynamodb = boto3.resource(
    #     "dynamodb",
    #     region_name='eu-west-1')    # Can we get this from the environment?

    # print(table_name)

    # return {
    #     "statusCode": 200,
    #     "body": table_name
    # }
    # logger.info(event)

    return {
        "statusCode": 200,
        "body": event
    }


# if __name__ == '__main__':
#     print(get_request_handler('', ''))
