import os
from dotenv import load_dotenv
import urllib3



# *****************************
# SCRAPY Config
# *****************************
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


BOT_NAME = 'google_news'
COOKIES_ENABLED = False
DOWNLOAD_DELAY = 1
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620
}
ROTATING_PROXY_PAGE_RETRY_TIMES = 5
ROTATING_PROXY_LIST_PATH = os.environ.get("PROXY_LIST") or "../development/proxy_list.txt"


SPIDER_MODULES = ['google_news.spiders']
NEWSPIDER_MODULE = 'google_news.spiders'

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "WARNING"

SEND_METRICS = os.environ.get("SEND_METRICS") or "false"
DAILY_METRICS_ENDPOINT = os.environ.get("DAILY_METRICS_ENDPOINT") or "localhost"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16
DOWNLOAD_TIMEOUT = 20

# If set to True, in the end, scraper will try to contact stats service and update daily scraping stats
POST_STATS = os.environ.get("POST_STATS") or "False"
STATS_SERVICE_URL = os.environ.get("STATS_SERVICE_URL") or "stats_service:6000"


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"

# what means integer in ITEM_PIPELINES: https://docs.scrapy.org/en/latest/topics/item-pipeline.html#activating-an-item-pipeline-component
ITEM_PIPELINES = {
    'google_news.pipelines.MongoPipeline': 300,
    'google_news.pipelines.ElasticsearchPipeline': 500,
}


# *********************************
# OUR Config
# *********************************
# db server and port (local for now)
MONGODB_SERVER = os.environ.get("MONGO_SERVER_URL") or "localhost"
MONGODB_PORT = os.environ.get("MONGO_SERVER_PORT") or 27017

MONGODB_USER = os.environ.get("MONGO_USER") or "root"
MONGODB_PASSWORD = os.environ.get("MONGO_PASSWORD") or "example"

ES_HOST = os.environ.get("ES_HOST") or "localhost"
ES_PORT = os.environ.get("ES_PORT") or "9200"

ES_USERNAME = os.environ.get("ES_USER") or "elastic"
ES_PASSWORD = os.environ.get("ES_PASSWORD") or "root"

ELASTIC_INDEX_NAME = os.environ.get("ELASTIC_INDEX_NAME") or "articles_index"
ELASTIC_INDEX_CONFIG = os.environ.get("ELASTIC_INDEX_CONFIG") or "articles_index_config.json"

MONGODB_URI = "mongodb://{user}:{password}@{server_url}:{port}/".format(user=MONGODB_USER, 
                                                                        password=MONGODB_PASSWORD, 
                                                                        server_url=MONGODB_SERVER, 
                                                                        port=MONGODB_PORT)

# db name
MONGODB_DB = os.environ.get("MONGO_DB") or "ams"

# db collections
MONGODB_ARTICLES = "articles"
MONGODB_CRIMEMAPS = "crimemaps"
MONGODB_ERRORLINKS = "errorlinks"
# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'google_news.middlewares.GoogleNewsSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'google_news.middlewares.GoogleNewsDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html





# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
