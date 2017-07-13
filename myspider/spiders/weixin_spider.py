# coding:utf-8

import scrapy
import urllib
import re
import json
import HTMLParser
from datetime import datetime
from scrapy import Selector
from myspider.items import WeixinItem

class WeixinSpider(scrapy.Spider):
    name = "weixin"
    urltemplate = "http://weixin.sogou.com/weixin?type=1&s_from=input&query={query}&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=11204&sst0=1497276915288&lkt=0%2C0%2C0"

    def __init__(self, date, url_file='./conf/weixin_urls'):
        self.date = date
        self.prefix = "http://mp.weixin.qq.com"

        self.urls = dict()
        with open(url_file, 'r') as fp:
            for line in fp:
                items = line.strip().split('\t')
                self.urls[items[0]] = [items[1], items[2], items[3]]

    def start_requests(self):
        for tag, values in self.urls.iteritems():
            if '1' == values[2]:
                continue
            request = scrapy.Request(url=self.urltemplate.format(query=urllib.quote(values[1])), callback=self.parse)
            request.meta['tag'] = tag
            request.meta['desc'] = values[0]
            request.meta['step'] = 1
            yield request

    def parse(self, response):
        step = response.meta['step']
        if 1 == step:
            sel = Selector(text=response.body)
            url = sel.css('.news-list2 li:nth-of-type(1) .tit a').xpath('@href').extract()[0]
            #print url

            request = scrapy.Request(url=url, callback=self.parse)
            request.meta['tag'] = response.meta['tag']
            request.meta['desc'] = response.meta['desc']
            request.meta['step'] = 2
            yield request
        elif 2 == step:
            html_parser = HTMLParser.HTMLParser()

            with open('./out/list/%s.html' % response.meta['tag'], 'w') as fp:
                fp.write(response.body)

            sel = Selector(text=response.body).xpath('//script[@type]/text()').extract()
            text = sel[3]

            pattern = re.compile(ur"var msgList = {(?P<json>.*)}")
            try:
                content = '{' + pattern.search(text).group('json') + '}'
            except AttributeError:
                input("请复制以上链接，手动输入验证码后按1: ")
                return
            c_json = json.loads(content)
            for item in c_json['list']:
                time = self.date_convert(item['comm_msg_info']['datetime'])
                if time >= self.date:
                    url = html_parser.unescape(item['app_msg_ext_info']['content_url'])
                    request = scrapy.Request(url=self.prefix + url, callback=self.parse_item)
                    request.meta['title'] = item['app_msg_ext_info']['title']
                    request.meta['cover'] = item['app_msg_ext_info']['cover']
                    request.meta['desc'] = response.meta['desc']
                    request.meta['tag'] = response.meta['tag']
                    request.meta['url'] = self.prefix + url
                    request.meta['date'] = time
                    yield request

                    if len(item['app_msg_ext_info']['multi_app_msg_item_list']):
                        for tt in item['app_msg_ext_info']['multi_app_msg_item_list']:
                            url = html_parser.unescape(tt['content_url'])
                            request = scrapy.Request(url=self.prefix + url, callback=self.parse_item)
                            request.meta['title'] = tt['title']
                            request.meta['cover'] = tt['cover']
                            request.meta['desc'] = response.meta['desc']
                            request.meta['tag'] = response.meta['tag']
                            request.meta['url'] = self.prefix + url
                            request.meta['date'] = time
                            yield request
        
    def parse_item(self, response):
        #with open('./out/html/%s.html' % response.meta['title'], 'w') as fp:
        #    fp.write(response.body)

        imgtemplate = '<img src="{src}">'
        item = WeixinItem()
        item['title'] = response.meta['title']
        item['cover'] = response.meta['cover']
        item['tag'] = response.meta['desc']
        item['date'] = response.meta['date']
        item['url'] = response.meta['url']

        item['content'] = ''
        tags = Selector(text=response.body).css('#js_content p')
        for tag in tags:
            imgtags = tag.xpath('.//img/@data-src').extract()
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
