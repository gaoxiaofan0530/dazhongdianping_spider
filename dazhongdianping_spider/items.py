# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DazhongdianpingSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    shop_id = scrapy.Field()
    shop_name = scrapy.Field()
    shop_start = scrapy.Field()
    shop_review_count = scrapy.Field()
    shop_bad_review = scrapy.Field()
    shop_per_capita_consumption = scrapy.Field()
    shop_effect = scrapy.Field()
    shop_region = scrapy.Field()
    shop_business_district = scrapy.Field()
    shop_category = scrapy.Field()
    shop_service = scrapy.Field()
    shop_surroundings = scrapy.Field()
    shop_address = scrapy.Field()
    shop_telephonenumber = scrapy.Field()
