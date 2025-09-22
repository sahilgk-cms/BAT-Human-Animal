import serpapi
import requests
import pandas as pd
from urllib.parse import urlparse
import re
from datetime import datetime
from typing import List, Union
import pandas as pd
from newspaper import Article
import os
import sys

parent_path = os.path.dirname(os.path.dirname(__file__))
root_path = os.path.dirname(parent_path)
sys.path.append(root_path)

from utils.format_date import convert_iso_date_into_ddmmyyyy
from utils.db_loader import load_to_mongodb
from config import SERP_API_KEY, QUERY, LOCATION
from logging_config import get_logger


logger = get_logger(__name__)
logger.info("Scraping from SerpAPI.\n\n\n")


def search_articles_on_web() -> List[dict]:
    '''
    Searches articles on Google News using SerpAPI
    Args:
        None
    Returns:
         list of dictionary containing news results
    '''

    queries = QUERY
    locations = LOCATION
    # Using SerpAPI to get links

    for query in queries:
        for loc in locations:
            print(f"Searching for {query} in {loc}")
            url = f"https://serpapi.com/search.json?engine=google_news&q={query}+in+{loc}&gl=in&hl=en&api_key={SERP_API_KEY}"
            results = requests.get(url)

            results = results.json()
            news_results = results["news_results"]

    return news_results


def scrape_articles(news_results: List[dict]) -> pd.DataFrame:
    '''
    Sscrapes articles from the given news results
    Args:
        news results
    Returns:
         dataframe containing scraped articles
    '''
    # Using Newspaper 3K to get text
    all_articles = []
    for i in range(0, len(news_results)):
        try:
            a = Article(news_results[i]["link"])
            a.download()
            a.parse()
            text = a.text
            date = convert_iso_date_into_ddmmyyyy(news_results[i]["date"])
            article = {
                "date": date,
                "title": news_results[i]["title"],
                "text": text,
                "scraped_from": news_results[i]["source"]["name"],
                "article_links": news_results[i]["link"],
            }
            all_articles.append(article)
        except Exception as e:
            logger.error(f"Error in article: {i}: {e}")
            continue

    df = pd.DataFrame(all_articles)
    df["scraped_date"] = [datetime.now() for i in range(len(df))]
    return df


if __name__ == "__main__":
    news_results = search_articles_on_web()
    if len(news_results) != 0:
        articles_dataframe = scrape_articles(news_results)
        load_to_mongodb(caller = "Scrapers", dataframe=articles_dataframe)
