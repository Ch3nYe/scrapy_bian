#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
爬取的是彼岸图网图片
'''
import scrapy
import requests
from scrapy import Request
from lxml import etree
from bian.headers import getheader
import re
import os
import time
from bian.settings import CONCURRENT_REQUESTS
from bian.settings import RETRY_TIMES


class InfoSpider(scrapy.Spider) :

    # 该爬虫的名字
    name = "bian"
    # 起始url
    start_url = 'http://pic.netbian.com/index_885.html'
    # 下一页链接
    next_page = start_url

    # 计数器
    index = 1
    # start_request() 方法用来设置初始请求，可以不进行设置，但本人觉得还有有初始方法更像爬虫

    def start_requests(self):
        # 超时设置为1秒，返回str
        print('''
        +------------------------------+
        |      初始化爬虫进程           |
        |       项目名称：{0}           |
        |      加载爬虫引擎>>>>>>       |
        +------------------------------+       
        '''.format(self.name))
        time.sleep(0.5)
        print("""
            >>>爬虫进程加载完成>>>
            线程数：{0}
            最大重试次数：{1}
            开始爬取>>>>>>
        """.format(CONCURRENT_REQUESTS ,RETRY_TIMES))
        time.sleep(0.5)
        yield Request(self.start_url, headers=getheader())

     #<end start_request>


    # parse 方法通过 Request中的callback调用
    def parse(self, response):
        # 解码respone
        response = response.text
        # etree格式化response
        html = etree.HTML(response)

        # 循环请求主页面上的二十多张图片页url
        for link in html.xpath('//ul[@class="clearfix"]/li/a[@target="_blank"]/@href'):  ## 切取图片主页链接
            #构造完整url
            link = "http://pic.netbian.com" + link
            # 打印日志
            print('当前抓取链接:',self.next_page,' -----' ,link,"当前已爬取 ...[{0}]...张图片".format(self.index-1))
            self.index += 1
            # 在目标图片页面抓取图片img_url 并构造完整
            r_img = etree.HTML(requests.get(link, headers=getheader(), timeout=1).content.decode('gbk'))
            img_link = "http://pic.netbian.com" + r_img.xpath('//div[@class="photo-pic"]/a/img/@src')[0]
            # 截取图片title
            title = r_img.xpath('//div[@class="photo-pic"]/a/img/@title')[0]
            # 去掉非法字符，空格代替
            title = re.sub('[\/:*?"<>|\t]', ' ', title)
            # 截取分类
            img_class = r_img.xpath('//div[@class="loaction"]/span/a/text()')[1]

            # 如果路径不存在，自动创建
            if not os.path.exists('F:/bian/{0}'.format(img_class)):
                # makedird 如果父目录不存在，自行创建父目录，比mkdir好用一点
                os.makedirs('F:/bian/{0}/'.format(img_class))
            # 抓取图片并保存
            with open('F:/bian/{2}/{0}.{1}'.format(title, "jpg", img_class), 'wb') as jpg:
                try:
                    res = requests.get(img_link, headers=getheader(), timeout=1)
                    res.raise_for_status()
                    jpg.write(res.content)
                except:
                    continue

        # 构造下一页url
        self.next_page = "http://pic.netbian.com" + (html.xpath('//a[contains(text(), "下一页")]/@href'))[0]
        if self.next_page is not None:
            # yield 回调parse
            yield Request(self.next_page, callback=self.parse)
    #<end parse>
