# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from ordasambond.settings import DATA_DIR
#from scrapy.exceptions import DropItem
import os


logger = logging.getLogger(__name__)


class SaveOrdasambandPipeline(object):
    # def __init__(self):
    #     self.ordasambond_seen = set()

    def process_item(self, item, spider):
        # ordasamband_hash = hash(item["ordasamband"])
        # if ordasamband_hash in self.ordasambond_seen:
        #     raise DropItem("Duplicate item found: %s" % item["ordasamband"])
        # else:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        filename = os.path.join(DATA_DIR, "ordasambond.txt")
        with open(filename, "ab") as f:
            f.write(item["ordasamband"].encode("utf-8") + "\n")
        return item
