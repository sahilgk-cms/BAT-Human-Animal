import os
from dotenv import load_dotenv

load_dotenv()

current_file_path = os.getcwd()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")
MONGODB_SCRAPED_COLLECTION = os.getenv("MONGODB_SCRAPED_COLLECTION")
MONGODB_PROCESSED_COLLECTION = os.getenv("MONGODB_PROCESSED_COLLECTION")
MONGODB_UNIQUE_KEY = os.getenv('MONGODB_UNIQUE_KEY')

CONTENT_UNAVAILABLE_MESSAGE = "Content unavailable"
DATE_UNAVAILABLE_MESSAGE = "Date unavailable"
MAX_TRANSLATION_CHUNK_SIZE = 4000

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")


CLASSIFICATION_MODEL = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"


CONFIDENCE_THRESHOLD = 0.75

GOOGLE_ALERTS_URLS = [
    # ASSAM ELEPHANT
    "https://www.google.com/alerts/feeds/09515345323936615134/6006832369043609958",

    # Human Elephant conflict / killed
    "https://www.google.com/alerts/feeds/09515345323936615134/17627656450777929599",

    # Kerala Madhya Pradesh Human Elephant Conflict
    "https://www.google.com/alerts/feeds/09515345323936615134/3726296060896987787"
]

QUERY = ["Elephant", "Human Elephant conflict / killed"]
LOCATION = ["Assam", "Kerala", "Madhya Pradesh"]

GOOGLE_SEARCH_API_URL = "https://www.googleapis.com/customsearch/v1"

LOGS_DIRECTORY = os.path.join(current_file_path, "logs")



