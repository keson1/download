#!/usr/bin/python3
#encoding: utf-8
'''
@File: qqyh31_gif.py
@Author:limz
@Time: 2019年03月11日12时
'''
import requests
from bs4 import BeautifulSoup
import os

def down_gif(startpage, endpage, storepath):
    urls = get_gifurl(startpage, endpage)
    for page in urls:
        for url in urls[page]:
            try:
                title = urls[page][url]
                path = storepath.format(page, title)
                #path = r'C:\ziyuan\gif\qqyh31\page%s\%s.gif' % (page, title)
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

def get_gifurl(startpage, endpage):
    urls = {}
    for page in range(startpage, endpage):
        gifurl = {}
        url = "https://qq.yh31.com/ka/zr/List_%s.html" % page
        res = requests.get(url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.content.decode(res.encoding), "html.parser")
        gifs = soup.findAll(attrs={"border": "0"})
        for i in gifs:
            url = "https://qq.yh31.com/" + i.get("src")
            title = i.get("alt")
            gifurl[url] = title
        urls[page] = gifurl
    print(urls)
    return urls

startpage = 81
endpage = 141
storepath = r'E:\ziyuan\gif\qqyh31\page{0}\{1}.gif'
#get_gifurl(startpage, endpage)
down_gif(startpage, endpage, storepath)