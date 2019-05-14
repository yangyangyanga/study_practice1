# -*- coding:utf-8 -*-
"""
# @PROJECT: Study
# @Author: admin
# @Date:   2019-05-13 11:37:58
# @Last Modified by:   admin
# @Last Modified time: 2019-05-13 11:37:58
"""
'''
问题描述：58同城租房信息爬取，房间size和面积，价格有字体反爬
'''
import requests
from lxml import etree, html
import time
import re
from fontTools.ttLib import TTFont
import base64
import io
import xlrd, xlwt
from urllib import parse

# 加密数字解析
# 返回加密数字
def covert_secret_int(yuanma, base64_str):
    # base64解析  下载到本地ttf文件
    ttf = base64.decodebytes(base64_str.encode())
    zufangFont = TTFont(io.BytesIO(ttf))
    zufangFont.save('58zufang2.ttf')

    zufangFont.saveXML('58zufang2.xml')
    # print(zufangFont.keys())
    uniList = zufangFont['cmap'].tables[0].ttFont.getGlyphOrder()
    uniListkey = zufangFont['cmap'].tables[0].ttFont.tables['cmap'].tables[0].cmap
    # print(uniList)
    # print(uniListkey)

    comparisonTable = {}
    for key, value in uniListkey.items():
        # print(hex(key))
        # comparisonTable[str(hex(key))[2:].lower()] = str(int(value.replace("glyph0000", "").replace("glyph000", ""))-1)
        comparisonTable[key] = str(int(value.replace("glyph0000", "").replace("glyph000", "")) - 1)
    # print("comparisonTable: ", comparisonTable)
    real_num = comparisonTable.get(yuanma)
    return real_num

# 将一个字符串中含有加密的数字转为正常文字输出
# return  返回
def get_result_data(yuan_str, base64_str):
    yuan_str_tmp = ""
    for sa_index in range(len(yuan_str)):
        num = covert_secret_int(ord(yuan_str[sa_index]), base64_str)
        if num is None:
            yuan_str_tmp += yuan_str[sa_index]
        else:
            yuan_str_tmp += num
    return yuan_str_tmp

# 写入excel
def write_in_excel(path, table, data_list):
    # 先读出最大行数
    data = xlrd.open_workbook(path)
    tables = data.sheet_by_index(0)
    nrows = tables.nrows
    print("nrows === ", nrows)
    # 写入一行的数据
    for i in range(len(data_list)):
        table.write(nrows, i, data_list[i])
    # file.save(path)

