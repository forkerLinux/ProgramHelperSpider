#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-09-23 15:52:07
# Project: csdn

from pyspider.libs.base_handler import *
from urllib.parse import urlencode
import re
from datetime import datetime


class Handler(BaseHandler):
    
    crawl_config = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
        }
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://blog.csdn.net', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('.categ > .blog_category > ul > li > a[href^="http"]').items():
               category = each.text()
         
               base_url = each.attr.href.replace('newarticle.html', '')
               for post_fix in ['newarticle.html', 'hotarticle.html']:
                   subcategory = post_fix.replace('.html', '')
                   params = {'category': category, 'subcategory':subcategory}
                   self.crawl(base_url+post_fix, callback=self.search_page, save=params)

    @config(priority=1)
    def search_page(self, response):
        pages = response.doc('.page_nav > a').items()
        last_page_url = list(pages)[-1].attr.href
        m = re.findall('\d+', last_page_url)
        total = int(m[0])
        for i in range(1, total+1):
            params = {'page': str(i)}
            url = response.url + '?&' + urlencode(params)
            self.crawl(url, callback=self.list_page, save=response.save)


    @config(priority=2)
    def list_page(self, response):
        for each in response.doc('dd > .tracking-ad > a').items():
            self.crawl(each.attr.href, callback=self.detail_page, save=response.save)


    @config(priority=3)
    def detail_page(self, response):
        tags = list(response.doc('.article_l a').items())
        tag_list = [item.text() for item in tags]
        content = response.doc('.article_content').text()

        time_str = response.doc('.link_postdate').text()
        create_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        fetch_time = datetime.now()
        create_time = int(create_time.timestamp())
        fetch_time = int(fetch_time.timestamp())

        return {
            "url": response.url,
            "title": response.doc('h1 a').text(),
            'tags':  tag_list,
            'category': response.save.get('category'),
            'subcategory': response.save.get('subcategory'),
            'content': content,
            'fetch_time': fetch_time,
            'create_time': create_time,
        }

