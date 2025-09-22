import logging
from dotenv import load_dotenv
import os
import sys
current_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(current_path))
sys.path.append(root_path)
from handlers.mongodb_handler import MongoDBHandler

load_dotenv()
scraped_collection_name = os.getenv('MONGODB_SCRAPED_COLLECTION')
processed_collection_name = os.getenv('MONGODB_PROCESSED_COLLECTION')
alerts_system_collection_name = os.getenv('MONGODB_ALERTS_SYSTEM_COLLECTION')

def load_to_mongodb(caller, dataframe):
    '''
    Loads the data into the MongoDB database based on the caller.
    :param caller: The calling module of the function.
    :param dataframe: DataFrame containing dates, articles, and article links.
    '''

    records = dataframe.to_dict(orient='records')
    try:
        if caller == "Scrapers":
            collection_name = scraped_collection_name
        else:
            error_message = "Invalid caller: " + caller
            logging.error(error_message)

        mongodb_handler = MongoDBHandler(collection_name)
        existing_data_list = mongodb_handler.read_data()
        unique_key = 'article_links'

        existing_links = set()
        for document in existing_data_list:
            existing_links.update(document.get(unique_key, []))

        insertion_data = []
        for record in records:
            if record.get(unique_key) not in existing_links:
                insertion_data.append(record)

        if insertion_data:
            mongodb_handler.insert_data(insertion_data)

        mongodb_handler.close_connection()
        logging.info(f"Loaded {len(insertion_data)} records into the database.")

    except Exception as ex:
        logging.error(ex)

