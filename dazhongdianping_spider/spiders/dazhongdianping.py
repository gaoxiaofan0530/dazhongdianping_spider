# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import DazhongdianpingSpiderItem
from scrapy_redis.spiders import RedisCrawlSpider
import time

class DazhongdianpingSpider(RedisCrawlSpider):
    name = 'dazhongdianping'
    allowed_domains = ['dianping.com']
    redis_key = 'dazhongdianping:start_urls'

    # start_urls = ['http://www.dianping.com/beijing/ch50/g157r1481']

    # 查找全部行业
    # def parse(self, response):
    #     hangye_list = response.xpath('//div[@id="classfy"]/a/@href').extract()  # 行业列表
    #     # print(chengqu_list)
    #     for i in range(1,len(hangye_list)+1):  # 全部行业
    #         # print(i)
    #         url = hangye_list[i]
    #         print('当前行业:' + url)
    #         yield scrapy.Request(url=url, callback=self.parse_chengqu)

    # 查找城区
    # def parse(self, response):
    #     chengqu_list = response.xpath('//div[@id="region-nav"]/a/@href').extract()  # 城区地址
    #     # print(chengqu_list)
    #     for i in range(1, len(chengqu_list)):  # 一共有16个城区
    #         # print(i)
    #         url = chengqu_list[i]
    #         print('当前城区:' + url)
    #         yield scrapy.Request(url=url, callback=self.parse_shangquan)

    # 查找商圈
    def parse(self, response):
        if 'https://verify.meituan.com' in response.url:
            print('遇到验证码，等待20秒，请尽快解决')
            time.sleep(20)
            shangquan_list = response.xpath('//div[@id="region-nav-sub"]/a/@href').extract()  # 商圈的地址
            for i in range(1, len(shangquan_list) - 2):
                url = response.xpath('//div[@id="region-nav-sub"]/a[' + str(1 + i) + ']/@href').extract_first()
                print('当前商圈:' + url)
                yield scrapy.Request(url=url, callback=self.parse_jiexi)
        else:
            time.sleep(20)
            shangquan_list = response.xpath('//div[@id="region-nav-sub"]/a/@href').extract()  # 商圈的地址
            for i in range(1, len(shangquan_list) - 2):
                url = response.xpath('//div[@id="region-nav-sub"]/a[' + str(1 + i) + ']/@href').extract_first()
                print('当前商圈:' + url)
                yield scrapy.Request(url=url, callback=self.parse_jiexi)
    # 每页的结果
    def parse_jiexi(self, response):
        if 'https://verify.meituan.com' in response.url:
            print('遇到验证码，等待20秒，请尽快解决')
            time.sleep(20)
            shop_id_list = response.xpath('//div[@class="tit"]/a[1]/@data-shopid').extract()  # 店铺IP
            url_list = response.xpath('//div[@class="tit"]/a[1]/@href').extract()  # 详情页地址
            next_url_list = response.xpath('//div[@class="page"]/a/@href').extract()
            i = 0
            for url in url_list:
                print(url)
                shop_id = shop_id_list[i]
                i += 1
                yield scrapy.Request(url=url, meta={'shop_id': shop_id}, callback=self.parse_item)

            for next_url_count in next_url_list:
                next_url = next_url_count
                if next_url != '':
                    yield scrapy.Request(url=next_url, callback=self.parse_jiexi)
        else:
            shop_id_list = response.xpath('//div[@class="tit"]/a[1]/@data-shopid').extract()  # 店铺IP
            url_list = response.xpath('//div[@class="tit"]/a[1]/@href').extract()  # 详情页地址
            next_url_list = response.xpath('//div[@class="page"]/a/@href').extract()
            i = 0
            for url in url_list:
                print(url)
                shop_id = shop_id_list[i]
                i += 1
                yield scrapy.Request(url=url, meta={'shop_id': shop_id}, callback=self.parse_item)

            for next_url_count in next_url_list:
                next_url = next_url_count
                if next_url != '':
                    yield scrapy.Request(url=next_url, callback=self.parse_jiexi)

    # 解析详情页
    def parse_item(self, response):
        if 'https://verify.meituan.com' in response.url:
            print('遇到验证码，等待20秒，请尽快解决')
            time.sleep(20)
            item = DazhongdianpingSpiderItem()
            # 店铺id
            shop_id = response.meta['shop_id']
            item['shop_id'] = shop_id
            # 店铺名称
            shop_name = response.xpath('//div[@id="basic-info"]/h1/text()').extract_first().strip()
            item['shop_name'] = shop_name
            # 店铺星级
            shop_start = response.xpath('//div[@class="brief-info"]/span[1]/@class').extract_first()
            if shop_start == None:
                shop_start = 0
            else:
                shop_start = int(re.findall('\d+', shop_start)[0]) / 10
            item['shop_start'] = shop_start
            # 评论数
            shop_review_count = response.xpath('//div[@class="brief-info"]/span[2]/text()').extract_first()  # 评论数
            if '消费' in shop_review_count:
                shop_review_count = 0
                item['shop_review_count'] = shop_review_count
                # 差评数
                shop_bad_review_1star = response.xpath('//a[@data-value="1star"]/span/text()').extract_first()
                if shop_bad_review_1star == None:  # 判断是否为空
                    shop_bad_review_1star = 0
                else:
                    shop_bad_review_1star = int(re.findall('\d+', shop_bad_review_1star)[0])
                shop_bad_review_2star = response.xpath('//a[@data-value="2star"]/span/text()').extract_first()  # 2星评论
                if shop_bad_review_2star == None:
                    shop_bad_review_2star = 0
                else:
                    shop_bad_review_2star = int(re.findall('\d+', shop_bad_review_2star)[0])
                shop_bad_review = str(shop_bad_review_1star + shop_bad_review_2star)
                item['shop_bad_review'] = shop_bad_review
                # 人均消费
                shop_per_capita_consumption = response.xpath('//div[@class="brief-info"]/span[2]/text()').extract_first()
                if re.findall('\d+', shop_per_capita_consumption) == []:
                    shop_per_capita_consumption = 0
                else:
                    shop_per_capita_consumption = int(re.findall('\d+', shop_per_capita_consumption)[0])
                item['shop_per_capita_consumption'] = shop_per_capita_consumption
                # 效果
                shop_effect = response.xpath('//div[@class="brief-info"]/span[3]/text()').extract_first()
                if re.findall('\d+', shop_effect) == []:
                    shop_effect = 0
                else:
                    if '.' in shop_effect:
                        shop_effect = re.findall('\d+\.\d+', shop_effect)[0]
                    else:
                        shop_effect = int(re.findall('\d+', shop_effect)[0])
                item['shop_effect'] = shop_effect
                # 环境
                shop_service = response.xpath('//div[@class="brief-info"]/span[4]/text()').extract_first()
                if re.findall('\d+', shop_service) == []:
                    shop_service = 0
                else:
                    if '.' in shop_service:
                        shop_service = re.findall('\d+\.\d+', shop_service)[0]
                    else:
                        shop_service = int(re.findall('\d+', shop_service)[0])
                item['shop_service'] = shop_service
                # 服务
                shop_surroundings = response.xpath('//div[@class="brief-info"]/span[5]/text()').extract_first()
                print(shop_surroundings)
                if re.findall('\d+', shop_surroundings) == []:
                    shop_surroundings = 0
                else:
                    if '.' in shop_surroundings:
                        shop_surroundings = re.findall('\d+\.\d+', shop_surroundings)[0]
                    else:
                        shop_surroundings = int(re.findall('\d+', shop_surroundings)[0])
                item['shop_surroundings'] = shop_surroundings
                # 地址
                # shop_address1 = response.xpath('//*[@id="basic-info"]/div[2]/span[1]/text()').extract_first()  # 地址
                # 区名
                shop_address2 = response.xpath('//*[@id="basic-info"]/div[2]/a/span/text()').extract_first()  # 区名
                # 详细地址
                shop_address3 = response.xpath(
                    '//*[@id="basic-info"]/div[2]/span[2]/text()').extract_first().strip()  # 详细地址
                if shop_address2 == None or shop_address3 == None:
                    shop_address = '没有标注'
                else:
                    shop_address = shop_address2 + shop_address3  # 拼接地址
                item['shop_address'] = shop_address
                # 区域
                item['shop_region'] = response.xpath('//div[@id="body"]/div[2]/div[1]/a[2]/text()').extract_first().strip()
                # 商圈
                item['shop_business_district'] = response.xpath(
                    '//div[@id="body"]/div[2]/div[1]/a[3]/text()').extract_first().strip()
                # 品类
                item['shop_category'] = response.xpath(
                    '//div[@id="body"]/div[2]/div[1]/a[4]/text()').extract_first().strip()
                # 电话
                shop_telephonenumber = response.xpath('//*[@id="basic-info"]/p/span[2]/text()').extract_first()  # 电话
                if shop_telephonenumber == None:
                    item['shop_telephonenumber'] = '没有标注'
                else:
                    shop_telephonenumber = shop_telephonenumber
                    item['shop_telephonenumber'] = shop_telephonenumber
                # shop_preferential1 = response.xpath('//div[@id="sales"]/div[@class="group_clearfix"][1]/div[@class="item_big"][1]/p[@class="title"]/text()').extract_first()
                # print(shop_preferential1)
                # num = 0
                # for i in range(2):
                #     num += 1
                #     if num == 1:
                #         shop_preferential = response.xpath('//div[@id="sales"]/div[@class="group_clearfix"][1]/div[1]')
                #         print(shop_preferential)
                #         shop_preferential_name = shop_preferential.xpath('/p[@class="title"]/text()').extract_first()
                #         print(shop_preferential_name)
                # shop_preferential = response.xpath('//div[@id="sales"]/')
                # shop_start = response.xpath('//div[@id="basic-info"]/div[@class="brief-info"]/span[1]/@title/text()')
                # print(shop_start)
                yield item
            else:
                if shop_review_count == None:
                    shop_review_count = 0
                else:
                    shop_review_count = int(re.findall('\d+', shop_review_count)[0])
                item['shop_review_count'] = shop_review_count
                # 差评数
                shop_bad_review_1star = response.xpath('//a[@data-value="1star"]/span/text()').extract_first()
                if shop_bad_review_1star == None:  # 判断是否为空
                    shop_bad_review_1star = 0
                else:
                    shop_bad_review_1star = int(re.findall('\d+', shop_bad_review_1star)[0])
                shop_bad_review_2star = response.xpath('//a[@data-value="2star"]/span/text()').extract_first()  # 2星评论
                if shop_bad_review_2star == None:
                    shop_bad_review_2star = 0
                else:
                    shop_bad_review_2star = int(re.findall('\d+', shop_bad_review_2star)[0])
                shop_bad_review = str(shop_bad_review_1star + shop_bad_review_2star)
                item['shop_bad_review'] = shop_bad_review
                # 人均消费
                shop_per_capita_consumption = response.xpath('//div[@class="brief-info"]/span[3]/text()').extract_first()
                if re.findall('\d+', shop_per_capita_consumption) == []:
                    shop_per_capita_consumption = 0
                else:
                    shop_per_capita_consumption = int(re.findall('\d+', shop_per_capita_consumption)[0])
                item['shop_per_capita_consumption'] = shop_per_capita_consumption
                # 效果
                shop_effect = response.xpath('//div[@class="brief-info"]/span[4]/text()').extract_first()
                if re.findall('\d+', shop_effect) == []:
                    shop_effect = 0
                else:
                    if '.' in shop_effect:
                        shop_effect = re.findall('\d+\.\d+', shop_effect)[0]
                    else:
                        shop_effect = int(re.findall('\d+', shop_effect)[0])
                item['shop_effect'] = shop_effect
                # 环境
                shop_service = response.xpath('//div[@class="brief-info"]/span[5]/text()').extract_first()
                if re.findall('\d+', shop_service) == []:
                    shop_service = 0
                else:
                    if '.' in shop_service:
                        shop_service = re.findall('\d+\.\d+', shop_service)[0]
                    else:
                        shop_service = int(re.findall('\d+', shop_service)[0])
                item['shop_service'] = shop_service
                # 服务
                shop_surroundings = response.xpath('//div[@class="brief-info"]/span[6]/text()').extract_first()
                print(shop_surroundings)
                if re.findall('\d+', shop_surroundings) == []:
                    shop_surroundings = 0
                else:
                    if '.' in shop_surroundings:
                        shop_surroundings = re.findall('\d+\.\d+', shop_surroundings)[0]
                    else:
                        shop_surroundings = int(re.findall('\d+', shop_surroundings)[0])
                item['shop_surroundings'] = shop_surroundings
                # 地址
                # shop_address1 = response.xpath('//*[@id="basic-info"]/div[2]/span[1]/text()').extract_first()  # 地址
                # 区名
                shop_address2 = response.xpath('//*[@id="basic-info"]/div[2]/a/span/text()').extract_first()  # 区名
                # 详细地址
                shop_address3 = response.xpath(
                    '//*[@id="basic-info"]/div[2]/span[2]/text()').extract_first().strip()  # 详细地址
                if shop_address2 == None or shop_address3 == None:
                    shop_address = '没有标注'
                else:
                    shop_address = shop_address2 + shop_address3  # 拼接地址
                item['shop_address'] = shop_address
                # 区域
                item['shop_region'] = response.xpath('//div[@id="body"]/div[2]/div[1]/a[2]/text()').extract_first().strip()
                # 商圈
                item['shop_business_district'] = response.xpath(
                    '//div[@id="body"]/div[2]/div[1]/a[3]/text()').extract_first().strip()
                # 品类
                item['shop_category'] = response.xpath(
                    '//div[@id="body"]/div[2]/div[1]/a[4]/text()').extract_first().strip()
                # 电话
                shop_telephonenumber = response.xpath('//*[@id="basic-info"]/p/span[2]/text()').extract_first()  # 电话
                if shop_telephonenumber == None:
                    item['shop_telephonenumber'] = '没有标注'
                else:
                    shop_telephonenumber = shop_telephonenumber
                    item['shop_telephonenumber'] = shop_telephonenumber
                # shop_preferential1 = response.xpath('//div[@id="sales"]/div[@class="group_clearfix"][1]/div[@class="item_big"][1]/p[@class="title"]/text()').extract_first()
                # print(shop_preferential1)
                # num = 0
                # for i in range(2):
                #     num += 1
                #     if num == 1:
                #         shop_preferential = response.xpath('//div[@id="sales"]/div[@class="group_clearfix"][1]/div[1]')
                #         print(shop_preferential)
                #         shop_preferential_name = shop_preferential.xpath('/p[@class="title"]/text()').extract_first()
                #         print(shop_preferential_name)
                # shop_preferential = response.xpath('//div[@id="sales"]/')
                # shop_start = response.xpath('//div[@id="basic-info"]/div[@class="brief-info"]/span[1]/@title/text()')
                # print(shop_start)
                yield item

            # print('---------------------------------------------')
        # except IndexError as e:
        #     print('程序出错' + str(e) + '网址:' + response.url)
        else:
            item = DazhongdianpingSpiderItem()
            # 店铺id
            shop_id = response.meta['shop_id']
            item['shop_id'] = shop_id
            # 店铺名称
            shop_name = response.xpath('//div[@id="basic-info"]/h1/text()').extract_first().strip()
            item['shop_name'] = shop_name
            # 店铺星级
            shop_start = response.xpath('//div[@class="brief-info"]/span[1]/@class').extract_first()
            if shop_start == None:
                shop_start = 0
            else:
                shop_start = int(re.findall('\d+', shop_start)[0]) / 10
            item['shop_start'] = shop_start
            # 评论数
            shop_review_count = response.xpath('//div[@class="brief-info"]/span[2]/text()').extract_first()  # 评论数
            if '消费' in shop_review_count:
                shop_review_count = 0
                item['shop_review_count'] = shop_review_count
                # 差评数
                shop_bad_review_1star = response.xpath('//a[@data-value="1star"]/span/text()').extract_first()
                if shop_bad_review_1star == None:  # 判断是否为空
                    shop_bad_review_1star = 0
                else:
                    shop_bad_review_1star = int(re.findall('\d+', shop_bad_review_1star)[0])
                shop_bad_review_2star = response.xpath('//a[@data-value="2star"]/span/text()').extract_first()  # 2星评论
                if shop_bad_review_2star == None:
                    shop_bad_review_2star = 0
                else:
                    shop_bad_review_2star = int(re.findall('\d+', shop_bad_review_2star)[0])
                shop_bad_review = str(shop_bad_review_1star + shop_bad_review_2star)
                item['shop_bad_review'] = shop_bad_review
                # 人均消费
                shop_per_capita_consumption = response.xpath('//div[@class="brief-info"]/span[2]/text()').extract_first()
                if re.findall('\d+', shop_per_capita_consumption) == []:
                    shop_per_capita_consumption = 0
                else:
                    shop_per_capita_consumption = int(re.findall('\d+', shop_per_capita_consumption)[0])
                item['shop_per_capita_consumption'] = shop_per_capita_consumption
                # 效果
                shop_effect = response.xpath('//div[@class="brief-info"]/span[3]/text()').extract_first()
                if re.findall('\d+', shop_effect) == []:
                    shop_effect = 0
                else:
                    if '.' in shop_effect:
                        shop_effect = re.findall('\d+\.\d+', shop_effect)[0]
                    else:
                        shop_effect = int(re.findall('\d+', shop_effect)[0])
                item['shop_effect'] = shop_effect
                # 环境
                shop_service = response.xpath('//div[@class="brief-info"]/span[4]/text()').extract_first()
                if re.findall('\d+', shop_service) == []:
                    shop_service = 0
                else:
                    if '.' in shop_service:
                        shop_service = re.findall('\d+\.\d+', shop_service)[0]
                    else:
                        shop_service = int(re.findall('\d+', shop_service)[0])
                item['shop_service'] = shop_service
                # 服务
                shop_surroundings = response.xpath('//div[@class="brief-info"]/span[5]/text()').extract_first()
                print(shop_surroundings)
                if re.findall('\d+', shop_surroundings) == []:
                    shop_surroundings = 0
                else:
                    if '.' in shop_surroundings:
                        shop_surroundings = re.findall('\d+\.\d+', shop_surroundings)[0]
                    else:
                        shop_surroundings = int(re.findall('\d+', shop_surroundings)[0])
                item['shop_surroundings'] = shop_surroundings
                # 地址
                # shop_address1 = response.xpath('//*[@id="basic-info"]/div[2]/span[1]/text()').extract_first()  # 地址
                # 区名
                shop_address2 = response.xpath('//*[@id="basic-info"]/div[2]/a/span/text()').extract_first()  # 区名
                # 详细地址
                shop_address3 = response.xpath(
                    '//*[@id="basic-info"]/div[2]/span[2]/text()').extract_first().strip()  # 详细地址
                if shop_address2 == None or shop_address3 == None:
                    shop_address = '没有标注'
                else:
                    shop_address = shop_address2 + shop_address3  # 拼接地址
                item['shop_address'] = shop_address
                # 区域
                item['shop_region'] = response.xpath('//div[@id="body"]/div[2]/div[1]/a[2]/text()').extract_first().strip()
                # 商圈
                item['shop_business_district'] = response.xpath(
                    '//div[@id="body"]/div[2]/div[1]/a[3]/text()').extract_first().strip()
                # 品类
                item['shop_category'] = response.xpath(
                    '//div[@id="body"]/div[2]/div[1]/a[4]/text()').extract_first().strip()
                # 电话
                shop_telephonenumber = response.xpath('//*[@id="basic-info"]/p/span[2]/text()').extract_first()  # 电话
                if shop_telephonenumber == None:
                    item['shop_telephonenumber'] = '没有标注'
                else:
                    shop_telephonenumber = shop_telephonenumber
                    item['shop_telephonenumber'] = shop_telephonenumber
                # shop_preferential1 = response.xpath('//div[@id="sales"]/div[@class="group_clearfix"][1]/div[@class="item_big"][1]/p[@class="title"]/text()').extract_first()
                # print(shop_preferential1)
                # num = 0
                # for i in range(2):
                #     num += 1
                #     if num == 1:
                #         shop_preferential = response.xpath('//div[@id="sales"]/div[@class="group_clearfix"][1]/div[1]')
                #         print(shop_preferential)
                #         shop_preferential_name = shop_preferential.xpath('/p[@class="title"]/text()').extract_first()
                #         print(shop_preferential_name)
                # shop_preferential = response.xpath('//div[@id="sales"]/')
                # shop_start = response.xpath('//div[@id="basic-info"]/div[@class="brief-info"]/span[1]/@title/text()')
                # print(shop_start)
                yield item
            else:
                if shop_review_count == None:
                    shop_review_count = 0
                else:
                    shop_review_count = int(re.findall('\d+', shop_review_count)[0])
                item['shop_review_count'] = shop_review_count
                # 差评数
                shop_bad_review_1star = response.xpath('//a[@data-value="1star"]/span/text()').extract_first()
                if shop_bad_review_1star == None:  # 判断是否为空
                    shop_bad_review_1star = 0
                else:
                    shop_bad_review_1star = int(re.findall('\d+', shop_bad_review_1star)[0])
                shop_bad_review_2star = response.xpath('//a[@data-value="2star"]/span/text()').extract_first()  # 2星评论
                if shop_bad_review_2star == None:
                    shop_bad_review_2star = 0
                else:
                    shop_bad_review_2star = int(re.findall('\d+', shop_bad_review_2star)[0])
                shop_bad_review = str(shop_bad_review_1star + shop_bad_review_2star)
                item['shop_bad_review'] = shop_bad_review
                # 人均消费
                shop_per_capita_consumption = response.xpath('//div[@class="brief-info"]/span[3]/text()').extract_first()
                if re.findall('\d+', shop_per_capita_consumption) == []:
                    shop_per_capita_consumption = 0
                else:
                    shop_per_capita_consumption = int(re.findall('\d+', shop_per_capita_consumption)[0])
                item['shop_per_capita_consumption'] = shop_per_capita_consumption
                # 效果
                shop_effect = response.xpath('//div[@class="brief-info"]/span[4]/text()').extract_first()
                if re.findall('\d+', shop_effect) == []:
                    shop_effect = 0
                else:
                    if '.' in shop_effect:
                        shop_effect = re.findall('\d+\.\d+', shop_effect)[0]
                    else:
                        shop_effect = int(re.findall('\d+', shop_effect)[0])
                item['shop_effect'] = shop_effect
                # 环境
                shop_service = response.xpath('//div[@class="brief-info"]/span[5]/text()').extract_first()
                if re.findall('\d+', shop_service) == []:
                    shop_service = 0
                else:
                    if '.' in shop_service:
                        shop_service = re.findall('\d+\.\d+', shop_service)[0]
                    else:
                        shop_service = int(re.findall('\d+', shop_service)[0])
                item['shop_service'] = shop_service
                # 服务
                shop_surroundings = response.xpath('//div[@class="brief-info"]/span[6]/text()').extract_first()
                print(shop_surroundings)
                if re.findall('\d+', shop_surroundings) == []:
                    shop_surroundings = 0
                else:
                    if '.' in shop_surroundings:
                        shop_surroundings = re.findall('\d+\.\d+', shop_surroundings)[0]
                    else:
                        shop_surroundings = int(re.findall('\d+', shop_surroundings)[0])
                item['shop_surroundings'] = shop_surroundings
                # 地址
                # shop_address1 = response.xpath('//*[@id="basic-info"]/div[2]/span[1]/text()').extract_first()  # 地址
                # 区名
                shop_address2 = response.xpath('//*[@id="basic-info"]/div[2]/a/span/text()').extract_first()  # 区名
                # 详细地址
                shop_address3 = response.xpath(
                    '//*[@id="basic-info"]/div[2]/span[2]/text()').extract_first().strip()  # 详细地址
                if shop_address2 == None or shop_address3 == None:
                    shop_address = '没有标注'
                else:
                    shop_address = shop_address2 + shop_address3  # 拼接地址
                item['shop_address'] = shop_address
                # 区域
                item['shop_region'] = response.xpath('//div[@id="body"]/div[2]/div[1]/a[2]/text()').extract_first().strip()
                # 商圈
                item['shop_business_district'] = response.xpath(
                    '//div[@id="body"]/div[2]/div[1]/a[3]/text()').extract_first().strip()
                # 品类
                item['shop_category'] = response.xpath(
                    '//div[@id="body"]/div[2]/div[1]/a[4]/text()').extract_first().strip()
                # 电话
                shop_telephonenumber = response.xpath('//*[@id="basic-info"]/p/span[2]/text()').extract_first()  # 电话
                if shop_telephonenumber == None:
                    item['shop_telephonenumber'] = '没有标注'
                else:
                    shop_telephonenumber = shop_telephonenumber
                    item['shop_telephonenumber'] = shop_telephonenumber
                # shop_preferential1 = response.xpath('//div[@id="sales"]/div[@class="group_clearfix"][1]/div[@class="item_big"][1]/p[@class="title"]/text()').extract_first()
                # print(shop_preferential1)
                # num = 0
                # for i in range(2):
                #     num += 1
                #     if num == 1:
                #         shop_preferential = response.xpath('//div[@id="sales"]/div[@class="group_clearfix"][1]/div[1]')
                #         print(shop_preferential)
                #         shop_preferential_name = shop_preferential.xpath('/p[@class="title"]/text()').extract_first()
                #         print(shop_preferential_name)
                # shop_preferential = response.xpath('//div[@id="sales"]/')
                # shop_start = response.xpath('//div[@id="basic-info"]/div[@class="brief-info"]/span[1]/@title/text()')
                # print(shop_start)
                yield item

            # print('---------------------------------------------')
        # except IndexError as e:
        #     print('程序出错' + str(e) + '网址:' + response.url)
