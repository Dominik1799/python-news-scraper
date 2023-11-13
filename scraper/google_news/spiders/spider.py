from os.path import dirname
import platform
import re
import subprocess
from database import Database
from elastic import Elastic
import os
import requests
import scrapy
from gnewsparser import GnewsParser
from google_news.items import GoogleNewsItem
from scrapy import Selector
import logging
from scrapy.exceptions import CloseSpider
from scrapy import signals
from pydispatch import dispatcher
import json
import google_news.settings as settings

CRIMES_FOLDER = './crimes/'

# run with command: scrapy crawl spider -o <outputfile.json>
# working directory: C:\Users\jakub\team_project\scraper\google_news\google_news

def get_text_content(html):
    final_html = ""

    try:
        # select only paragraphs and headings using xpath
        text_results = Selector(text=html).xpath('//p | //h1 | //h2 | //h3 | //h4 | //h5 | //h6').getall()
    except:
        return final_html

    # for each result (paragraph or heading tag) remove
    # all specifications - classes, ids etc.    
    for result in text_results:
        i = result.index(">")
 
        if "<p" in result:
            result = result[:2] + result[i:]
            tag_content = result[3:-4]

        elif "<h" in result:
            result = result[:3] + result[i:]
            tag_content = result[4:-5]

        # check if the body of current tag is empty
        # if it is, then ignore the tag
        if not tag_content.strip():
            continue

        result = str(result)
        final_html += result

    return final_html


