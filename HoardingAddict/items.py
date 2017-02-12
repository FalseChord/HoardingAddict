# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImageItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    names = scrapy.Field()
    image_sizes = scrapy.Field()
    
    # for image pipeline
    image_urls = scrapy.Field() #image download url
    image_paths = scrapy.Field() #relative store path
    image_checksums = scrapy.Field()
    image_store_path = scrapy.Field() #absolute store path
    images = scrapy.Field()