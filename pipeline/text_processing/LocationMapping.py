import json
from datetime import datetime
import logging
import numpy as np
import pandas as pd
import subprocess
import os
import sys

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
from handlers.mongodb_handler import MongoDBHandler
from utils.retreive_data import retreive
from config import MONGODB_PROCESSED_COLLECTION
from logging_config import get_logger


mongodbhandler = MongoDBHandler(MONGODB_PROCESSED_COLLECTION)

logger = get_logger(__name__)


with open(os.path.join(root_path, 'locations.json'), 'r') as f:
    zones_data = json.load(f)

state_to_districts = {}
district_to_blocks = {}
block_to_districts = {}

ambiguous_blocks_and_districts = [
    # districts
    'Bid', 'Krishna',

    # blocks
    'Amla', 'Anand', 'Ani', 'Begun', 'Bind', 'Burden', 'Chand'
                                                       'Jama', 'Industrial', 'Khanna', 'Lanka', 'Man', 'Maker', 'Motu'
                                                                                                                'Nagar',
    'Para', 'Punch', 'Renuka', 'Ron', 'Sagar', 'Sahara', 'Sakshi'
]

for zone in zones_data:
    for state in zone['states']:
        state_name = state['name']
        state_to_districts[state_name] = []
        for district in state['districtList']:
            district_name = district['name']
            state_to_districts[state_name].append(district_name)
            district_to_blocks[district_name] = district['blockList']
            for block in district['blockList']:
                block_to_districts[block] = (district_name, state_name)


def match_locations(words):
    matched_states = set()
    matched_districts = set()
    matched_blocks = set()

    for block in block_to_districts:
        for word in words:
            if block.lower() == word.lower():
                matched_blocks.add(block)
                matched_districts.add(block_to_districts[block][0])
                matched_states.add(block_to_districts[block][1])
                break

    for district, blocks in district_to_blocks.items():
        for word in words:
            if district.lower() == word.lower():
                matched_districts.add(district)
                matched_states.add(block_to_districts[blocks[0]][1])
                break

    for state, _ in state_to_districts.items():
        for word in words:
            if state.lower() == word.lower():
                matched_states.add(state)
                break

    matched = True if len(matched_states) > 0 else False

    return matched_blocks, matched_districts, matched_states, matched


def update_document_with_matches(doc: dict):
    """
    Updates doc based on matched location
    Arguments:
        doc
    Returns:
        updated doc with locations - states, districts, blocks is added to MongoDB
    """
    # Skip if already processed (contains any of these keys)
    if any(k in doc for k in ["states", "districts", "blocks"]):
        return  # skip this document
    mongodbhandler.insert_data([doc])

    title_words = doc['title'].lower().split()
    text_words = doc['text'].lower().split()

    matched_blocks, matched_districts, matched_states, matched = match_locations(title_words)
    if not matched:
        matched_blocks, matched_districts, matched_states, matched = match_locations(text_words)
    elif matched_states:
        for state in matched_states:
            for district in state_to_districts[state]:
                if district.lower() in text_words:
                    matched_districts.add(district)
                    for block in district_to_blocks[district]:
                        if block.lower() in text_words:
                            matched_blocks.add(block)

    update_fields = {}
    if matched_states:
        update_fields['states'] = list(matched_states)
    if matched_districts:
        update_fields['districts'] = list(matched_districts)
    if matched_blocks:
        update_fields['blocks'] = list(matched_blocks)
    # logging.info(update_fields)

    if update_fields:
        mongodbhandler.update_data({'_id': doc['_id']}, update_fields)



if __name__ == "__main__":
    processed = 0
    documents = retreive('LocationMapping')

    for idx, doc in enumerate(documents):
        try:
            if idx%10 == 0:
               logger.info(f"Processing document {idx}/{len(documents)}")
            update_document_with_matches(doc)
            processed += 1
        except Exception as ex:
            logger.error(ex)
            continue

    logger.info(f"Processed {processed} documents")