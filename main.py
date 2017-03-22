# __author__ = 'kohna'
# -*- coding:utf-8 -*-
# -*- date : 2015-12-31 -*-
# -*- timr : 17:10  -*-

import os
import time
import codecs
import requests
import html2text
import logging
import lxml.html as html
from time import sleep

mon = time.strftime('%Y%m', time.localtime())
day = time.strftime('%Y%m%d', time.localtime())
logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=day + ".log",
                    filemode='a+',
                    level=logging.WARNING,
                    )


class Getls:
    def __init__(self):
        tem = ""
        try:
            os.path.exists("zhihu") or os.mkdir("zhihu")  # 如果不存在则创建
        except os.error, e:
            logging.error("DIR error" + e)

        self.prod = os.getcwd() + '/zhihu/'  # 构造路径
        os.chdir(self.prod)  # 进入知乎文件夹
        os.path.exists("img") or os.mkdir("img")  # 创建img文件夹
        self.htex = html2text.HTML2Text()  # 初始化H2T对象
        self.see = requests.Session()  # 初始化 Session
        self.see.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
        try:
            tem = self.see.get("http://daily.zhihu.com/")
        except requests.RequestException.args, e:
            logging.error("Get list error " + e)
        try:

            tem = html.document_fromstring(tem.content)
        except html.etree.Error.args, e:
            logging.error("Error:" + e)
        self.tit = tem.xpath("//span[@class='title']/text()")  # 抓了标题
        self.url = tem.xpath("//a[@class='link-button']/@href")  # 连接按钮
        self.smmu = ""

    def getwoi(self):
        for iurl in self.url:
            iurl = "http://daily.zhihu.com" + iurl  # 文章标题
            snum = str((filter(lambda x: x.isdigit(), iurl)))  # 提取文章id
            imgd = "img/" + snum
            fp = codecs.open(snum + ".md", "w+", "UTF-8")
            try:
                temp = self.see.get(iurl)
            except requests.ConnectionError, e:
                logging.error("error by ", e)
            temp = html.document_fromstring(temp.content)
            auth = temp.xpath("//span[@class='author']/text()")  # 作者
            imgt = temp.xpath("//img[@class='content-image']")  # 图片列表
            tits = temp.xpath("//h2[@class='question-title']/text()")
            if len(auth) > 0:
                auth = auth[0]
            if len(tits) > 0:
                tits = tits[0]
            if len(imgt) > 0:  # 判断是否有图片
                os.path.exists(imgd) or os.mkdir(imgd)  # 创建文件夹，按文章号码来创建
                self.doimg(imgt, imgd)  # 下载图片，imgt 是图片地址列表,snum 是文件夹
            cont = temp.xpath("//div[@class='content']")
            cont = self.htex.handle(html.tostring(cont[0]))
            self.smmu = """<!--\n    author: %s\n    head: %s\n    date: %s\n    title: %s\n    tags: GitBlog\n    category: zhihu\n    status: publish\n    summary:%s\n-->\n""" % (
                auth, 'none', time.asctime(), tits, cont[:120].replace("\n", "") + "...",)
            yuan = "\n[打开知乎原文](%s)".decode("UTF-8") % iurl
            sx = self.smmu + cont + yuan
            fp.write(sx)
            fp.close()
            sleep(5)

    def doimg(self, imgl, imgd):  # 下载图片并替换地址
        os.chdir(imgd)  # 转到该目录去
        img = ""
        for iur in range(len(imgl)):
            url = imgl[iur].attrib['src']
            while True:  # 下载图片
                flag = 1
                try:
                    img = self.see.get(url, stream=True)
                except requests.exceptions.ConnectionError:  # 如果下载不成功
                    flag = 0
                if flag:
                    break
                else:
                    continue
            with open(str(iur) + ".jpg", 'wb') as fd:
                for imgstr in img.iter_content():
                    fd.write(imgstr)  # 写入图片
                fd.close()
            imgl[iur].attrib['src'] = imgd + "/" + str(iur) + ".jpg"
        os.chdir(self.prod)  # 回到目录


# os.chdir("../phpStudy/WWW/blog")
x = Getls()
x.getwoi()
