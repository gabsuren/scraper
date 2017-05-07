import unittest
import os, sys
from faragov_scraper.spiders import active_principals
from responses import fake_response_from_file

class ActivePrincipalSpiderTest(unittest.TestCase):
    """
    This class is provided sample check for ActivePrincipalSpider parse function.
    It parses the content of data/fara_quick_search.html and checks if created object is correct,
    by extracting and comparing first and last object values.
    """
    def setUp(self):
        self.spider = active_principals.ActivePrincipalsSpider()

    def _test_item_results(self, results):
        print type(results)
        item = next(results)
        print type(item)
        self.assertRegexpMatches("AFGHANISTAN", item.body)
        for i in range(1, 14):
            next(results)
        item = next(results)
        self.assertRegexpMatches("AUSTRALIA", item.body)

    def test_parse(self):
        results = self.spider.parse(fake_response_from_file('data/fara_quick_search.html'))
        self._test_item_results(results)

if __name__ == '__main__':
    unittest.main()
