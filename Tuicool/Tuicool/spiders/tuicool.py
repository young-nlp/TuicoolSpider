# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
from Tuicool.items import TuicoolItem

class TuicoolSpider(scrapy.Spider):
    name = 'Tuicool'
    host = 'http://www.tuicool.com/'
    start_urls = ['http://www.tuicool.com/ah/0/1?lang=1']

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "http://www.tuicool.com/login"
    }

    def start_requests(self):
        return [Request('http://www.tuicool.com/login',meta={'cookiejar':1},callback=self.pre_login)]

    def pre_login(self,response):
        print "Pre Login..."
        authenticity_token = Selector(response).xpath('//input[@name="authenticity_token"]/@value').extract()[0]
        # print authenticity_token
        return [FormRequest.from_response(response,
                                          meta={'cookiejar':response.meta['cookiejar']},
                                          headers=self.headers,
                                          formdata={
                                              'utf8':'✓',
                                              'authenticity_token':authenticity_token,
                                              'email':'814701007@qq.com',
                                              'password':'snmnmfku7',
                                              'remember':'1'
                                           },
                                          callback=self.my_login,
                                          dont_filter=True
                                           )]

    def my_login(self,response):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self, response):
        articles = Selector(response).xpath('//*[@class="aricle_item_info"]')
        print "共有%s篇文章" % len(articles)
        for article in articles:
            item = TuicoolItem()
            title = article.xpath('div[@class="title"]/a/text()').extract()[0].encode('utf-8')
            link = self.host+article.xpath('div[@class="title"]/a/@href').extract()[0].encode('utf-8')
            source = article.xpath('div[@class="tip"]/span[1]/text()').extract()[0].strip().encode('utf-8')
            create_time = article.xpath('div[@class="tip"]/span[3]/text()').extract()[0].strip().encode('utf-8')
            # print title,link,source,create_time
            item['title'] = title
            item['link'] = link
            item['publish'] = source
            item['create_time'] = create_time
            yield item

        nextpage = Selector(response).xpath('//*[@class="next"]/a/@href').extract()
        if len(nextpage) != 0:
            next_url = self.host+nextpage[0]
            print "=====================next=========================="
            yield self.make_requests_from_url(next_url)


