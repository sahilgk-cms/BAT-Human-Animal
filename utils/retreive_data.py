import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pymongo
import logging
from dotenv import load_dotenv
import os
import sys
current_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(current_path))
sys.path.append(root_path)
from handlers.mongodb_handler import MongoDBHandler
from config import CONTENT_UNAVAILABLE_MESSAGE

load_dotenv()
scraped_collection_name = os.getenv('MONGODB_SCRAPED_COLLECTION')
processed_collection_name = os.getenv('MONGODB_PROCESSED_COLLECTION')

def retreive(caller):
    '''
    Accesses the MongoDB database and returns a list of existing documents.
    '''
    
    if caller == 'RelevanceFiltering':
        collection = scraped_collection_name
    elif caller in ['EntityRecognition', 'Summarization', 'SentimentScoring', 'DocumentClustering', 'DiseaseMapping', 'LocationMapping']:
        collection = processed_collection_name
    else:
        error_message = 'Invalid caller: ' + caller
        logging.error(error_message)

    document_list = []
    try:
        mongodb_handler = MongoDBHandler(collection)
        
        latest_date_doc = mongodb_handler.read_data(query={}, sort=[('scraped_date', pymongo.DESCENDING)], limit=1)
        start_date = latest_date_doc[0]['scraped_date']
        start_date = datetime.strptime("01/01/2023", "%d/%m/%Y")        
        end_date = datetime.today()
        
        if caller == 'DocumentClustering':
            start_date = datetime.now() - relativedelta(days=7)

        query = {
            'scraped_date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }

        documents = mongodb_handler.read_data(query)
        document_list = list(documents)
        mongodb_handler.close_connection()

        texts = []
        for doc in document_list:
            if doc['text'] == CONTENT_UNAVAILABLE_MESSAGE and doc['title'] != CONTENT_UNAVAILABLE_MESSAGE:
                texts.append(doc['title'])
            else:
                texts.append(doc['text'])

        if caller in ['RelevanceFiltering', 'EntityRecognition', 'DocumentClustering']:
            df = pd.DataFrame(document_list)
            df['text'] = texts
            return df

    except Exception as ex:
        logging.error(ex)
    
    return document_list
