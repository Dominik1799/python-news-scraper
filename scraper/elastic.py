import os
import sys
import json
from telnetlib import EL
import logging
from attr import field
import google_news.settings as settings
from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection


class Elastic(object):
    es_connection = None

    elastic_index_name = settings.ELASTIC_INDEX_NAME
    elastic_index_config = settings.ELASTIC_INDEX_CONFIG

    @staticmethod
    def initialize():
        protocol = "https"
        host = settings.ES_HOST
        port = settings.ES_PORT
        username = settings.ES_USERNAME
        password = settings.ES_PASSWORD

        connection_string = "{protocol}://{username}:{password}@{host}:{port}/".format(
            protocol=protocol,
            username=username,
            password=password,
            host=host,
            port=port
        )
        Elastic.es_connection = Elasticsearch(hosts=connection_string, verify_certs=False, ssl_show_warn=False)
        # This triggers if elastic connection is not successfull
        if (not Elastic.es_connection.ping()):
            logging.error("Elastic connection unsuccessfull. Exiting")
            exit(1)

    @staticmethod
    def index_article(article_id, item):
        # make sure connection is set
        if Elastic.es_connection is None:
            print('Article with id {} wasn\'t indexed, because connection to Elasticsearch wasn\'t established.'.format(article_id))
            return False

        if not Elastic.es_connection.indices.exists(index=Elastic.elastic_index_name):
            # firstly load index configuration
            with open(os.getcwd() + '/' + Elastic.elastic_index_config) as articles_config_file:
                configuration = json.load(articles_config_file)

                # create index
                res = Elastic.es_connection.indices.create(index=Elastic.elastic_index_name, settings=configuration["settings"])
                
                # make sure index was created
                if not res['acknowledged']:
                    print('Index wasn\'t created')
                    print(res)
                    sys.exit()
                else:
                    print('Index successfully created.')

        # create dictionary from GoogleNewsItem, because GoogleNewsItem is not JSON serializable
        # ommit article_id, because it is not in elastic index as a field
        article_data = {field_name: field_value for field_name, field_value in item.items() if field_name != 'article_id'}

        response = Elastic.es_connection.index(
            index=Elastic.elastic_index_name,
            doc_type='_doc',
            id=article_id, # document id in Elasticsearch == article id in articles collection
            document=json.dumps(article_data)
        )

        # inform user about not indexed article
        if 'result' not in response:
            logging.error('FAIL TO INDEX ARTICLE: {} AND RESPONSE DOESN\'T HAVE result FIELD'.format(article_id))
            return False
        elif response['result'] != 'created' and response['result'] != 'updated':
            logging.error('FAIL TO INDEX ARTICLE: {}, RESPONSE RESULT: {}'.format(article_id, response['result']))
            return False
        return True