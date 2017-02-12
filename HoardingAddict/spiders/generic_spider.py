#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# scrapy api
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

import os
import logging

from HoardingAddict.spiders._img_spider import SpiderFactory
from HoardingAddict.spiders.config import configs

configure_logging({"LOG_LEVEL":logging.INFO})
settings = get_project_settings()

@defer.inlineCallbacks
def spawnSpiders():
    for config in configs:
        #print(config)
        settings.set('DEFAULT_REQUEST_HEADERS', {'Referer': config['root']})
        settings.set('IMAGES_STORE', os.path.join(os.pardir, settings.get('IMAGES_STORE'), config['name']))
        try:
            settings.set('IMAGES_MIN_WIDTH', config['image_limitations']['width'])
            settings.set('IMAGES_MIN_HEIGHT', config['image_limitations']['height'])
        except Exception as e:
            #print(e) #not such setting, ignore
            pass
        #print(settings.get('IMAGES_MIN_WIDTH'),settings.get('IMAGES_MIN_HEIGHT'))
        runner = CrawlerRunner(settings)
        spider = SpiderFactory(config)
        yield runner.crawl(spider)
    reactor.stop()

spawnSpiders()
reactor.run()
