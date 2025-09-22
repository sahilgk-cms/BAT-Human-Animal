from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError
from datetime import datetime
import os
import sys
current_path = os.path.dirname(__file__)
root_path = os.path.dirname(current_path)
sys.path.append(root_path)
from config import MONGODB_URI, MONGODB_DATABASE, MONGODB_UNIQUE_KEY
from logging_config import get_logger


logger = get_logger(__name__)

class MongoDBHandler():
    def __init__(self, collection_name):
        self.client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

        self.db = self.client[MONGODB_DATABASE]
        self.collection = self.db[collection_name]

        self.collection.create_index(MONGODB_UNIQUE_KEY, unique=True)


    def get_collection(self):
        return self.collection
    

    def insert_data(self, data):
        inserted_ids = []

        for document in data:
            try:
                result = self.collection.insert_one(document)
                inserted_ids.append(result.inserted_id)
            except DuplicateKeyError:
                logger.info(f"Duplicate key error for document: {document['article_links']}. Skipping insertion.")
                continue
        
        logger.info(f"Inserted {len(inserted_ids)} records into the database.")


    def read_data(self, query=None, sort=None, limit=None):
        if query:
            data = self.collection.find(query)
        else:
            data = self.collection.find()

        if sort:
            data = data.sort(sort)

        if limit:
            data = data.limit(limit)

        data_list = list(data)
        return data_list
    
    def update_data(self, query, data):
        update_query = {"$set": data}
        self.collection.update_one(query, update_query)


    def delete_data(self, data={}, archiving=False):
        if not archiving and data:
            self.collection.delete_one(data)
        else:
            self.collection.delete_many(filter={'scraped_date':{'$gte':datetime.strptime('01/01/2023', '%d/%m/%Y')}})


    def close_connection(self):
        self.client.close()