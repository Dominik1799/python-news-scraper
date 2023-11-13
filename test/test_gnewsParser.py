import sys
import os
import unittest
# this is so you can import GnewsParser even though it's in another package
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from scraper.gnewsparser import GnewsParser


class TestGnewsParser(unittest.TestCase):
    def test_setup_phase(self):
        gnews_parser = GnewsParser()
        gnews_parser.setup_search("murder", "2020-01-01", "2020-01-03", locale="sk-sk")
        gnews_parser.get_results()
        state = gnews_parser.save_state()
        self.assertEqual(state["last_url"], "https://news.google.com/rss/search?q=murder+after:2020-01-01+before:2020-01-02&hl=sk&gl=SK&ceid=SK:sk")
        self.assertEqual(state["query"], "murder")
        self.assertEqual(state["days_step"], 1)

    def test_connection(self):
        gnews_parser = GnewsParser()
        gnews_parser.setup_search("murder", "2020-01-01", "2020-01-03", locale="sk-sk")
        self.assertIsNotNone(gnews_parser.get_results())