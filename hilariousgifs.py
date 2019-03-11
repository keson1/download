#!/usr/bin/python3
#encoding: utf-8
'''
@File: hilariousgifs.py
@Author:limz
@Time: 2019年03月05日22时
'''
import requests
from bs4 import BeautifulSoup
import os

def down_gif(category, startpage, endpage):
    urls = get_gifurl(category, startpage, endpage)
    for page in urls:
        for url in urls[page]:
            try:
                res = requests.get(url)
                soup = BeautifulSoup(res.text, "html.parser")
                title = soup.find(attrs={"property": "og:title"}).get("content").split("|")[0].replace("/", "\/")
                temp = title.split("?")  # 去除名称中特殊字符”？”
                if len(temp) >= 2:
                    title = temp[0]
                gif_url = soup.find(attrs={"property": "og:url"}).get("content")
                path = r'E:\ziyuan\gif\hilariousgifs\%s\page%s\%s.gif' % (category, page, title)
                dirname = os.path.dirname(path)
                if os.path.exists(dirname):
                    pass
                else:
                    os.makedirs(dirname)
                res = requests.get(gif_url)
                with open(path, 'ab') as file:
                    file.write(res.content)
                    file.flush()
                    print("receive data，file name:%s, file path: %s" % (title, path))
            except Exception as e:
                print("下载图片出错：%s" % e)

def get_gifurl(category, startpage, endpage):
    urls = {}
    for page in range(startpage, endpage):
        gifurl = []
        url = "http://www.hilariousgifs.com/category/hilariousgifs/%s/page/%s/" % (category, page)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        gifs = soup.findAll(attrs={"class": "post"})
        for i in gifs:
            url = i.a.get("href")
            gifurl.append(url)
        urls[page] = gifurl
    print(urls)
    return urls

category = "funny-hilariousgifs" #分类
startpage = 3
endpage = 10
down_gif(category, startpage, endpage)