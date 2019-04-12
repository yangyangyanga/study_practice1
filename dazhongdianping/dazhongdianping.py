# -*- coding:utf-8 -*-
"""
# @PROJECT: Study
# @Author: yangyaxia
# @Date:   2019-04-09 14:41:12
# @Last Modified by:   yangyaxia
# @Last Modified time: 2019-04-09 14:41:12
"""
import re
import requests
import lxml.html as H
from lxml import etree
import math


headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",}

'''1.获取css_url及span对应的TAG值'''
def get_tag(_list, offset=1):
    # 从第一个开始查
    _new_list = [data[0:offset] for data in _list]

    if len(set(_new_list)) == 1:
        # 如果set后只有一个值，说明全部重复，这个时候就把offset加1
        offset += 1
        return get_tag(_list, offset)
    else:
        _return_data = [data[0:offset-1] for data in _list][0]
        return _return_data

def get_css(content):
    """
    :param content:大众点评页源码内容：https://www.dianping.com/beijing/ch10/r70191
    :return:css_url:svg内容的url，多个span对应的class值
                    例：['qsu0f', 'qsxjd', 'qst99', ..., 'qsxjd']

    """
    matched = re.search(r'href="([^"]+svgtextcss[^"]+)"', content, re.M)
    # print("=====matched: ", matched)
    if not matched:
        raise Exception("cannot find svgtextcss file")
    css_url = matched.group(1)

    css_url = "https:" + css_url
    class_tag = re.findall(r"<b><span class=\"(.*?)\"></span>", content)
    _tag = get_tag(class_tag)
    # print(_tag, '*****_tag')

    return css_url, _tag


def get_css_and_tag(content):
    """
    :param content:待爬链接
    :return: css链接，该span对应的tag
    """
    find_css_url = re.search(r'href="([^"]+svgtextcss[^"]+)"', content, re.M)
    print("=====find_css_url: ", find_css_url)
    if not find_css_url:
        raise Exception("cannot find css_url, check")
    css_url = find_css_url.group(1)

    css_url = "https:" + css_url
    # 这个网页上不同的字段是由不同的css段来进行控制的，所以要找到这个评论数据对应的tag，在这里返回的值为vx；而在获取评论数据时，tag就是fu-;
    # 具体可以观察上面截图的3个span对应的属性值，相等的最长部分为vx
    class_tag = re.findall("<b class=\"(.*?)\"></b>", content)
    _tag = get_tag(class_tag)

    return css_url, _tag


'''2.获取属性与像素值的对应关系
        span的class属性值对应的像素值，返回一个字典
'''
def get_css_and_px_dict(css_url):
    """
    :param css_url: svg的css样式链接
    :return: css_name_and_px[span_class_attr_name] = [offset, position]
            例：css_name_and_px['mar7k'] = [-240.0, -857.0]
    """
    con = requests.get(css_url, headers=headers).content.decode('utf-8')
    find_datas = re.findall(r'(\.[a-zA-Z0-9-]+)\{background:(\-\d+\.\d+)px (\-\d+\.\d+)px', con)
    css_name_and_px = {}
    print("======find_datas: ", find_datas)
    for data in find_datas:
        # 属性对应的值
        span_class_attr_name = data[0][1:]
        # 偏移量
        offset = data[1]
        # 阈值
        position = data[2]
        css_name_and_px[span_class_attr_name] = [offset, position]
    return css_name_and_px

