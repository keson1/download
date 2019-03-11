#!/usr/bin/python3
#encoding: utf-8
'''
@File: duowantuku_pic.py
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
offset = 30   #偏移量为30的倍数，每次下载30条
def get_gid():
    gid_url = "http://tu.duowan.com/m/tucao?offset=%s&order=created&math=%s" % (offset, math)
    res = requests.get(gid_url)
    lis = json.loads(res.text)["html"]
    soup = BeautifulSoup(lis, "html.parser")
    pics = soup.findAll(attrs={"class": "box"})
    gids = []
    for i in pics:
        pic = i.find(attrs={"target": "_blank"})
        pic_addr = pic.get("href")
        gid = re.findall("\d+", pic_addr)[0]
        gids.append(gid)
        print(gid)
    return gids

def get_pic():
    gids = get_gid()
    picall = {}
    for i in gids:
        url = "http://tu.duowan.com/index.php?r=show/getByGallery/&gid=%s" % i
        res = requests.get(url)
        picinfo = json.loads(res.text)["picInfo"]
        pics = {}
        for pic in picinfo:
            pics[pic["url"]] = pic["add_intro"]
        picall[i] = pics
    print(picall)
    return picall

def down_pic():
    picall = get_pic()
    for gid in picall:
        pics = picall[gid]
        for url in pics:
            try:
                name = pics[url]
                temp = name.split("?")  # 去除名称中特殊字符”？”
                if len(temp) >= 2:
                    name = temp[0]
                path = r'C:\ziyuan\pic\duowantuku\offset%s\%s\%s.jpg' % (offset, gid, name)

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

down_pic()