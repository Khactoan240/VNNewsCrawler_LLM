import requests
import sys
from pathlib import Path

from bs4 import BeautifulSoup

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from logger import log
from crawler.base_crawler import BaseCrawler
from utils.bs4_utils import get_text_from_tag


class VNExpressCrawler(BaseCrawler):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.logger = log.get_logger(name=__name__)

        self.article_type_dict = {
            0: "thoi-su",
            1: "goc-nhin",
            2: "the-gioi",
            3: "kinh-doanh",
            4: "bat-dong-san",
            5: "khoa-hoc",
            6: "giai-tri",
            7: "the-thao",
            8: "phap-luat",
            9: "giao-duc",
            10: "suc-khoe",
            11: "doi-song",
            12: "du-lich",
            13: "so-hoa",
            14: "oto-xe-may",
            15: "y-kien",
            16: "tam-su",
            17: "thu-gian",

        } 

    def extract_content(self, url: str) -> tuple:
        """
        Extract title, description and paragraphs from url
        @param url (str): url to crawl
        @return title (str)
        @return description (generator)
        @return paragraphs (generator)
        """
        content = requests.get(url).content
        soup = BeautifulSoup(content, "html.parser")

        title = soup.find("h1", class_="title-detail") 
        if title == None:
            return None, None, None
        title = title.text

        # some sport news have location-stamp child tag inside description tag
        description = (get_text_from_tag(p) for p in soup.find("p", class_="description").contents)
        paragraphs = (get_text_from_tag(p) for p in soup.find_all("p", class_="Normal"))

        return title, description, paragraphs

    def write_content(self, url: str, output_fpath: str) -> bool:
        """
        From url, extract title, description and paragraphs then write in output_fpath
        @param url (str): url to crawl
        @param output_fpath (str): file path to save crawled result
        @return (bool): True if crawl successfully and otherwise
        """
        title, description, paragraphs = self.extract_content(url)
                    
        if title == None:
            return False

        with open(output_fpath, "w", encoding="utf-8") as file:
            file.write(title + "\n")
            for p in description:
                file.write(p + "\n")
            for p in paragraphs:                     
                file.write(p + "\n")

        return True

    def get_urls_of_type_thread(self, article_type, page_number):
        """" Get urls of articles in a specific type in a page"""
        page_url = f"https://vnexpress.net/{article_type}-p{page_number}"
        content = requests.get(page_url).content
        soup = BeautifulSoup(content, "html.parser")
        titles = soup.find_all(class_="title-news")

        if (len(titles) == 0):
            self.logger.info(f"Couldn't find any news in {page_url} \nMaybe you sent too many requests, try using less workers")

        articles_urls = list()

        for title in titles:
            link = title.find_all("a")[0]
            articles_urls.append(link.get("href"))
    
        return articles_urls
