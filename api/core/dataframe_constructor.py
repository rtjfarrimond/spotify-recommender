from core.settings import DYNAMODB_TABLE
from core.settings import ANNOY_INDEX_COL
import boto3
import json
import logging
import os
import pandas as pd
import pickle


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFrameConstructor(object):

    CACHE_FILE = '/tmp/item_cache.pkl'
    df = None

    def __init__(self, table_name, hash_key):
        self.table_name = table_name
        self.hash_key = hash_key

    def fetch_all(self):
        # TODO: Refactor below to use a DynamoDB object.
        dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")
        table = dynamodb.Table(self.table_name)
        items = []
        last_evaluated_key = None
        page = 1
        logger.info(f"Fetching page {page}...")
        response = table.scan()

        while True:
            try:
                items += response['Items']
                last_evaluated_key = response['LastEvaluatedKey']
                page += 1
                logger.info(f"Fetching page {page}...")
                response = table.scan(ExclusiveStartKey=last_evaluated_key)
            except KeyError:
                break

        logger.info(f"Fetched {len(items)} from database.")
        return items

    def build_dataframe(self):
        if not os.path.isfile(self.CACHE_FILE):
            items = self.fetch_all()
            logger.info(f"Caching items to file {self.CACHE_FILE}...")
            with open(self.CACHE_FILE, 'wb') as f:
                pickle.dump(items, f)
        else:
            logger.info(f"Loading items from cache file {self.CACHE_FILE}...")
            with open(self.CACHE_FILE, 'rb') as f:
                items = pickle.load(f)

        D = pd.DataFrame(items)
        self.df = D.set_index(ANNOY_INDEX_COL)
        logger.info(f"Built DataFrame with shape {self.df.shape}.")


    def get_dataframe(self):
        if not self.df:
            self.build_dataframe()
        return self.df

if __name__ == '__main__':
    main()
