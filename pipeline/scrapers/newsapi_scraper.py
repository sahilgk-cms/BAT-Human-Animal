from newsapi import NewsApiClient
from datetime import datetime, timedelta
from newspaper import Article
import pandas as pd
from time import sleep
import os
import sys
from typing import List

parent_path = os.path.dirname(os.path.dirname(__file__))
root_path = os.path.dirname(parent_path)
sys.path.append(root_path)

from utils.db_loader import load_to_mongodb
from config import NEWS_API_KEY, QUERY, LOCATION
from utils.format_date import convert_iso_date_into_ddmmyyyy
from logging_config import get_logger

logger = get_logger(__name__)

logger.info("Scraping from NewsAPI.\n\n\n")





def get_links_from_newsapi() -> List[dict]:
    '''
    This function returns llist of articles links from NewsAPI
    Args:
        None
    Returns:
        list of articles containing source, url, title, publishedAt
    '''
    news_api = NewsApiClient(api_key = NEWS_API_KEY)
    all_articles = []
    seen_urls = set()

    queries = QUERY
    location = LOCATION

    current_date = datetime.today().date().isoformat()
    from_date = (datetime.today() - timedelta(days = 30)).date().isoformat()

    for query in queries:
        for loc in location:
            logger.info(f"Scraping articles with query:{query} and location: {loc}")
            final_query = query  + f"AND {loc}"

            try:
                articles = news_api.get_everything(
                q = final_query,
                sources =  "the-times-of-india",
                from_param = from_date,
                to = current_date,
                sort_by = "relevancy"
                )
            except Exception as e:
                logger.error(f" Failed to get articles for query '{query}': {e}")
                continue

            for article in articles.get("articles", []):
                if article["url"] not in seen_urls:
                    all_articles.append(article)
                    seen_urls.add(article["url"])

            sleep(2)

    return all_articles


def scrape_articles_from_newsapi(all_articles: List[dict]) -> pd.DataFrame:
    '''
    This function scrapes articles from links and returns dataframe
    Args:
        list of articles 
    Returns:
        dataframe containing articles text, source, date, title
    '''

    text_list = []
    title_list = []
    links_list = []
    sources_list = []
    dates_list = []

    logger.info("Extracting text from all articles.....")


    for i in range(0, len(all_articles)):
        a = Article(all_articles[i]["url"])
        a.download()
        a.parse()
        text_list.append(a.text)

        sources_list.append(all_articles[i]["source"]["name"])
        links_list.append(all_articles[i]["url"])
        title_list.append(all_articles[i]["title"])
        dates_list.append(convert_iso_date_into_ddmmyyyy(all_articles[i]["publishedAt"]))

    scraped_date = [datetime.now() for i in range(0, len(title_list))]

    df = pd.DataFrame({"date": dates_list, "title": title_list, "text": text_list, "article_links": links_list,
                        "scraped_date": scraped_date, "scraped_from": sources_list})
    return df


if __name__ == "__main__":
    links = get_links_from_newsapi()
    if len(links) != 0:
        article_dataframe =scrape_articles_from_newsapi(links)
        load_to_mongodb(caller="Scrapers", dataframe=article_dataframe)