from scrapy.crawler import CrawlerProcess
from google_news.spiders.spider import Spider
from scrapy.utils.project import get_project_settings
import json


process = CrawlerProcess(get_project_settings())

process.crawl(Spider)
process.start()