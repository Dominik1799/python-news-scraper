## How to run
  * git clone <url>
  * go to repository folder
  * python -m venv .\venv
  * .\venv\Scripts\activate
  * pip install -r requirements.txt
  * cd .\development
  * docker-compose up -d
  * cd ..\scraper
  * scrapy scrawl news_spider <ARGUMENTS>
 
 arguments:
  * crimes_file=<FILENAME> - filename of crimes to parse. (murder.txt / list_of_crimes_english.txt / list_of_crimes_slovak.txt etc.)
  * search_from=YYYY-MM-DD - date
  * search_to=YYYY-MM-DD - date
  * locale=locale - set your locale (en-gb / sk-sk etc.)
 
Arguments need to be passed using scrapy anotation, with the _-a_ switch.
Example:
 
```
 scrapy crawl news_spider -a crimes_file=murder.txt -a search_from=2020-01-01 -a search_to=2020-01-04 -a locale=en-gb
```

## Testing:
Run this commad in the root of this repository:
```
python -m unittest discover
```
