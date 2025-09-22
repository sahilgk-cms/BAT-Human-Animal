import re
import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from newspaper import Article, ArticleException
from googletrans import Translator
import asyncio
import os
import sys

parent_path = os.path.dirname(os.path.dirname(__file__))
root_path = os.path.dirname(parent_path)
sys.path.append(root_path)

from utils.db_loader import load_to_mongodb
from config import (
    GOOGLE_ALERTS_URLS,
    CONTENT_UNAVAILABLE_MESSAGE,
    DATE_UNAVAILABLE_MESSAGE,
    MAX_TRANSLATION_CHUNK_SIZE,
    MONGODB_SCRAPED_COLLECTION
)
from logging_config import get_logger

logger = get_logger(__name__)

headers = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "referer": "https://www.google.com/",
}


logger.info("Scraping from Google Alerts.\n\n\n")


def scrape_google_alerts():
    """
    Sends a get request to the Google Alerts URL and parses the HTML obtained.
    Returns a BeautifulSoup object.
    """

    alert_url_and_soups = {}
    for url in GOOGLE_ALERTS_URLS:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, features="xml")
            alert_url_and_soups[url] = soup

        except Exception as ex:
            logger.error(ex)

    return alert_url_and_soups


def get_article_details(alert_url_and_soups):
    """
    Returns a list of tuples with details of each entry in the Google Alerts feeds.
    :param soup: BeautifulSoup object
    """
    tag_pattern = "<.*?>"
    link_pattern = "url=(.*?)&"  # example- https://www.google.com/url?rct=j&sa=t&url=https://nation.africa/kenya/health/vaccines-shortage-what-is-at-stake--4629622&ct=ga&cd=CAIyHDljNzBlNzk1ZWI1YWQ4YWQ6Y29tOmVuOlVTOkw&usg=AOvVaw0Ss72Z-AcXfAH5jXsqzJvs
    date_pattern = (
        r"(\d{4})-(\d{2})-(\d{2})T\d{2}:\d{2}:\d{2}Z"  # example- 2024-05-20T05:42:44Z
    )
    content_pattern = '<content type="html">(.*)</content>'  # example- <content type="html">Among <b>viruses</b>, in Argentina porcine <b>rotaviruses</b> (PoRV) groups A, B and C and transmissible gastroenteritis <b>coronavirus</b> (TGEV) has been described&nbsp;...</content>
    miscellaneous_pattern_1 = "&nbsp;..."
    miscellaneous_pattern_2 = "&lt;/?b&gt;"
    miscellaneous_pattern_3 = r"Our DivisionsCopyright © \d{4}-\d{2} DB Corp ltd., All Rights ReservedThis website follows the DNPA Code of Ethics."
    miscellaneous_pattern_4 = r"&\s?amp"
    miscellaneous_pattern_5 = "Advertisement"
    miscellaneous_patterns = [
        miscellaneous_pattern_1,
        miscellaneous_pattern_2,
        miscellaneous_pattern_3,
        miscellaneous_pattern_4,
        miscellaneous_pattern_5,
    ]

    entry_details = []
    links_not_found = []
    dates_not_found = []
    try:
        for alert_url, soup in alert_url_and_soups.items():
            entries = soup.find_all("entry")
            for entry in entries:
                raw_link = entry.find("link")
                raw_date = entry.find("published")
                raw_content = entry.find("content")
                try:
                    x = re.search(link_pattern, str(raw_link))
                    if x:
                        link = x.group(1)
                    else:
                        links_not_found.append(str(raw_link))
                        continue
                except:
                    links_not_found.append(str(raw_link))
                    continue

                try:
                    x = re.search(date_pattern, str(raw_date))
                    if x:
                        date = x.group(3) + "/" + x.group(2) + "/" + x.group(1)
                    else:
                        date = DATE_UNAVAILABLE_MESSAGE
                        dates_not_found.append(str(raw_date))
                except:
                    date = DATE_UNAVAILABLE_MESSAGE
                    dates_not_found.append(str(raw_date))

                try:
                    x = re.search(content_pattern, str(raw_content))
                    content = x.group(1)
                    content = re.sub(tag_pattern, "", content)
                    for pattern in miscellaneous_patterns:
                        if pattern == miscellaneous_pattern_3:
                            content = CONTENT_UNAVAILABLE_MESSAGE
                            break
                        else:
                            content = re.sub(pattern, "", content)
                except:
                    content = CONTENT_UNAVAILABLE_MESSAGE

                entry_details.append((alert_url, link, date, content))

    except Exception as e:
        logger.error(e)

    if len(links_not_found) > 0:
        link_not_found_message = (
            f"\n{len(links_not_found)} links not found: \n{links_not_found}"
        )
        logger.info(link_not_found_message)

    if len(dates_not_found) > 0:
        date_not_found_message = (
            f"\n{len(dates_not_found)} dates not found: \n{dates_not_found}"
        )
        logger.info(date_not_found_message)

    return entry_details


def create_chunks(corpus):
    chunks = [
        corpus[i : i + MAX_TRANSLATION_CHUNK_SIZE]
        for i in range(0, len(corpus), MAX_TRANSLATION_CHUNK_SIZE)
    ]
    return chunks