'''3.获取svg文件【css样式文件】的.svg取值url 
    解析取值页面
'''
def get_svg_threshold_and_int_dict(css_url, _tag):
    """
    :param css_url:例：http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/0f9a1a0cbe115484299a3d9b29f27f89.css
    :param _tag:span的class值，tag
    :return:    index_and_word_dict[int_data] = range(last, y+1)
                例：index_and_word_dict['27138613370663304843259425811177915135472833228069'] = range(31, 80)
    """
    con = requests.get(css_url, headers=headers).content.decode('utf-8')
    index_and_word_dict = {}

    # 根据tag值匹配到相应的svg的网址
    find_svg_url = re.search(r'span\[class\^="%s"\].*?background\-image: url\((.*?)\);' % _tag, con)
    if not find_svg_url:
        raise Exception("cannot find svg file, check")
    svg_url = find_svg_url.group(1)
    svg_url = "https:"+svg_url

    # svg网址内容
    svg_content = requests.get(svg_url, headers=headers).content
    root = H.document_fromstring(svg_content)
    datas = root.xpath("//text")
    # 把阈值和对应的数字集合放入一个字典中
    last = 0
    for index, data in enumerate(datas):
        y = int(data.xpath('@y')[0])    # 阈值
        int_data = data.xpath('text()')[0]  # 数据字段集合
        index_and_word_dict[int_data] = range(last, y+1)    # 以数据字段集合为key，阈值范围为value
        last = y
    return index_and_word_dict