def parse_rent(url, path):
    headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
               "accept-encoding": "gzip, deflate, br",
               "accept-language": "zh-CN,zh;q=0.9",
               "cache-control": "max-age=0",
               "cookie": "f=n; commontopbar_new_city_info=1%7C%E5%8C%97%E4%BA%AC%7Cbj; commontopbar_ipcity=bj%7C%E5%8C%97%E4%BA%AC%7C0; userid360_xml=BE64C4FDEB75ABC681E8205AFE2CA856; time_create=1560309353965; f=n; id58=c5/nn1yLbeo3tDg37uyIAg==; 58tj_uuid=e543770f-1b6f-42ca-9db2-ddbe9b04777b; wmda_uuid=a93016c02d61c06ed05e1c54becc4192; wmda_new_uuid=1; wmda_visited_projects=%3B2385390625025; als=0; f=n; xxzl_deviceid=YqMRANQyNnw%2BGNokmM7n%2F9jW6t6VnDeMNyijlyKOsWisPsEZmWF4Adcxz%2FxbyPM4; defraudName=defraud; Hm_lvt_dcee4f66df28844222ef0479976aabf1=1557724755; Hm_lpvt_dcee4f66df28844222ef0479976aabf1=1557724755; 58home=bj; commontopbar_new_city_info=1%7C%E5%8C%97%E4%BA%AC%7Cbj; city=bj; commontopbar_ipcity=bj%7C%E5%8C%97%E4%BA%AC%7C0; ppStore_fingerprint=AA634CFAFD3E9216491F9A87BBD6049FACE35FEE9840E3E1%EF%BC%BF1557726277735; wmda_session_id_2385390625025=1557728564432-3494d745-ea9d-1834; new_session=1; new_uv=3; utm_source=; spm=; init_refer=https%253A%252F%252Fbj.58.com%252Fzufang%252F38096370880666x.shtml%253Fentinfo%253D38096370880666_0%2526fzbref%253D1%2526from%253D1-list-0%2526params%253Drank0830gspanxuan0099%255Edesc%2526psid%253D128353237204174267685623143%2526iuType%253Dgz_2%2526ClickID%253D2%2526cookie%253D%257C%257C%257Cc5%252Fnn1yLbeo3tDg37uyIAg%253D%253D%2526PGTID%253D0d300008-0047-667b-fd6d-8d4f8065d725%2526apptype%253D0%2526key%253D%2526pubid%253D74017401%2526trackkey%253D38096370880666_c020bba5-bd78-488f-9a05-31ae2ce0fd6e_20190513134413_1557726253048%2526fcinfotype%253Dgz; xzfzqtoken=odXW0DzzgP%2B0EFp840UENiyIyAeave%2BYqK4Xbc7KdY%2BswYy7O8Wx3T5xAwkak0ycin35brBb%2F%2FeSODvMgkQULA%3D%3D",
               "referer": "https://bj.58.com/zufang/38096370880666x.shtml?entinfo=38096370880666_0&fzbref=1&from=1-list-0&params=rank0830gspanxuan0099^desc&psid=128353237204174267685623143&iuType=gz_2&ClickID=2&cookie=|||c5/nn1yLbeo3tDg37uyIAg==&PGTID=0d300008-0047-667b-fd6d-8d4f8065d725&apptype=0&key=&pubid=74017401&trackkey=38096370880666_c020bba5-bd78-488f-9a05-31ae2ce0fd6e_20190513134413_1557726253048&fcinfotype=gz",
               "upgrade-insecure-requests": "1",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36", }

    data = requests.get(url, headers)
    # response = etree.HTML(data.text)
    response = html.fromstring(data.text)

    # 匹配ttf font
    cmp = re.findall(r";src:url\('(data.*)'\)\sformat\('truetype'\)", data.text)
    print("cmp: ", cmp)
    try:
        base64_str = cmp[0][cmp[0].index('base64,') + 7:]
        print(base64_str)
        # real_num = covert_secret_int("ss", base64_str)

        file = xlwt.Workbook()
        table = file.add_sheet('zufang', cell_overwrite_ok=False)
        # 标题、价钱、size、面积、链接、所属区域、所在小区、邻近地铁站
        li_list = response.xpath("//ul[@class='listUl']/li")
        print("li_list====", len(li_list))
        for li in li_list:
            data_list = []
            time.sleep(3)
            print("=========================================")
            # 链接
            link = ''.join(li.xpath("div[2]//h2[1]/a/@href")).strip()
            print("link == ", link)
            data_list.append(link)

            # 标题
            title = ''.join(li.xpath("div[2]//h2[1]/a//text()")).strip()
            print("title == ", title)
            if title:
                title_str = get_result_data(title, base64_str)
            print("解析之后：title_str == ", title_str)
            data_list.append(title_str)

            # 价钱
            price = ''.join(li.xpath("div[@class='listliright']/div[@class='money']/b//text()"))
            print("price == ", price)
            price_str = ""
            if price:
                price_str = get_result_data(price, base64_str)
                # for p in price:
                #     price_str += covert_secret_int(ord(p), base64_str)
            print("解析后：price_str == ", price_str)
            data_list.append(price_str)

            # 房子布局、面积       【字符串不可变】
            sizeArea = ''.join(li.xpath("div[2]//h2[1]/following-sibling::p[1]//text()")).strip()
            print("sizeArea == ", sizeArea)
            sizeAreaTmp = ''
            if sizeArea:
                sizeAreaTmp = get_result_data(sizeArea, base64_str)
            print("解析后：sizeAreaTmp == ", sizeAreaTmp)
            sizeArea_list = sizeAreaTmp.split()
            print(sizeArea_list)
            if len(sizeArea_list) == 2:
                size = sizeArea_list[0]
                area = sizeArea_list[1]
            else:
                size = area = sizeAreaTmp
            data_list.append(size)
            data_list.append(area)

            # 所属区域
            region = ''.join(li.xpath("div[2]/h2[1]/following-sibling::p[@class='add']/a[1]//text()")).strip()
            print("region == ", region)
            data_list.append(region)

            # 所在小区
            village = ''.join(li.xpath("div[2]/h2[1]/following-sibling::p[@class='add']/a[2]//text()")).strip()
            print("village == ", village)
            data_list.append(village)

            # 邻近地铁
            subway = ''.join(li.xpath("div[2]/h2[1]/following-sibling::p[@class='add']/text()")).strip()
            print("subway == ", subway)
            data_list.append(subway)
            write_in_excel(path, table, data_list)
            file.save(path)
    except Exception as e:
        print("异常报错： ", str(e))

if __name__ == '__main__':
    url = "https://bj.58.com/chaoyang/chuzu/"
    path = "58zufang.xlsx"
    parse_rent(url, path)
