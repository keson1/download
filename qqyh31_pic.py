#!/usr/bin/python3
#encoding: utf-8
'''
@File: qqyh31_pic.py
@Author:limz
@Time: 2019年03月06日12时
'''
import requests
from bs4 import BeautifulSoup
import os

def down_pic(startpage, endpage):
    urls = get_picurl(startpage, endpage)
    for page in urls:
        for url in urls[page]:
            try:
                title = urls[page][url]
                path = r'C:\ziyuan\pic\qqyh31\page%s\%s.jpg' % (page, title)
                dirname = os.path.dirname(path)
                if os.path.exists(dirname):
                    pass
                else:
                    os.makedirs(dirname)
                res = requests.get(url)
                with open(path, 'ab') as file:
                    file.write(res.content)
                    file.flush()
                    print("receive data，file name:%s, file path: %s" % (title, path))
            except Exception as e:
                print("下载图片出错：%s" % e)

def get_picurl(startpage, endpage):
    urls = {}
    for page in range(startpage, endpage):
        picurl = {}
        url = "https://qq.yh31.com/ka/bx/List_%s.html" % page
        res = requests.get(url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.content.decode(res.encoding), "html.parser")
        pics = soup.findAll(attrs={"border": "0"})
        for i in pics:
            url = "https://qq.yh31.com/" + i.get("src")
            title = i.get("alt")
            picurl[url] = title
        urls[page] = picurl
    print(urls)
    return urls

startpage = 1
endpage = 41
#get_picurl(startpage, endpage)
down_pic(startpage, endpage)