'''4.获取最终的值'''
def get_data(url):
    """
    :param page_url:待获取url
    :return:
    """
    con = requests.get(url, headers=headers).content.decode('utf-8')
    # print("====con==== ", con)
    # 获取css_url，及tag
    css_url, _tag = get_css(con)
    # print("css_url, _tag: ", get_css(con))
    # 获取css对应名与像素的映射
    css_and_px_dict = get_css_and_px_dict(css_url)
    # 获取svg的阈值与数字集合的映射
    svg_threshold_and_int_dict = get_svg_threshold_and_int_dict(css_url, _tag)

    doc = etree.HTML(con)
    shops = doc.xpath('//div[@id="shop-all-list"]/ul/li')
    for shop in shops:
        # 店名
        name = shop.xpath('.//div[@class="tit"]/a/h4/text()')[0]
        # print("======店名：", name)

        # 评论数、人均价格、口味、服务、环境分
        comment_num = 0
        price_num = taste = service = environment = 0
        comment_and_price_datas = shop.xpath(".//div[@class='comment']")
        for comment_and_price_data in comment_and_price_datas:
            # print("======店名======：", name)

            # 评论数
            # 是一个私有变量, 只用于标明, 外部类还是可以访问到这个变量
            _comment_data = comment_and_price_data.xpath('a[@class="review-num"]/b/node()')
            # print("_comment_data: ", _comment_data)
            # 遍历每一个node，这里node的类型不同，分别有etree._ElementStringResult(字符),etree._Element(元素),etree._ElementUnicodeResult(字符)
            for _node in _comment_data:
                #     如果是字符，则直接取出
                if isinstance(_node, etree._ElementStringResult) or isinstance(_node, etree._ElementUnicodeResult):
                    # print("是字符")
                    comment_num = comment_num * 10 + int(_node)     # 从左到右获得数字，依次乘10+上次的数
                else:
                    # 如果是span类型，则要去找数据
                    # span  class的attr属性
                    span_class_attr_name = _node.attrib["class"]
                    # print("span_class_attr_name: ", span_class_attr_name)
                    # 偏移量，以及所处的段（阈值）
                    offset, position = css_and_px_dict[span_class_attr_name]
                    index = abs(int(float(offset)))
                    position = abs(int(float(position)))
                    # print("index = ", index)
                    # print("position = ", position)
                    # 判断
                    for key, value in svg_threshold_and_int_dict.items():
                        # 如果阈值在value里面说明数字集合从这段获得，即svg_threshold_and_int_dict的key
                        if position in value:
                            threshold = int(math.ceil(index/12))
                            number = int(key[threshold-1])
                            comment_num = comment_num * 10 + number
                            # print("=====comment_num=====****:", comment_num)
            # print("=======comment_num: ", comment_num)

            # 人均价格
            _price = comment_and_price_data.xpath('a[@class="mean-price"]/b/node()')
            for price_node in _price:
                if isinstance(price_node, etree._ElementStringResult):
                    price_num = price_num * 10 + int(price_node)
                elif isinstance(price_node, etree._ElementUnicodeResult):
                    if len(price_node) > 1:
                        price_num = price_num * 10 + int(price_node[1:])
                else:
                    span_class_attr_name = price_node.attrib['class']
                    offset, position = css_and_px_dict[span_class_attr_name]
                    index = abs(int(float(offset)))
                    position = abs(int(float(position)))
                    for key, value in svg_threshold_and_int_dict.items():
                        if position in value:
                            threshold = int(math.ceil(index/12))
                            price_number = int(key[threshold-1])
                            price_num = price_num * 10 + price_number
            # print("=======price_num: ", price_num)

            # 口味、环境、服务评分数据
            others_num_node = shop.xpath('.//span[@class="comment-list"]/span')
            for other_datas in others_num_node:
                # print("============other_datas.xpath============", other_datas.xpath("text()")[0])
                # 口味
                # 前面加个条件，是为了判断他不为空才能继续后面的取值第一个元素
                if other_datas.xpath("text()") and other_datas.xpath("text()")[0] == "口味":
                    _taste_data = other_datas.xpath('b/node()')
                    for _taste in _taste_data:
                        if isinstance(_taste, etree._Element):
                            css_class = _taste.attrib['class']
                            offset, position = css_and_px_dict[css_class]
                            index = abs(int(float(offset)))
                            position = abs(int(float(position)))
                            for key, value in svg_threshold_and_int_dict.items():
                                if position in value:
                                    threshold = int(math.ceil(index/12))
                                    number = int(key[threshold-1])
                                    taste = taste * 10 + number
                        else:
                            if len(_taste) > 1:
                                taste = taste * 10 + int(_taste[1:])


                if other_datas.xpath('text()') and other_datas.xpath('text()')[0] == "服务":
                    _service_data = other_datas.xpath('b/node()')
                    for _service in _service_data:
                        if isinstance(_service, etree._Element):
                            css_class = _service.attrib['class']
                            # 偏移量
                            offset, position = css_and_px_dict[css_class]
                            index = abs(int(float(offset)))
                            position = abs(int(float(position)))
                            for key, value in svg_threshold_and_int_dict.items():
                                if position in value:
                                    threshold = int(math.ceil(index/12))
                                    number = int(key[threshold-1])
                                    service = service * 10 + number
                        else:
                            if len(_service) > 1:
                                service = service * 10 + int(_service[1:])

                if other_datas.xpath('text()') and other_datas.xpath('text()')[0] == "环境":
                    _enviroment_data = other_datas.xpath('b/node()')
                    for _enviroment in _enviroment_data:
                        if isinstance(_enviroment, etree._Element):
                            css_class = _enviroment.attrib['class']
                            # 根据他的span标签class属性值获取他的偏移量和阈值
                            offset, position = css_and_px_dict[css_class]
                            index = abs(int(float(offset)))
                            position = abs(int(float(position)))
                            for key, value in svg_threshold_and_int_dict.items():
                                # 如果阈值在value范围里面，说明取值这一段字符串key里面的数
                                if position in value:
                                    threshold = int(math.ceil(index/12))
                                    number = int(key[threshold-1])
                                    environment = environment * 10 + number
                        else:
                            if len(_enviroment) > 1:
                                environment = environment * 10 + int(_enviroment[1:])

            print("restaurant: {},\n"
                  "comment total num: {},\n"
                  "price num: {},\n"
                  "taste score: {},\n"
                  "service socre: {},\n"
                  "environment_score: {},"
                  "\n ".
                  format(name, comment_num, price_num, taste, service, environment))
            # print("=======taste: ", taste)
            # print("=======service: ", service)
            # print("=======environment: ", environment)


if __name__ == '__main__':
    url = "https://www.dianping.com/beijing/ch10/r70191"
    get_data(url)






















