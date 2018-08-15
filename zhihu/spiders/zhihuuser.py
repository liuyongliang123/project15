# -*- coding: utf-8 -*-
import scrapy
import re
import json
from ..items import ZhihuItem
class ZhihuuserSpider(scrapy.Spider):
    name = 'zhihuuser'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    # 首先获取其实的大v名称

    start_user = "excited-vczh"
    user_url = "https://www.zhihu.com/api/v4/members/{user}?include={include}"

    user_query = "allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics"
    # "allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics"

    #  每个大v关注的列表的接口
    follows_url = "https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}"

    follows_query ="data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics"

    def start_requests(self):
        # url = "https://www.zhihu.com/api/v4/members/iwoba?include=allow_message%2Cis_followed%2Cis_following%2Cis_org%2Ci"

        yield scrapy.Request(self.user_url.format(user = self.start_user,include = self.user_query),callback= self.parse_user)


        yield scrapy.Request(self.follows_url.format(user = self.start_user,include = self.follows_query,offset=0,limit =20),callback=self.parse_follows)



    def parse_user(self, response):
        result = json.loads(response.text)
        item = ZhihuItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item

        # 递归的进行爬取
        yield scrapy.Request(self.follows_url.format(user=result.get("url_token"),include=self.follows_query,limit=20,offset=0),callback=self.parse_follows)

    def parse_follows(self,response):
        # print(len(response.text),"--------------------------------")

        results = json.loads(response.text)

        if "data" in results.keys():
            for result in results.get("data"):
                yield scrapy.Request(self.user_url.format(user=result.get("url_token"),include=self.user_query),callback=self.parse_user)


            if "paging" in results.keys() and results.get("paging").get("is_end")==False:
                next_page = results.get("paging").get("next")
                yield scrapy.Request(next_page,self.parse_follows)





