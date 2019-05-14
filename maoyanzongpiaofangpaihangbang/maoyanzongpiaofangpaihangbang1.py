# -*- coding:utf-8 -*-
"""
# @PROJECT: study_practice
# @Author: admin
# @Date:   2019-04-16 10:54:24
# @Last Modified by:   admin
# @Last Modified time: 2019-04-12 16:48:24
"""
# 解析woff字体
# 每次访问页面，下载woff文件的链接都会变化
# 每次下载woff文件的字体不变，但是字符编码在变

from fontTools.ttLib import TTFont
import requests
from lxml import etree, html
import re
import base64
import io

# 选择一个标准字体对照表
standardFont = TTFont("standard_font.woff")
# 使用 "FontCreator字体查看软件" 查看字体的对应关系，然后设置对应关系
standardNumList = ["8", "0", "5", "7", "3", "2", "4", "1", "9", "6"]
standardUnicodeList = ["uniEF89", "uniF493", "uniF25B", "uniE11C", "uniF4D2", "uniE0C0", "uniF774", "uniEBC5", "uniF586", "uniEC3A"]

def get_piaofang(url):
    headers = { "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Cookie": "_lxsdk_cuid=16a05095977c8-0e7ec65aa6b70e-b78173e-144000-16a05095978c8; _lxsdk=16a05095977c8-0e7ec65aa6b70e-b78173e-144000-16a05095978c8; _lxsdk_s=16a240a6d0b-906-ce5-508%7C%7C3",
                "Host": "piaofang.maoyan.com",
                "Referer": "https://www.jianshu.com/p/5aa978e9823d",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36", }
    data = requests.get(url, headers=headers)
    # response = etree.HTML(data.text)
    response = html.fromstring(data.text)

    # 正则匹配woff的下载地址将其下载到本地
    woff_pat = re.compile(r':url\((data.*)\)\sformat\("woff"\)')
    woff = woff_pat.findall(data.text)
    print(woff)
    s = woff[0][woff[0].index('base64,')+7:]
    print(s)
    dtmp = base64.b64decode(s)
    maoyanFont = TTFont(io.BytesIO(dtmp))
    # print(maoyanFont['name'].glyphOrder)

    maoYanUnicodeList = maoyanFont['cmap'].tables[0].ttFont.getGlyphOrder()[2:]
    maoyanFont.saveXML('maoyan.xml')
    print(maoYanUnicodeList)

    comparisonTable = {".": "."}
    for i in range(10):
        maoYanGlyph = maoyanFont["glyf"][maoYanUnicodeList[i]]
        # print(maoYanGlyph, "***")
        for j in range(10):
            baseGlyph = standardFont["glyf"][standardUnicodeList[j]]
            if baseGlyph == maoYanGlyph:
                comparisonTable[maoYanUnicodeList[i][3:].lower()] = standardNumList[j]
                break
    print("comparisonTable: =====", comparisonTable)

    # 排名、片名、票房、平均票价、场均人次
    ul_objList = response.xpath("//div[@id='ranks-list']/ul")
    for ul in ul_objList:
        rank = ul.xpath("li[1]//text()")[0]
        pianming = ul.xpath("li[2]/p[1]/text()")[0]
        piaofang = ul.xpath("li[3]/i/text()")
        print(piaofang)

        piaofang_number = ''
        if piaofang:
            piaotmp = repr(piaofang[0]).strip("'").split(r"\u")[1:]
            print("解析： ", piaotmp)
            if piaotmp:
                for tmp in piaotmp:
                    piaofang_number += comparisonTable[tmp]


        avg_price = ul.xpath("li[4]/i/text()")
        changjun = ul.xpath("li[5]/i/text()")

        print("排名: {}, \n"
              "片名: {}, \n"
              "票房: {}, \n"
              "平均票价: {}, \n"
              "场均人次: {}, \n".format(rank, pianming, piaofang_number, avg_price, changjun))
    return comparisonTable

# def get_piaofang():


if __name__ == '__main__':
    url = "https://piaofang.maoyan.com/rankings/year"
    get_piaofang(url)












