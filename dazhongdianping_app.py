# -*- encoding=utf8 -*-
from airtest.core.api import auto_setup
import time
import requests
import re
from lxml import etree
import pymysql
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
# 操作手机端
poco = AndroidUiautomationPoco(use_alrtest_input=True,
                               screenshot_each_action=False)
# # 进入大众点评
# poco(text="大众点评").click()
# # 进入丽人
# time.sleep(10)
# poco(text="丽人/美发").click()
# time.sleep(3)
# poco(text="美甲美睫").click()
# time.sleep(4)
# poco(text="筛选").click()
# time.sleep(3)
# poco(text="新店").click()
# time.sleep(4)
# poco(text="确定").click()
# time.sleep(3)

def get_url_data(url):
    # 设置请求头
    headers = {
        'Accept':
        'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Cookie':'s_ViewType=10; _lxsdk_cuid=16d1e3d755bc8-0dd2e391c603eb-5373e62-144000-16d1e3d755cc8; _lxsdk=16d1e3d755bc8-0dd2e391c603eb-5373e62-144000-16d1e3d755cc8; _hc.v=224df215-bde2-3c65-8fbf-f0f3b9adf599.1568170407; cityid=2; switchcityflashtoast=1; source=m_browser_test_33; platformSource=1; userPlatform=PC; requestSource=dp; realAccountId=3323092; accountSource=0; accountId=3323092; fromEntry=1; default_ab=shop%3AA%3A5%7Cindex%3AA%3A1%7CshopList%3AC%3A4; aburl=1; cye=beijing; PHOENIX_ID=0a51d4cf-16dbef711a5-156827; edper=xOkdedaKUXW0H8wAkGeBeYkP8eZt6icmDWY78K6KlBXcbg_ZnCQmh5LtxYJdlDtR0uuUc-S9dK-e8E2PF4OVeg; mpmerchant_portal_shopid=5659606; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; cy=2; _lxsdk_s=16ded5dd4dc-33e-6b4-fa8%7C%7C49',
        'Host': 'www.dianping.com',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
    }
    # 发送post请求，下载网页
    url_data = requests.get(url, headers=headers)
    # 解析网页
    html = etree.HTML(url_data.text)
    # 返回网页数据
    return html

