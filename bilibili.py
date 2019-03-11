#!/usr/bin/python3
#encoding: utf-8
'''
@File: bilibili.py
@Author:limz
@Time: 2019年02月23日22时
'''

import os
import requests
from bs4 import BeautifulSoup
import re
import json
import sys
from threading import Thread
import threading
import queue
import time

class bilibili():
    def __init__(self,page_start, page_end, keyword):
        self.page_start = int(page_start)      #下载起始页
        self.page_end = int(page_end)          #下载结束页，不下在结束页。如下载第一页，设置为：1，2。
        self.keyword = keyword                 #搜索关键字
        self.pages = [1]                       #下载页列表
        self.right = 0                         #成功个数
        self.error = 0                         #失败个数
        if page_start < page_end:
            self.pages = list(range(page_start, page_end))
        else:
            print("页码输入有误,退出！")
            sys.exit(1)

    def get_aid(self):
        # 获取视频的aid即播放地址
        aids_allpage = {}  #指定页数的aid
        try:
            for page in self.pages:
                    aids = {}  # 某一页的aid
                    url = "https://search.bilibili.com/all?keyword=%s&order=totalrank&duration=1&tids_1=0&page=%s" % (self.keyword, int(page))
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text, "html.parser")
                    videos = soup.findAll(attrs={"class": "headline clearfix"})
                    for i in videos:
                        video = i.find(attrs={"class": "title"})
                        addr_origin = video.get("href")  # 播放地址url
                        temp = addr_origin.split("av")[1]
                        aid = temp[0:8]  # 截取aid
                        title = video.get("title")  # 视频名称
                        aids[aid] = title
                    aids_allpage[page] = aids
            print(aids_allpage)
            return aids_allpage  # 返回指定页数视频名称和aid的字典
        except Exception as e:
            print("获取aid时报错" + str(e))

    def get_downloadurl(self):
        # 获取视频下载地址
        aids_allpage = self.get_aid()
        videos_allpage = {}
        try:
            for page in aids_allpage:
                videos = {}
                for aid in aids_allpage[page]:
                    try:
                        url = "https://www.kanbilibili.com/video/av" + aid  # 视频播放地址
                        res = requests.get(url)
                        soup = BeautifulSoup(res.text, "html.parser")
                        video = soup.findAll(attrs={"class": "content scroll"})[1]
                        cid_str = video.find(attrs={"target": "_blank"}).get("href")
                        cid = re.findall("\d+", cid_str)[0]  # 截取视频cid用于生成下载链接
                        pre_downloadurl = "https://www.kanbilibili.com/api/video/%s/download?cid=%s" % (aid, cid)  # 视频下载链接接口地址
                        downurl_res = requests.get(pre_downloadurl)
                        downloadurl = json.loads(downurl_res.text)["data"]["durl"][0]["url"]  # 下载链接
                        videos[downloadurl] = aids_allpage[page][aid]  # 视频名称和下载地址字典
                    except Exception as e:
                        print("获取下载地址时报错：" + str(e))
                videos_allpage[page] = videos #指定页数视频的下载地址字典
            print(videos_allpage)
            return videos_allpage  # 返回指定页数视频的下载地址字典
        except Exception as e:
            print("获取下载列表时报错：" + str(e))

    def do_load_media(self, q):
        #获取下载队列信息，执行下载
        thread = threading.current_thread()
        while True:
            if q.empty():
                print("线程：[%s]，下载队列为空" % thread.getName())
                break
            else:
                msg = q.get()
            name = msg["name"]
            temp = name.split("?")  #去除特殊字符”？”
            if len(temp) >= 2:
                name = temp[0] + temp[1]
            url = msg["url"]
            errorstr = 'cn-zjhz2-wasu-acache'
            turestr = 'http://upos-hz-mirrorks3u.acgvideo.com/upgcxcode'
            if errorstr in url:
                url = turestr + url.split("upgcxcode")[1]
            page = msg["page"]
            path = r'C:\ziyuan\bilibili\%s\page%s\%s.flv' % (self.keyword, page, name)
            print("线程：[%s],准备下载-%s:%s,保存路径为：%s" % (thread.getName(), name, url, path))
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.3.2.1000 Chrome/30.0.1599.101 Safari/537.36"}
                pre_content_length = 0
                # 循环接收视频数据
                count = 0
                while True:
                    if count > 3:
                        break
                    #判断目录是否存在，否则创建
                    dirname = os.path.dirname(path)
                    if os.path.exists(dirname):
                        pass
                    else:
                        os.makedirs(dirname)
                     # 若文件已经存在，则断点续传，设置接收来需接收数据的位置
                    if os.path.exists(path):
                        headers['Range'] = 'bytes=%d-' % os.path.getsize(path)
                    res = requests.get(url, stream=True, headers=headers)

                    content_length = int(res.headers['content-length'])
                    # 若当前报文长度小于前次报文长度，或者已接收文件等于当前报文长度，则可以认为视频接收完成
                    if content_length < pre_content_length or (
                            os.path.exists(path) and os.path.getsize(path) == content_length):
                        break
                    pre_content_length = content_length

                    # 写入收到的视频数据
                    with open(path, 'ab') as file:
                        file.write(res.content)
                        file.flush()
                        print('线程：[%s],receive data，file size : %d   total size:%d' % (thread.getName(), os.path.getsize(path), content_length))
                    count += 1
                    self.right += 1
            except Exception as e:
                print('ERROR:线程：[%s],此视频下载出错，名称是%s，错误信息是%s，已跳过' % (thread.getName(), str(name), e))
                self.error += 1
                pass

    def load_media(self):
        threads = []
        q = queue.Queue()
        videos_allpage = self.get_downloadurl()   #视频信息
        for page in videos_allpage:
            videos = videos_allpage[page]
            for url in videos:
                msg = {"name": videos[url], "url": url, "page": page}
                q.put(msg)            #加入下载对列
        for i in range(3):
            t = Thread(target=self.do_load_media, args=(q, ))     #执行下载线程
            threads.append(t)
        for t in threads:
            t.start()
            time.sleep(1)
        for t in threads:
            t.join()
        print("下载完成！成功：%s, 失败：%s" % (self.right, self.error))

    def main(self):
        self.load_media()

if __name__ == '__main__':
    page_start = 1  #下载起始页
    page_end = 2    #下载结束页，不下载结束页。如下载第一页，设置为：1，2。
    keyword = "月下瓜田一只猹"    #搜索关键字
    bilibili(page_start, page_end, keyword).main()
