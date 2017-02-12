# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from PIL import Image
import os

from HoardingAddict.psql import Psql

class ImageDataProcessPipeline(object):

    def open_spider(self, spider):
        #print('spider is opening, connect to db...')
        self.psql = Psql(
            spider.settings.attributes['PSQL_DATABASE'].value,
            spider.settings.attributes['PSQL_USERNAME'].value
        )
        self.psql.create_col(spider.name, spider.settings.attributes['IMAGES_STORE'].value, spider.ended)

    def close_spider(self, spider):
        self.psql.update_col(spider.name)

    def process_item(self, item, spider):
        print('process_item', item)
        for name, checksum, size, path, url in zip(
            item['names'], 
            item['image_checksums'], 
            item['image_sizes'], 
            item['image_paths'], 
            item['image_urls']
        ):
            self.psql.create_img(spider.name, name, checksum, size, path, url, spider.type)
        return item

class ImageFetchPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        #print('get media items', item, info)
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        #print('item complete', results, item)
        image_paths = [x['path'] for ok, x in results if ok]
        image_checksums = [x['checksum'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        item['image_checksums'] = image_checksums
        full_path = [ os.path.join(item['image_store_path'], filepath) for filepath in item['image_paths']]

        def getImageSize(path):
            with Image.open(path) as im:
                return im.size
        item['image_sizes'] = list(map(getImageSize, full_path))

        return item