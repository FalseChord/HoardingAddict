#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy import signals, Request, FormRequest

import logging
import os
import sys
from urllib.parse import urljoin

from HoardingAddict.items import ImageItem
from HoardingAddict.spiders.config import callbackConfig

class BaseSpider(CrawlSpider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):        
        thisspider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(thisspider.spider_onclose, signal=signals.spider_closed)
        return thisspider

    def spider_onclose(self, spider):
        print('spider '+self.name+' is closing')

    def parsed_callback(self, res):
        callbackID = res.meta['callbackID'] if 'callbackID' in res.meta else 'default'
        config = callbackConfig[self.name][callbackID]

        (target, name) = self.extract_from_res(res, config)
        print('callback:',callbackID, '\n', res.url, '\n', target, '\n', name)
        for req in self.generate_req(config, target, name):
            yield req

    def start_requests(self):
        config = self.request_config
        if(config['protocol']) == 'POST':
            while len(config['urls']) > len(config['formdata']):
                config['formdata'].append(config['formdata'][0])
            while len(config['urls']) < len(config['formdata']):
                config['urls'].append(config['urls'][0])
            return [ FormRequest(url, formdata=formdata, callback=self.parsed_callback) for url, formdata in zip(config['urls'], config['formdata'])]
        else:
            return [ Request(url, callback=self.parsed_callback) for url in config['urls']]
        #BaseSpider.start_requests()

    def generate_req(self, config, target, name):
        if name == []:
            name = ['NONAME']
        while len(target) > len(name):
            name.append(name[0])
        if ('follow' in config):
            for url, n in zip(target, name):
                req = Request(url, callback=self.parsed_callback)
                req.meta['callbackID'] = config['follow']
                req.meta['name'] = n
                yield req
        else:
            item = ImageItem({
                'names': name, 
                'image_urls': target,
                'image_store_path': os.path.abspath(self.settings.attributes['IMAGES_STORE'].value)
            })
            yield item

    def extract_from_res(self, res, config):
        #target 來源： xpath(config['target_dom']) or res[config['target_dom']]
        #name 來源： xpath(config['name_dom']) or res.meta['name']
        try:
            target = res.xpath(config['target_dom']).extract()
            target = list(map(lambda x: urljoin(res.url, x), target))
        except:
            target = []
        finally:
            if len(target) == 0:
                if 'target_alt' in config and hasattr(res, config['target_alt']):
                    target = [getattr(res, config['target_alt'])]
                elif 'target_dom' in config and hasattr(res, config['target_dom']):
                    target = [getattr(res, config['target_dom'])]

        try:
            name = res.xpath(config['name_dom']).extract()
            name = list(map(lambda x: x.strip(), name))
        except:
            if ('name' in res.meta):
                name = [res.meta['name']]
            else:
                name = []
        return (target, name)


def SpiderFactory(config, BaseSpider=BaseSpider):
    def __init__(self):
        self.type = config['type']
        self.name = config['name']
        self.ended = config['ended']
        self.request_config = config['request']
        self.rules = [
                #Rule(LinkExtractor(deny_extensions='', tags=('img', ), attrs=('src', )), callback='img_parsed'),
        ]
        for rule in config['rules']:
            self.rules.append(Rule(
                LinkExtractor(**rule['extractor']),
                callback=rule['callback'],
            ))
        BaseSpider.__init__(self)

    newSpiderClass = type(config['name']+'Class', (BaseSpider,), {"__init__": __init__})
    return newSpiderClass