async def detect_languages(text):
    translator = Translator()
    response = await translator.detect(text)
    return response.lang if response is not None else None


async def translate_text(text, detected_language):
    translator = Translator()
    response = await translator.translate(text, src=detected_language, dest="en")
    return response.text if response is not None else None


def check_translation(text):
    global type_errors, value_errors, attribute_errors
    if text is not None and text != "":
        try:
            detected_language = asyncio.run(detect_languages(text))
            if detected_language == "en":
                return text

            if detected_language is not None:
                translated_text = asyncio.run(translate_text(text, detected_language))
                if translated_text is not None:
                    return translated_text
                else:
                    logger.info("Translation failed for text: ", text)
                    return CONTENT_UNAVAILABLE_MESSAGE
            else:
                return text

        except TypeError as e:
            error = "TypeError in translate_text(): " + str(e)
            type_errors.append(error)
            return CONTENT_UNAVAILABLE_MESSAGE

        except ValueError as e:
            error = "ValueError in translate_text(): " + str(e)
            value_errors.append(error)
            return CONTENT_UNAVAILABLE_MESSAGE

        except AttributeError as e:
            error = "AttributeError in translate_text(): " + str(e)
            attribute_errors.append(error)
            return CONTENT_UNAVAILABLE_MESSAGE

        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return CONTENT_UNAVAILABLE_MESSAGE

    else:
        return CONTENT_UNAVAILABLE_MESSAGE


def process_text(text):
    spaces_pattern = "\n|  |\t|\r|\f"
    text = re.sub(spaces_pattern, "", text)
    text = text.strip()

    try:
        if len(text) > MAX_TRANSLATION_CHUNK_SIZE:
            text_chunks = create_chunks(text)

            concatenated_text = ""
            for chunk in text_chunks:
                translated_text = check_translation(chunk)
                if translated_text != CONTENT_UNAVAILABLE_MESSAGE:
                    concatenated_text += translated_text

            if len(concatenated_text) > 0:
                return concatenated_text
            else:
                return CONTENT_UNAVAILABLE_MESSAGE

        else:
            translated_text = check_translation(text)
            if translated_text != CONTENT_UNAVAILABLE_MESSAGE:
                return translated_text
            else:
                return CONTENT_UNAVAILABLE_MESSAGE

    except Exception as e:
        error_message = "Error processing text: ", e
        logger.error(error_message)
        return CONTENT_UNAVAILABLE_MESSAGE


def get_data(entry_details):
    """
    Obtains all articles from the URLs and returns a DataFrame of the cleaned dates and article texts.
    :param article_links: List of links to the individual articles
    """
    global type_errors, value_errors, attribute_errors
    type_errors = []
    value_errors = []
    attribute_errors = []

    articles = []
    titles = []
    dates = []
    links_with_data = []
    alert_urls = []

    today = datetime.today()

    default_date = today.strftime("%d/%m/%Y")

    forbidden_urls = []
    for entry in entry_details:
        alert_url = entry[0]
        link = entry[1]
        date = entry[2]
        content = entry[3]

        try:
            article = Article(link)
            article.download()
            article.parse()

            text = process_text(article.text)
            if (
                text == CONTENT_UNAVAILABLE_MESSAGE
                and content != CONTENT_UNAVAILABLE_MESSAGE
            ):
                text = process_text(content)

            title = article.title
            title = process_text(title)

            if date != "No date available":
                try:
                    date = article.publish_date.strftime("%d/%m/%Y")
                except:
                    date = default_date

            titles.append(title)
            articles.append(text)
            dates.append(date)
            links_with_data.append(link)
            alert_urls.append(alert_url)

        except ArticleException:
            forbidden_urls.append(link)

        except Exception as e:
            logger.error(str(e))

    if len(forbidden_urls) > 0:
        log_message = f"{len(forbidden_urls)} links forbidden: \n{forbidden_urls}\n\n\n"
        logger.info(log_message)

    if len(type_errors) > 0:
        log_message = (
            f"{len(type_errors)} type errors in translation: \n{type_errors}\n\n\n"
        )
        logger.info(log_message)

    if len(value_errors) > 0:
        log_message = (
            f"{len(value_errors)} value errors in translation: \n{value_errors}\n\n\n"
        )
        logger.info(log_message)

    if len(attribute_errors) > 0:
        log_message = f"{len(attribute_errors)} attribute errors in translation: \n{attribute_errors}\n\n\n"
        logger.info(log_message)

    dataframe = pd.DataFrame(
        {
            "date": dates,
            "title": titles,
            "text": articles,
            "article_links": links_with_data,
            "scraped_date": today,
            "scraped_from": "Google Alerts",
            "alert_url": alert_urls,
        }
    )

    logger.info("Completed scraping from Google Alerts.")

    return dataframe


if __name__ == "__main__":
    entry_details = scrape_google_alerts()
    links = get_article_details(entry_details)
    article_dataframe = get_data(links)
    load_to_mongodb(caller="Scrapers", dataframe=article_dataframe)
