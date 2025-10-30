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
from utils.map_district_cordinates import coord_map
from config import MONGODB_PROCESSED_COLLECTION
from logging_config import get_logger


mongodbhandler = MongoDBHandler(MONGODB_PROCESSED_COLLECTION)

logger = get_logger(__name__)


def map_cordinates(doc: dict):
    """
       Updates cordinates based on matched location
       Arguments:
           doc
       Returns:
           updated doc with coordinates added to MongoDB
    """
    if "coordinates" in doc:
        return

    districts = doc.get("districts", [])
    if not districts:
        return

    matches_coords = []
    for district in districts:
        district_lower = district.lower()
        coords = coord_map.get(district_lower)

        if not coords:
            continue

        matches_coords.append(
            {
                "district": district,
                "latitude": coords["latitude"],
                "longitude": coords["longitude"]
            }
        )

    if matches_coords:
        update_fields = {"coordinates": matches_coords}
        mongodbhandler.update_data({"_id": doc["_id"]}, update_fields)




if __name__ == "__main__":
    processed = 0
    documents = retreive('CoordinatesMapping')

    for idx, doc in enumerate(documents):
        try:
            if idx%10 == 0:
               logger.info(f"Processing document {idx}/{len(documents)}")
            map_cordinates(doc)
            processed += 1
        except Exception as ex:
            logger.error(ex)
            continue

    logger.info(f"Processed {processed} documents")
