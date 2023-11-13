import os
import sys
import json
import pymongo
import logging
import google_news.settings as settings

class Database(object):
    DATABASE = None

    @staticmethod
    def initialize():
        connection = pymongo.MongoClient(settings.MONGODB_URI)
        Database.DATABASE = connection[settings.MONGODB_DB]
        articles = Database.DATABASE[settings.MONGODB_ARTICLES]

        articles.create_index('link', unique=True)

    @staticmethod
    def insert(collection, document):
        if Database.DATABASE is None:
            logging.error('Unable to add document to {} collection, because ther is no connection to MongoDB.'.format(collection))
            return None

        article_id = Database.DATABASE[collection].insert(document)

        return article_id

    @staticmethod
    def update(collection, link, to_update):
        if Database.DATABASE is None:
            logging.error('Unable to update collection {}, because there is not connection to MongoDB'.format(collection))
            return None

        Database.DATABASE[collection].update_one({'link': link}, 
                                                 {'$addToSet': {'keywords': to_update}}, upsert=True)