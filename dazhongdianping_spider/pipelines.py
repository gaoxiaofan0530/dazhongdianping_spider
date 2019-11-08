# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class DazhongdianpingSpiderPipeline(object):
    def process_item(self, item, spider):
        return item

#  存数据库
class MySqlPipeline(object):
    def open_spider(self, spider):
        self.connction = pymysql.connect("localhost", "root", "123456", "dazhongdianping")
        self.cursor = self.connction.cursor()

    def process_item(self, item, spider):
        # sql语句
        # 测试分支
        sql = "INSERT INTO app_dazhongdianping_liren_all_data VALUES(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.cursor.execute(sql, (
            item['shop_id'], item['shop_name'], item['shop_start'],
            item['shop_review_count'], item['shop_bad_review'], item['shop_per_capita_consumption'],
            item['shop_effect'], item['shop_service'], item['shop_surroundings'],
            item['shop_address'],item['shop_telephonenumber'],item['shop_region'],item['shop_business_district'],item['shop_category'],'无'))
        self.connction.commit()
        # 将python对象，转换成json串
        return item  # 千万别忘了
    def close_spider(self, spider):
        self.cursor.close()
        self.connction.close()