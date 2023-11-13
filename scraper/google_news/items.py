# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GoogleNewsItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    published = scrapy.Field()
    link = scrapy.Field()
    html = scrapy.Field()
    region = scrapy.Field()
    language = scrapy.Field()
    keywords = scrapy.Field()
    article_id = scrapy.Field()
                    
    def __str__(self):
        return self.title
