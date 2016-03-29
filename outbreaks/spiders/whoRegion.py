# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector
from outbreaks.items import OutbreaksItems


class OutbreakRegion(scrapy.Spider):
    name = "outbreakRegion"
    allowed_domains = ["http://www.who.int"]
    start_urls = [
        "http://www.who.int/csr/don/archive/year/2016/en/"
    ]

    def parse(self, response):
        print "Processing Data............................................."
        outbreakpost = Selector(response).xpath("//ul[@class='auto_archive']")
        items = []
        for post in outbreakpost:
            item = OutbreaksItems()
            item['lastUpdated'] = post.xpath("li/a/text()").extract()
            item['outbreakNameCountry'] = post.xpath("li/span/text()").extract()
            items.append(item)

        return items
