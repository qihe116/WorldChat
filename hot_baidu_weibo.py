from urllib import request, parse
import time
from bs4 import BeautifulSoup
import random
import json
import pandas as pd
from lxml import etree
import requests
import pymongo
from datetime import datetime
# from loguru import logger

# logger.add('hot.log')

collection_baidu = pymongo.MongoClient("mongodb://192.168.230.128:27017/")['hot_news']['baidu']
collection_weibo = pymongo.MongoClient("mongodb://192.168.230.128:27017/")['hot_news']['weibo']


class DownNews:
    def __init__(self):
        # self.baidu_url = 'https://www.baidu.com/'
        self.baidu_url = 'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd=%E5%A4%9A%E8%87%82%E8%80%81%E8%99%8E%E6%9C%BA&oq=%25E5%25A4%259A%25E5%25B1%2582%25E6%2584%259F%25E7%259F%25A5%25E6%259C%25BA&rsv_pq=e322ae62002a9c41&rsv_t=5caf2by%2FyZV3mi4lcLuhJIirqkmLay6cU3RjpvFYBhOeeVROWOreOSELf6M&rqlang=cn&rsv_dl=tb&rsv_enter=0&rsv_btype=t&inputT=2721&rsv_sug3=73&rsv_sug1=22&rsv_sug7=100&rsv_sug2=0&rsv_sug4=5067'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
        self.top_baidu_url = 'https://top.baidu.com/board?tab=realtime'
        self.top_baidu_url_movie = 'https://top.baidu.com/board?tab=movie'
        self.BASE_URL = 'https://s.weibo.com'

    def baidu_hot_search(self):
        req = request.Request(url=self.baidu_url, headers=self.headers)
        response = request.urlopen(req, timeout=2)
        content = response.read().decode('utf8')
        # with open('data/test.html', 'w', encoding='utf8') as f:
        #     f.write(content)
        soup = BeautifulSoup(content, 'lxml')
        # div = soup.find_all('div', class_='s-hotsearch-wrapper')
        # div = soup.find_all('div', class_='toplist1-tr_4kE4D')
        # div = soup.find_all('div', class_='cr-offset ')
        # print(div)
        # for i in div:
        #     div1 = i.find_all('div')
        #     print(len(div1))
        #     for j in div1:
        #         div2 = j.find_all('div')
        a = soup.find_all('div')
        print(a)
        for i in a:
            print(i.attrs)

    # 百度热搜
    def baidu_hot_search_top(self):
        req = request.Request(url=self.top_baidu_url, headers=self.headers)
        response = request.urlopen(req, timeout=2)
        content = response.read().decode('utf8')
        soup = BeautifulSoup(content, 'lxml')
        # titles, hot_indices = [], []
        res_json = {'day': time.strftime("%Y%m%d", time.localtime(time.time())),
                    'time': time.strftime("%H:%M:%S", time.localtime(time.time()))}
        res_json_title = {'day': time.strftime("%Y%m%d", time.localtime(time.time())),
                    'time': time.strftime("%H:%M:%S", time.localtime(time.time()))}
        div = soup.find_all('div', {'class': 'category-wrap_iQLoo'})
        for idx, item in enumerate(div):
            title_tag = item.find('div', {'class': 'c-single-text-ellipsis'})
            desc = item.find('div', {'class': 'hot-desc_1m_jR'})
            # img = item.find('div', {'class': 'index_1Ew5p'}).find('img')
            if title_tag and desc:
                # if img:
                #     img_url = img.get('src')
                # else:
                #     img_url = ''
                # res_json.append(title_tag.text.strip())
                # res_json[idx] = {'title': title_tag.text.strip(),
                #                  'desc': desc.text.strip().replace('查看更多>', '')}
                res_json['title_' + str(idx)] = title_tag.text.strip()
                res_json_title['title_' + str(idx)] = title_tag.text.strip()
                res_json['desc' + str(idx)] = desc.text.strip().replace('查看更多>', '')
                # hot_indices.append(hot_index_tag.text.strip())
        return res_json, res_json_title

    # weibo热搜
    def getHTML(self, url):
        ''' 获取网页 HTML 返回字符串

        Args:
            url: str, 网页网址
        Returns:
            HTML 字符串
        '''
        # Cookie 有效期至2023-02-10
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
            'Cookie': 'SUB=_2AkMVWDYUf8NxqwJRmP0Sz2_hZYt2zw_EieKjBMfPJRMxHRl-yj9jqkBStRB6PtgY-38i0AF7nDAv8HdY1ZwT3Rv8B5e5; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFencmWZyNhNlrzI6f0SiqP'
        }
        response = requests.get(url, headers=headers)
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding if response.apparent_encoding != 'ISO-8859-1' else 'utf-8'
        return response.text

    # weibo热搜
    def parseHTMLByXPath(self, content):
        html = etree.HTML(content)

        titles = html.xpath(
            '//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/text()')
        hrefs = html.xpath(
            '//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/@href')
        hots = html.xpath(
            '//tr[position()>1]/td[@class="td-02"]/a[not(contains(@href, "javascript:void(0);"))]/../span/text()')
        titles = [title.strip() for title in titles]
        hrefs = [self.BASE_URL + href.strip() for href in hrefs]
        hots = [int(hot.strip().split(' ')[-1])
                for hot in hots]  # 该处除了热度还会返回大致分类，形如 `剧集 53412536`，前为分类，后为热度

        correntRank = {}
        for i, title in enumerate(titles):
            correntRank[title] = {'href': hrefs[i], 'hot': hots[i]}

        res_json = {'day': time.strftime("%Y%m%d", time.localtime(time.time())),
                    'time': time.strftime("%H:%M:%S", time.localtime(time.time()))}
        for i, j in enumerate(correntRank.keys()):
            res_json['title_' + str(i + 1)] = j

        return res_json

    # weibo热搜
    def weibo_hot_search(self):
        url = '/top/summary'
        content = self.getHTML(self.BASE_URL + url)
        correntRank = self.parseHTMLByXPath(content)
        return correntRank

    def get_when_1h_v2(self):
        hot_baidu = self.baidu_hot_search_top()[0]
        collection_baidu.insert_one(hot_baidu)

        hot_weibo = self.weibo_hot_search()
        collection_weibo.insert_one(hot_weibo)



if __name__ == '__main__':
    dn = DownNews()
    dn.get_when_1h_v2()

