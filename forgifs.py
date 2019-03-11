#!/usr/bin/python3
#encoding: utf-8
'''
@File: forgifs.py
@Author:limz
@Time: 2019年03月11日22时
'''
import requests
from bs4 import BeautifulSoup
import os

category = "Funny" #分类  Cats , Cool, Funny, Animals, Sports, Dogs
startpage = 1
endpage = 11
storepath = r'E:\ziyuan\gif\forgifs\{0}\page{1}\{2}.gif'
def down_gif():
    urls = get_gifurl()
    for page in urls:
        for url in urls[page]:
            try:
                url = "http://forgifs.com" + url
                res = requests.get(url)
                soup = BeautifulSoup(res.text, "html.parser")
                title = soup.find(attrs={"class": "giDescription"}).text.strip('\r\n')
                temp = title.split("?")  # 去除名称中特殊字符”？”
                if len(temp) >= 2:
                    title = temp[0]
                gif_url = soup.find(attrs={"id": "gsImageView"}).img.get("src")
                gif_url = "http://forgifs.com" + gif_url
                path = storepath.format(category, page, title)
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

def get_gifurl():
    urls = {}
    for page in range(startpage, endpage):
        gifurl = []
        url = "http://forgifs.com/gallery/v/%s/?g2_page=%s" % (category, page)
        res = requests.get(url)
        #print(res.status_code)
        soup = BeautifulSoup(res.text, "html.parser")
        gifs = soup.findAll(attrs={"class": "giItemCell"})
        for i in gifs:
            #print(i)
            url = i.a.get("href")
            gifurl.append(url)
        urls[page] = gifurl
    print(urls)
    return urls

#get_gifurl()
down_gif()