# -*- coding: utf-8 -*-

from itertools import permutations
import logging
import scrapy
import string
import lxml.html
from ordasambond.items import OrdasambondItem
import re
import urllib2

results_regex = re.compile(ur'\d+\/(\d+)')
search_text_regex = re.compile(ur'ftexti=(.+)')
start_position_regex = re.compile(ur'pos=(\d+)')

logger = logging.getLogger(__name__)

BASE_SEARCH_URL = "http://www.lexis.hi.is/osamb/osamb.pl?finna=Leita&ftexti={}"
BASE_URL = "http://www.lexis.hi.is/osamb/"


class OrdasambondScraper(scrapy.Spider):
    name = "ordasambond_spider"
    allowed_domains = ["lexis.hi.is"]

    def parse_url(self, url):
        start_position = re.search(start_position_regex, url)
        search_text = re.search(search_text_regex, url)
        search_text = search_text.groups()[0]
        search_text = urllib2.unquote(search_text.decode('iso-8859-1')).encode('utf-8')
        if not start_position:
            start_position = "0"
        else:
            start_position = start_position.groups()[0]
        return [search_text, start_position]

    def start_requests(self):
        alphabet = string.ascii_lowercase
        icelandic = u'áíóéúýðþæö'
        alphabet = alphabet + icelandic
        alphabet = alphabet.encode('iso-8859-1')
        for letterstring in permutations(alphabet, 3):
            letterstring = "".join(letterstring)
            request = self.make_requests_from_url(
                        BASE_SEARCH_URL.format(letterstring)
                            )
            yield request

    def parse(self, response):
        logger.info("Parsing {}".format(response.url))
        body = response.body.decode('iso-8859-1')
        search_text, start_position = self.parse_url(response.url)
        if u"Of margar færslur fundust" in body:
            logger.warning("Too many results for {} at position {}".format(search_text, start_position))
            return
        count_results = re.search(results_regex, response.body)
        if int(count_results.groups()[0]) == 0:
            logger.info("Zero results for {} at position {}".format(search_text, start_position))
        else:
            logger.info("Total {} results for {} at position {}".format(count_results.groups()[0], search_text, start_position))
            root = lxml.html.fromstring(body)
            words = root.xpath("//td[@bgcolor='#d9e4eb']")
            if words:
                logger.info("Processing {} words for {} at position {}".format(len(words), search_text, start_position))
                for word in words:
                    item = OrdasambondItem()
                    item["url"] = response.url
                    item["ordasamband"] = word.text_content()
                    yield item
            next_link = root.xpath("//a[contains(text(), '{}')]/@href".format('N\xe6sta s\xed\xf0a').decode('iso-8859-1'))
            if next_link:
                url = BASE_URL + next_link[0]
                yield scrapy.Request(url, callback=self.parse)
            else:
                logger.info("No more results for {} at position {}".format(search_text, start_position))


