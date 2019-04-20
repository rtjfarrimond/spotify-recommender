from boto3.dynamodb.conditions import Key
import boto3
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamoTable(object):

    def __init__(self, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def __repr__(self):
        return self.table_name

    def get_item(self, key):
        logger.info(f"key={key}")
        try:
            response = self.table.get_item(Key=key)
            return response['Item']

        except KeyError:
            return None

    def get_item_from_index(self, index_name, key, value):
        res = self.table.query(
            IndexName=index_name,
            KeyConditionExpression=Key(key).eq(value)
        )['Items'][0]

        ret = {}

        AttributesToGet=['TrackId', 'Artists', 'Title', 'PreviewUrl']
        for k in res.keys():
            if k in AttributesToGet:
                ret[k] = res[k]

        return ret


def main(dynamo_table, annoy_id, index_name, index_hash_key):
    response = dynamo_table.get_item_from_index(
        index_name, index_hash_key, annoy_id)

    items = response['Items']
    n_items = len(items)
    if n_items > 1:
        raise ValueError(f"Unexpected number of items returned: {n_items}")
    elif n_items == 0:
        return None
    else:
        select = ['TrackId', 'Artists', 'Title', 'PreviewUrl']
        item = response['Items'][0]
        item = {item[attr] for attr in select}
        return item


if __name__ == '__main__':
    table_name = 'spot-rec-audio-metadata'
    dynamo_table = DynamoTable(table_name)

    annoy_id = 11741
    index_name = 'annoy_index'
    key = 'AnnoyIndex'
    item = main(dynamo_table, annoy_id, index_name, key)
    print(item)
