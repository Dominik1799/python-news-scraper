# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from database import Database
from elastic import Elastic
from scrapy import Selector

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class MongoPipeline(object):
    def __init__(self):
        Database.initialize()

    def process_item(self, item, spider):
        title = item['title'][0]
        published = item['published'][0]
        link = item['link'][0]
        html = item['html']
        region = item['region'] if 'region' in item else ""
        language = item['language']
        keywords = item['keywords']

        field_list = ['title', 'published', 'link', 'region', 'language', 'keywords', 'html']
        to_insert = {}

        # creates dictionary from item values
        for field in field_list:
            to_insert[field] = eval(field)
        
        # inserts into collection if document doesnt exist
        article_id = Database.insert("articles", to_insert)
        if article_id is not None:
            spider.crawler.stats.inc_value("mongo_inserts")

        item['article_id'] = article_id

        return item

class ElasticsearchPipeline:
    def __init__(self):
        Elastic.initialize()

    def process_item(self, item, spider):
        article_id = item['article_id']
        list_of_plain_texts = Selector(text=item['html']).xpath('//text()').getall()
        item['html'] = ' '.join(list_of_plain_texts)
        
        if Elastic.index_article(article_id, item):
            spider.crawler.stats.inc_value("elastic_inserts")
        return item