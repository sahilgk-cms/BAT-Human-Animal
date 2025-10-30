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

DISTRICT_MAPPING_EXCEL_PATH = os.path.join(current_file_path, "Updated_District_Mapping.xlsx")

CLASSIFICATION_MODEL = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"


CONFIDENCE_THRESHOLD = 0.75

GOOGLE_ALERTS_URLS = [
    # ASSAM ELEPHANT
    "https://www.google.com/alerts/feeds/09515345323936615134/6006832369043609958",

    # Human Elephant conflict / killed
    "https://www.google.com/alerts/feeds/09515345323936615134/17627656450777929599",

    # Kerala Madhya Pradesh Human Elephant Conflict
    "https://www.google.com/alerts/feeds/09515345323936615134/3726296060896987787",
    
    # Man Elephant conflict
    "https://www.google.com/alerts/feeds/09515345323936615134/4931230651768095945",

    # elephant attack
    "https://www.google.com/alerts/feeds/09515345323936615134/7644789520755648298",

    # elephant killed
    "https://www.google.com/alerts/feeds/09515345323936615134/7644789520755649997",

    # elephant death
    "https://www.google.com/alerts/feeds/09515345323936615134/1826218283448115891"

    # elephant electrocuted
    "https://www.google.com/alerts/feeds/09515345323936615134/1826218283448115530",

    # elephant trampled
    "https://www.google.com/alerts/feeds/09515345323936615134/7251229532208347210",

    # elephant crop raid
    "https://www.google.com/alerts/feeds/09515345323936615134/1263561576838186465",

    # elephant entered village
    "https://www.google.com/alerts/feeds/09515345323936615134/14563176845556140556",

    # elephant herd damaged
    "https://www.google.com/alerts/feeds/09515345323936615134/14563176845556138726",

    # elephant corridor blocked
    "https://www.google.com/alerts/feeds/09515345323936615134/10872408727649526976",

    # elephant rescue
    "https://www.google.com/alerts/feeds/09515345323936615134/17191226051954354288",

    # elephant translocation
    "https://www.google.com/alerts/feeds/09515345323936615134/17191226051954353767",

    # elephant killed by train
    "https://www.google.com/alerts/feeds/09515345323936615134/11610249039944088510",

    # elephant poaching
    "https://www.google.com/alerts/feeds/09515345323936615134/1595351409908091737",

    # elephant accident
    "https://www.google.com/alerts/feeds/09515345323936615134/4425273195027443912",

    # elephant mitigation
    "https://www.google.com/alerts/feeds/09515345323936615134/4425273195027444701",

    # human death elephant
    "https://www.google.com/alerts/feeds/09515345323936615134/9415393225357504402",

    # man killed by elephant
    "https://www.google.com/alerts/feeds/09515345323936615134/4425273195027447560"
]

QUERY = ["Elephant",
         "Human Elephant conflict / killed",
         "elephant attack",
         "elephant killed",
         "elephant death",
         "elephant electrocuted",
         "elephant trampled",
         "elephant crop raid",
         "elephant entered village",
         "elephant herd damaged",
         "elephant corridor blocked",
         "elephant rescue",
         "elephant translocation",
         "elephant killed by train",
         "elephant poaching",
         "elephant accident",
         "elephant mitigation",
         "human death elephant",
         "man killed by elephant"]

LOCATION = ["Assam", "Kerala", "Madhya Pradesh", "North East India", "Tamil Nadu"]

GOOGLE_SEARCH_API_URL = "https://www.googleapis.com/customsearch/v1"

LOGS_DIRECTORY = os.path.join(current_file_path, "logs")



