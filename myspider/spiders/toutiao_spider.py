# coding:utf-8

import scrapy
import urllib
import re
import json
import HTMLParser
from datetime import datetime
from scrapy import Selector
from myspider.items import ToutiaoItem

class ToutiaoSpider(scrapy.Spider):
    name = "toutiao"
    urltemplate = "http://www.toutiao.com/c/user/article/?page_type=1&user_id={userid}&max_behot_time=0&count=20&as=A1B5382B95E4C02&cp=58B5747C80723E1"
    referer = "http://www.toutiao.com"

    def __init__(self, date, url_file='./conf/toutiao_urls'):
        self.date = date
        self.prefix = "http://www.toutiao.com"

        self.urls = dict()
        with open(url_file, 'r') as fp:
            for line in fp:
                items = line.strip().split('\t')
                self.urls[items[0]] = [items[1], items[2]]

    def start_requests(self):
        for tag, values in self.urls.iteritems():
            #if '1' == values[2]:
            #    continue
            request = scrapy.Request(url=self.urltemplate.format(userid=values[1]), headers={'Referer':self.referer}, callback=self.parse)
            request.meta['tag'] = tag
            request.meta['desc'] = values[0]
            request.meta['step'] = 1
            yield request

    def parse(self, response):
        step = response.meta['step']
        if 1 == step:
            myheader = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, sdch',
                'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
                'Referer':None,
                'Host':'www.toutiao.com',
                'Connection':'keep-alive',
                'Upgrade-Insecure-Requests':1,
                'Cookie':'uuid="w:709328a5ab3c420b8d385fc65f1e6822"; UM_distinctid=15cc070609e5a0-0619158ae2b289-3060750a-fa000-15cc070609f662; login_flag=bc8cc0b99c768c8cfd15e29f59861ab8; sid_guard="81491b3b1f8261b69b9931bcc5c4eacc|1497886884|2592000|Wed\054 19-Jul-2017 15:41:24 GMT"; sessionid=81491b3b1f8261b69b9931bcc5c4eacc; sid_tt=81491b3b1f8261b69b9931bcc5c4eacc; csrftoken=caf4f44a58306e4f5a39367a68146d8e; sso_login_status=0; tt_webid=6433333624234116610; __tasessionId=cot4qw9f91497969757341; _ga=GA1.2.1374535477.1497877209; _gid=GA1.2.1310737854.1497877209; CNZZDATA1259612802=33422345-1497876284-%7C1497968084',
                'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

            #with open('./test/%s.html' % response.meta['tag'], 'w') as fp:
            #    fp.write(response.body)

            items = json.loads(response.body)
            data = items['data']
            for item in data:
                time = self.date_convert(item['behot_time'])
                if time >= self.date and 'article' == item['article_genre']:
                    url = item['display_url']
                    print url
                    request = scrapy.Request(url=url, headers=myheader, callback=self.parse_item)
                    request.meta['title'] = item['title']
                    request.meta['desc'] = response.meta['desc']
                    request.meta['url'] = url
                    request.meta['date'] = time
                    request.meta['cover'] = item['image_url']
                    yield request
                
    def parse_item(self, response):
        #with open('./test/%s.html' % response.meta['title'], 'w') as fp:
        #    fp.write(response.body)

        imgtemplate = '<img src="{src}">'
        item = ToutiaoItem()
        item['title'] = response.meta['title']
        item['cover'] = response.meta['cover']
        item['tag'] = response.meta['desc']
        item['date'] = response.meta['date']
        item['url'] = response.meta['url']

        item['content'] = ''
        tags = Selector(text=response.body).css('.article-content p')
        for tag in tags:
            imgtags = tag.xpath('.//img/@src').extract()
            if len(imgtags):
                for imgtag in imgtags:
                    item['content'] += imgtemplate.format(src=imgtag) + '\n'
                    #print imgtemplate.format(src=imgtag)
            else:
                tt = "".join(tag.xpath('.//text()').extract()).strip()
                if len(tt):
                    item['content'] += '<p>' + tt + '</p>\n'
                    #print tt
        
        return item if len(item['content']) else None

    # 将unix时间戳转换为格式20170101
    def date_convert(self, from_date):
        return datetime.strftime(datetime.fromtimestamp(from_date), '%Y%m%d')
