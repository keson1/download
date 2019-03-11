#!/usr/bin/python3
#encoding: utf-8
'''
@File: duowantuku.py
@Author:limz
@Time: 2019年02月26日20时
'''
import random
import requests
import re
import json
from bs4 import BeautifulSoup
import os

math = random.random()
offset = 60   #偏移量为30的倍数，每次下载30条
def get_gid():
    gid_url = "http://tu.duowan.com/m/bxgif?offset=%s&order=created&math=%s" % (offset, math)
    res = requests.get(gid_url)
    lis = json.loads(res.text)["html"]
    soup = BeautifulSoup(lis, "html.parser")
    gifs = soup.findAll(attrs={"class": "box"})
    gids = []
    for i in gifs:
        gif = i.find(attrs={"target": "_blank"})
        gif_addr = gif.get("href")
        #print(gif_addr)
        gid = re.findall("\d+", gif_addr)[0]
        gids.append(gid)
        #print(gid)
    return gids

def get_gif():
    gids = get_gid()
    gifall = {}
    for i in gids:
        url = "http://tu.duowan.com/index.php?r=show/getByGallery/&gid=%s" % i
        res = requests.get(url)
        picinfo = json.loads(res.text)["picInfo"]
        gifs = {}
        for pic in picinfo:
            gifs[pic["url"]] = pic["add_intro"]
        gifall[i] = gifs
    #print(gifall)
    return gifall

def down_gif():
    gifall = get_gif()
    for gid in gifall:
        gifs = gifall[gid]
        for url in gifs:
            try:
                name = gifs[url]
                temp = name.split("?")  # 去除名称中特殊字符”？”
                if len(temp) >= 2:
                    name = temp[0]
                path = r'C:\ziyuan\duowantuku\offset%s\%s\%s.gif' % (offset, gid, name)

                # 判断目录是否存在，否则创建
                dirname = os.path.dirname(path)
                if os.path.exists(dirname):
                    pass
                else:
                    os.makedirs(dirname)

                 #下载图片
                res = requests.get(url)
                with open(path, 'ab') as file:
                    file.write(res.content)
                    file.flush()
                    print("receive data，file name:%s, file path: %s" % (name, path))

            except Exception as e:
                print("下载图片出错：%s" % e)

down_gif()