class Spider(scrapy.Spider):
    name = "news_spider"

    __ERROR_MESSAGE = """
        Please provide arguments. Example:
        scrapy crawl {spider_name} -a crimes_file=FILE -a search_from=DATE -a search_to=DATE -a locale=LOCALE
    """


    def __load_crimes(self):
        ''' 
            open list_of_crimes_english and user specified file with list of crimes in other language english too
            create and return dictionary where key value is crime keyword from user specified file and value is corresponding english crime keyword 
        '''

        crimes_dict:dict = {}

        crime_f = open(self.crimes_file, "r", encoding="utf8")
        crime_f_en = open(self.crimes_file_en, "r", encoding="utf8")

        crime_lines:list[str] = [line.replace("\n", "") for line in crime_f.readlines()]
        crime_lines_en:list[str] = [line.replace("\n", "") for line in crime_f_en.readlines()]

        crimes_dict:dict = {crime_keyword: crime_keyword_en for crime_keyword, crime_keyword_en in zip(crime_lines, crime_lines_en)}

        crime_f_en.close()
        crime_f.close()

        return crimes_dict

    def process_locale(self, locale):
        region = locale
        language = locale

        if '-' in locale:
            region = locale.split('-')[1]
            language = locale.split('-')[0]

        return region, language


    def __check_proxies(self):
        with open(settings.ROTATING_PROXY_LIST_PATH, "r") as proxies:
            param = '-n' if platform.system().lower()=='windows' else '-c'
            # atleast 1 proxy should be alive, else dont even start scraping
            isProxyAlive = False
            for line in proxies:
                if line == "":
                    continue
                line = line.replace("http://", "").split(":")[0]
                code = subprocess.run(["ping", param, "1", line.rstrip()]).returncode
                if code == 0:
                    isProxyAlive = True
                logging.warning("Proxy " + line + "seems to be down.")
            
            if not isProxyAlive:
                raise CloseSpider("Not a single proxy is alive, do not even start scraping. Exiting...")
            logging.info("Proxies seem to be up and running, proceeding with scraping...")


    def __init__(self, crimes_file="testing_murder.txt", search_from="", search_to="", locale="", days_step=1,  **kwargs):
        super().__init__(**kwargs)
        if search_from == "" or search_to == "" or locale == "":
            logging.error(self.__ERROR_MESSAGE)
            exit(1)
        self.__check_proxies()
        self.crimes_file = CRIMES_FOLDER + crimes_file
        self.crimes_file_en = CRIMES_FOLDER + 'list_of_crimes_english.txt'
        self.search_from = search_from
        self.search_to = search_to
        self.locale = locale
        self.days_step = days_step
        message = "STARTING WITH ARGS: locale: {slocale}, crimes_file: {cfile}, days step: {sstep} ,search_from: {sfrom}, search_to: {sto}".format(
            slocale=locale,
            cfile=crimes_file,
            sstep=days_step,
            sfrom=search_from,
            sto=search_to
        )
        # set shutdown function
        dispatcher.connect(self.scrape_end, signals.spider_closed)
        logging.critical(message)
    


    def start_requests(self):
        loaded_crimes_dict = self.__load_crimes()

        # set up searching for each crime defined in crime_keywords
        for crime_keyword, crime_keyword_en in loaded_crimes_dict.items():
            print("processing crime: ", crime_keyword)
            gnews_parser = GnewsParser()
            gnews_parser.setup_search(crime_keyword, self.search_from, self.search_to, locale=self.locale, days_step=self.days_step)
            while True:
                new_url = gnews_parser.get_new_url()  # getting articles on daily basis
                
                if new_url is None:
                    break

                yield scrapy.Request(new_url,
                                    callback=self.parse_feed,
                                    cb_kwargs=dict(
                                        crime_keyword=crime_keyword,
                                        crime_keyword_en=crime_keyword_en,
                                        loaded_crimes_dict=loaded_crimes_dict
                                    )
                                )
                                         


    def parse_feed(self, response, crime_keyword, crime_keyword_en, loaded_crimes_dict):
        gnews_parser = GnewsParser()
        res = gnews_parser.get_parsed_feed(response.body)
        for article in res:
            # retrieve needed data from Google RSS
            link = article['link']
            title = article['title']
            published = article['published']

            # make get request on article link
            yield scrapy.Request(link,
                                    callback=self.extract_url,
                                    cb_kwargs=dict(
                                        published=published,
                                        title=title,
                                        crime_keyword=crime_keyword,
                                        crime_keyword_en=crime_keyword_en,
                                        loaded_crimes_dict=loaded_crimes_dict
                                    ),
                                    meta={
                                             'dont_retry': True
                                    },
                                )
    def extract_url(self, response, published, title, crime_keyword, crime_keyword_en, loaded_crimes_dict):
        url = response.xpath("string(//a/@href)").get()
        if not response.status == 200:
            return
        else: 
            yield scrapy.Request(url,
                                    callback=self.parse,
                                    cb_kwargs=dict(
                                        published=published,
                                        title=title,
                                        crime_keyword=crime_keyword,
                                        crime_keyword_en=crime_keyword_en,
                                        loaded_crimes_dict=loaded_crimes_dict
                                    ),
                                    meta={
                                             'dont_retry': True
                                    },
                                )




    def parse(self, response, published, title, crime_keyword, crime_keyword_en, loaded_crimes_dict):
        accepted_http_status = [200, 301, 302, 303]
        item = GoogleNewsItem()  # this item will be writin in output file, when it is yield
        Database.initialize()    # connect to mongo database
        Elastic.initialize()     # connect to elasticsearch
        # parse only responses with status code 200
        if response.status in accepted_http_status:
            try:
                # retrieve body tag with data
                body_tag = response.css('body').get()
                # retrieve only text tags from html body (paragraphs and headings)
                text_content = get_text_content(body_tag)
                # lower case text context for crimes keywords searching
                text_content_lower = text_content.lower()
                # remove any links. This way no matches are found in URLs
                # text_content_lower = re.sub(r'^https?:\/\/.*[\r\n]*', "", flags=re.MULTILINE)

                # all crime keywords, which are in article's text will be in this list
                # crime keywords will be in english for better consistency, when searching an article from multiple countries based on crime keyword
                crimes_in_article = [crime_keyword_en]

                # iterate through each keyword and check if it is in article
                for keyword_crime, keyword_crime_en in loaded_crimes_dict.items():
                    # arleady contains this crime
                    if keyword_crime == crime_keyword:
                        continue
                    
                    # lower case keyword_crime before adding spaces
                    # to find out if keyword_crime is single word add blank space before and after keyword_crime
                    # this makes sure, that only whole words are matched and not substrings of words. example: 'word' in 'swordsmith' == True, but ' word ' in 'swordsmith' == False
                    keyword_crime_spaces = ' ' + keyword_crime.lower() + ' '

                    if keyword_crime_spaces in text_content_lower:
                        logging.info('UPDATED CRIME {} FOR LINK {}'.format(keyword_crime, response.url))
                        # add english crime keyword to list, which will be stored in keywords field in MongoDB
                        crimes_in_article.append(keyword_crime_en)

                # writes data into item, which will be yield into MongoDB pipeline
                item['title'] = title,
                item['published'] = published,
                item['link'] = response.url,
                item['html'] = text_content
                item['keywords'] = crimes_in_article

                # '-' in locale makes sure, there is language and region, otherwise only language is passed https://developers.google.com/search/docs/advanced/crawling/localized-versions#regional-variations-table
                if '-' in self.locale:
                    region, language = self.process_locale(self.locale)
                    item['region'] = region
                    item['language'] = language
                else:
                    # possible languages https://developers.google.com/admin-sdk/directory/v1/languages
                    item['language'] = self.locale

                yield item

            except Exception:
                # if page doesn't contains body tag, program will execute this line of code
                pass

        # store respones with status code other than 200
        else:
            # insert to database or update crime keywords
            Database.update('errorlinks', response.url, crime_keyword)  


    def scrape_end(self, spider):
        spider_stats = spider.crawler.stats.get_stats()
        # final stats can be sent to stats service, someday :)
        final_stats = {
            "locale": self.locale,
            "scraping_date":  spider_stats["start_time"].strftime("%Y-%m-%d, %H:%M:%S"),
            "elapsed_time_seconds": spider_stats["elapsed_time_seconds"],
            "items_scraped_count": spider_stats["item_scraped_count"] if "item_scraped_count" in spider_stats else 0,
            "mongo_inserts": spider_stats["mongo_inserts"] if "mongo_inserts" in spider_stats else 0,
            "elastic_inserts": spider_stats["elastic_inserts"] if "elastic_inserts" in spider_stats else 0
        }
        if settings.SEND_METRICS == "true":
            requests.post(settings.DAILY_METRICS_ENDPOINT, json=final_stats)
        logging.critical("Spider ended. Stats:")
        logging.critical(json.dumps(spider_stats, indent=4, default=lambda o: f"<<non-serializable: {type(o).__qualname__}>>"))