connction = pymysql.connect("localhost", "root", "123456", "dazhongdianping")
cursor = connction.cursor()
try:
    while True:
        time.sleep(3)
        poco.swipe([0.5, 0.8], [0.2, 0.6])
        shop_title = poco("com.dianping.v1:id/tv_shop_title")[0].get_text()
        print(shop_title)
        url_data = get_url_data('https://www.dianping.com/search/keyword/2/0_' + shop_title)
        html_data = url_data
        url = html_data.xpath('//div[@id="shop-all-list"]/ul/li')
        print('搜索到'+str(len(url))+'家店铺') 
        try:
            if len(url) == 1:
                title = html_data.xpath('//div[@id="shop-all-list"]/ul/li/div[@class="txt"]/div[@class="tit"]/a[1]/@title')
                # 判断是否是新店名称
                if title[0] == shop_title:
                    url = html_data.xpath('//div[@id="shop-all-list"]/ul/li/div[@class="txt"]/div[@class="tit"]/a[1]/@href')
                    url_data = get_url_data(url[0])
                    shop_id = html_data.xpath('//div[@id="shop-all-list"]/ul/li/div[@class="txt"]/div[@class="tit"]/a[1]/@data-shopid')
                    print('店铺名称:', shop_title)
                    print('商铺id:',shop_id)
                    shop_id = shop_id[0]
                    shop_start = url_data.xpath('//div[@class="brief-info"]/span[1]/@class')
                    shop_start = shop_start[0]
                    if shop_start == None:
                        shop_start = 0
                    else:
                        shop_start = int(re.findall('\d+',shop_start)[0])/10
                    print('店铺星级:',shop_start)
                    # 评论数
                    try:
                        shop_review_count = url_data.xpath('//div[@class="brief-info"]/span[2]/text()')[0]
                        if shop_review_count == [] or shop_review_count == None:
                            shop_review_count = 0
                        else:
                            shop_review_count = int(re.findall('\d+', shop_review_count)[0])
                        # 效果
                        shop_effect = url_data.xpath('//div[@class="brief-info"]/span[4]/text()')
                        shop_effect = shop_effect[0]
                        if re.findall('\d+',shop_effect) == []:
                            shop_effect = 0
                        else:
                            if '.' in shop_effect:
                                shop_effect = re.findall('\d+\.\d+',shop_effect)[0]
                            else:
                                shop_effect = int(re.findall('\d+',shop_effect)[0])
                        print('效果',shop_effect)
                        # 环境
                        shop_service = url_data.xpath('//div[@class="brief-info"]/span[5]/text()')
                        shop_service = shop_service[0]
                        if re.findall('\d+',shop_service) == []:
                            shop_service = 0
                        else:
                            if '.' in shop_service:
                                shop_service = re.findall('\d+\.\d+', shop_service)[0]
                            else:
                                shop_service = int(re.findall('\d+', shop_service)[0])
                        print('环境:',shop_service)
                        # 服务
                        shop_surroundings = url_data.xpath('//div[@class="brief-info"]/span[6]/text()')
                        shop_surroundings = shop_surroundings[0]
                        if re.findall('\d+',shop_surroundings) == []:
                            shop_surroundings = 0
                        else:
                            if '.' in shop_surroundings:
                                shop_surroundings = re.findall('\d+\.\d+', shop_surroundings)[0]
                            else:
                                shop_surroundings = int(re.findall('\d+', shop_surroundings)[0])
                        print('服务:',shop_surroundings)
                    except:
                        shop_review_count = 0
                        # 效果
                        shop_effect = url_data.xpath('//div[@class="brief-info"]/span[3]/text()')
                        shop_effect = shop_effect[0]
                        if re.findall('\d+',shop_effect) == []:
                            shop_effect = 0
                        else:
                            if '.' in shop_effect:
                                shop_effect = re.findall('\d+\.\d+',shop_effect)[0]
                            else:
                                shop_effect = int(re.findall('\d+',shop_effect)[0])
                        print('效果',shop_effect)
                        # 环境
                        shop_service = url_data.xpath('//div[@class="brief-info"]/span[4]/text()')
                        shop_service = shop_service[0]
                        if re.findall('\d+',shop_service) == []:
                            shop_service = 0
                        else:
                            if '.' in shop_service:
                                shop_service = re.findall('\d+\.\d+', shop_service)[0]
                            else:
                                shop_service = int(re.findall('\d+', shop_service)[0])
                        print('环境:',shop_service)
                        # 服务
                        shop_surroundings = url_data.xpath('//div[@class="brief-info"]/span[5]/text()')
                        shop_surroundings = shop_surroundings[0]
                        if re.findall('\d+',shop_surroundings) == []:
                            shop_surroundings = 0
                        else:
                            if '.' in shop_surroundings:
                                shop_surroundings = re.findall('\d+\.\d+', shop_surroundings)[0]
                            else:
                                shop_surroundings = int(re.findall('\d+', shop_surroundings)[0])
                        print('服务:',shop_surroundings)
                    print('评论数:',shop_review_count)
                    # # 差评数
                    # shop_bad_review_1star = response.xpath('//*[@id="comment"]/h2/span/a[6]/span/text()')
                    # print('1星差评:',shop_bad_review_1star)
                    # if shop_bad_review_1star == None:  # 判断是否为空
                    #     shop_bad_review_1star = 0
                    # else:
                    #     shop_bad_review_1star = int(re.findall('\d+', shop_bad_review_1star)[0])
                    # shop_bad_review_2star = response.xpath('//*[@id="comment"]/h2/span/a[5]/span/text()')  # 2星评论
                    # print('2星差评:',shop_bad_review_2star)
                    # if shop_bad_review_2star == None:
                    #     shop_bad_review_2star = 0
                    # else:
                    #     shop_bad_review_2star = int(re.findall('\d+', shop_bad_review_2star)[0])
                    # shop_bad_review = str(shop_bad_review_1star + shop_bad_review_2star)
                    # print('差评数:',shop_bad_review)
                    # 人均消费
                    shop_per_capita_consumption = url_data.xpath('//div[@class="brief-info"]/span[3]/text()')
                    shop_per_capita_consumption = shop_per_capita_consumption[0]
                    if re.findall('\d+',shop_per_capita_consumption) == []:
                        shop_per_capita_consumption = 0
                    else:
                        shop_per_capita_consumption = int(re.findall('\d+',shop_per_capita_consumption)[0])
                    print('人均消费',shop_per_capita_consumption)
                    
                    shop_address2 = url_data.xpath('//*[@id="basic-info"]/div[2]/a/span/text()')  # 区名
                    # 详细地址
                    shop_address3 = url_data.xpath('//*[@id="basic-info"]/div[2]/span[2]/text()')  # 详细地址
                    if shop_address2 or shop_address3:
                        shop_address = shop_address2[0] + shop_address3[0]
                    else:
                        shop_address = '没有标注'
                    # 拼接地址
                    print('地址:',shop_address)
                    # 区域
                    shop_region = url_data.xpath('//div[@class="breadcrumb"]/a[2]/text()')[0].strip()
                    # shop_region = shop_region[0]
                    print('区域:',shop_region)
                    # 商圈
                    shop_business_district = url_data.xpath('//div[@class="breadcrumb"]/a[3]/text()')[0].strip()
                    # shop_business_district = shop_business_district[0]
                    print('商圈:',shop_business_district)
                    # 品类
                    shop_category = url_data.xpath('//div[@class="breadcrumb"]/a[4]/text()')[0].strip()
                    # shop_category = shop_category[0]
                    print('品类:',shop_category)
                    # 电话
                    shop_telephonenumber = url_data.xpath('//*[@id="basic-info"]/p[1]/span[2]/text()')
                    print(shop_telephonenumber)
                    # shop_telephonenumber = shop_telephonenumber[0]
                    if shop_telephonenumber:
                        shop_telephonenumber = shop_telephonenumber[0]
                    else:
                        shop_telephonenumber = '没有标注'
                    print('电话:',shop_telephonenumber)
                    sql = "INSERT INTO app_dazhongdianping_liren_new_all_data VALUES({0},{1},'{2}',{3},{4},{5},{6},{7},{8},'{9}','{10}','{11}','{12}','{13}','{14}')".format(
                            'NULL', shop_id, str(shop_title), shop_start, shop_review_count,
                            shop_per_capita_consumption, shop_effect,
                            shop_service, shop_surroundings, str(shop_region),
                            str(shop_business_district), str(shop_category), str(shop_address.replace(' ', '')), shop_telephonenumber, '无')
                    print(sql)
                    cursor.execute(sql)
                    connction.commit()
                else:
                    pass
        
            else:
                try:
                    # 使用for循环遍历每家店的名称
                    for i in range(1,len(url)):
                        title = html_data.xpath('//div[@id="shop-all-list"]/ul/li['+ str(i) +']/div[@class="txt"]/div[@class="tit"]/a[1]/@title')
                        # 判断是否是新店名称
                        if title[0] == shop_title:
                            url = html_data.xpath('//div[@id="shop-all-list"]/ul/li['+ str(i) +']/div[@class="txt"]/div[@class="tit"]/a[1]/@href')
                            url_data = get_url_data(url[0])
                            shop_id = html_data.xpath('//div[@id="shop-all-list"]/ul/li['+ str(i) +']/div[@class="txt"]/div[@class="tit"]/a[1]/@data-shopid')
                            shop_id = shop_id[0]
                            print('店铺名称:', shop_title)
                            print('商铺id:',shop_id)
                            # 星级
                            shop_start = url_data.xpath('//div[@class="brief-info"]/span[1]/@class')
                            shop_start = shop_start[0]
                            if shop_start == None:
                                shop_start = 0
                            else:
                                shop_start = int(re.findall('\d+',shop_start)[0])/10
                            print('店铺星级:',shop_start)
                            # 评论数
                            # 评论数
                            try:
                                shop_review_count = url_data.xpath('//div[@class="brief-info"]/span[2]/text()')[0]
                                if shop_review_count == [] or shop_review_count == None:
                                    shop_review_count = 0
                                else:
                                    shop_review_count = int(re.findall('\d+', shop_review_count)[0])
                                # 效果
                                shop_effect = url_data.xpath('//div[@class="brief-info"]/span[4]/text()')
                                shop_effect = shop_effect[0]
                                if re.findall('\d+',shop_effect) == []:
                                    shop_effect = 0
                                else:
                                    if '.' in shop_effect:
                                        shop_effect = re.findall('\d+\.\d+',shop_effect)[0]
                                    else:
                                        shop_effect = int(re.findall('\d+',shop_effect)[0])
                                print('效果',shop_effect)
                                # 环境
                                shop_service = url_data.xpath('//div[@class="brief-info"]/span[5]/text()')
                                shop_service = shop_service[0]
                                if re.findall('\d+',shop_service) == []:
                                    shop_service = 0
                                else:
                                    if '.' in shop_service:
                                        shop_service = re.findall('\d+\.\d+', shop_service)[0]
                                    else:
                                        shop_service = int(re.findall('\d+', shop_service)[0])
                                print('环境:',shop_service)
                                # 服务
                                shop_surroundings = url_data.xpath('//div[@class="brief-info"]/span[6]/text()')
                                shop_surroundings = shop_surroundings[0]
                                if re.findall('\d+',shop_surroundings) == []:
                                    shop_surroundings = 0
                                else:
                                    if '.' in shop_surroundings:
                                        shop_surroundings = re.findall('\d+\.\d+', shop_surroundings)[0]
                                    else:
                                        shop_surroundings = int(re.findall('\d+', shop_surroundings)[0])
                                print('服务:',shop_surroundings)
                            except:
                                shop_review_count = 0
                                # 效果
                                shop_effect = url_data.xpath('//div[@class="brief-info"]/span[3]/text()')
                                shop_effect = shop_effect[0]
                                if re.findall('\d+',shop_effect) == []:
                                    shop_effect = 0
                                else:
                                    if '.' in shop_effect:
                                        shop_effect = re.findall('\d+\.\d+',shop_effect)[0]
                                    else:
                                        shop_effect = int(re.findall('\d+',shop_effect)[0])
                                print('效果',shop_effect)
                                # 环境
                                shop_service = url_data.xpath('//div[@class="brief-info"]/span[4]/text()')
                                shop_service = shop_service[0]
                                if re.findall('\d+',shop_service) == []:
                                    shop_service = 0
                                else:
                                    if '.' in shop_service:
                                        shop_service = re.findall('\d+\.\d+', shop_service)[0]
                                    else:
                                        shop_service = int(re.findall('\d+', shop_service)[0])
                                print('环境:',shop_service)
                                # 服务
                                shop_surroundings = url_data.xpath('//div[@class="brief-info"]/span[5]/text()')
                                shop_surroundings = shop_surroundings[0]
                                if re.findall('\d+',shop_surroundings) == []:
                                    shop_surroundings = 0
                                else:
                                    if '.' in shop_surroundings:
                                        shop_surroundings = re.findall('\d+\.\d+', shop_surroundings)[0]
                                    else:
                                        shop_surroundings = int(re.findall('\d+', shop_surroundings)[0])
                                    print('服务:',shop_surroundings)
                            print('评论数:',shop_review_count)
                            # # 差评数
                            # shop_bad_review_1star = response.xpath('//*[@id="comment"]/h2/span/a[6]/span/text()')
                            # print('1星差评:',shop_bad_review_1star)
                            # if shop_bad_review_1star == None:  # 判断是否为空
                            #     shop_bad_review_1star = 0
                            # else:
                            #     shop_bad_review_1star = int(re.findall('\d+', shop_bad_review_1star)[0])
                            # shop_bad_review_2star = response.xpath('//*[@id="comment"]/h2/span/a[5]/span/text()') # 2星评论
                            # print('2星差评:',shop_bad_review_2star)
                            # if shop_bad_review_2star == None:
                            #     shop_bad_review_2star = 0
                            # else:
                            #     shop_bad_review_2star = int(re.findall('\d+', shop_bad_review_2star)[0])
                            # shop_bad_review = str(shop_bad_review_1star + shop_bad_review_2star)
                            # print('差评数:',shop_bad_review)
                            # 人均消费
                            shop_per_capita_consumption = url_data.xpath('//div[@class="brief-info"]/span[3]/text()')
                            shop_per_capita_consumption = shop_per_capita_consumption[0]
                            if re.findall('\d+',shop_per_capita_consumption) == []:
                                shop_per_capita_consumption = 0
                            else:
                                shop_per_capita_consumption = int(re.findall('\d+',shop_per_capita_consumption)[0])
                            print('人均消费',shop_per_capita_consumption)
                            shop_address2 = url_data.xpath('//*[@id="basic-info"]/div[2]/a/span/text()')  # 区名
                            # 详细地址
                            shop_address3 = url_data.xpath('//*[@id="basic-info"]/div[2]/span[2]/text()')  # 详细地址
                            if shop_address2 or shop_address3:
                                shop_address = shop_address2[0] + shop_address3[0]       
                            else:
                                shop_address = '没有标注'
                                # 拼接地址
                            shop_address.replace(' ', '')
                            print('地址:',shop_address)
                            # 区域  
                            shop_region = url_data.xpath('//div[@class="breadcrumb"]/a[2]/text()')[0].strip()
                            # shop_region = shop_region[0]
                            print('区域:',shop_region)
                            # 商圈
                            shop_business_district = url_data.xpath('//div[@class="breadcrumb"]/a[3]/text()')[0].strip()
                            # shop_business_district = shop_business_district[0]
                            print('商圈:',shop_business_district)
                            # 品类
                            shop_category = url_data.xpath('//div[@class="breadcrumb"]/a[4]/text()')[0].strip()
                            # shop_category = shop_category[0]
                            print('品类:',shop_category)
                            # 电话
                            shop_telephonenumber = url_data.xpath('//*[@id="basic-info"]/p[1]/span[2]/text()')
                            print(shop_telephonenumber)
                            # shop_telephonenumber = shop_telephonenumber[0]
                            if shop_telephonenumber:
                                shop_telephonenumber = shop_telephonenumber[0]
                            else:
                                shop_telephonenumber = '没有标注'
                            sql = "INSERT INTO app_dazhongdianping_liren_new_all_data VALUES({0},{1},'{2}',{3},{4},{5},{6},{7},{8},'{9}','{10}','{11}','{12}','{13}','{14}')".format(
                                'NULL', shop_id, str(shop_title), shop_start, shop_review_count,
                                shop_per_capita_consumption, shop_effect,
                                shop_service, shop_surroundings, str(shop_region),
                                str(shop_business_district), str(shop_category), str(shop_address.replace(' ', '')), shop_telephonenumber, '无')
                            print(sql)
                            cursor.execute(sql)
                            connction.commit()
                        else:
                            pass
                except:
                    print('出错')
        except:
            print('出错')
except:
    print('出错')