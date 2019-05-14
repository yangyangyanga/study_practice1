# -*- coding:utf-8 -*-
"""
# @PROJECT: study_practice
# @Author: admin
# @Date:   2019-04-12 16:48:24
# @Last Modified by:   admin
# @Last Modified time: 2019-04-12 16:48:24
"""
# 解析woff字体


from fontTools.ttLib import TTFont
import io
import base64

# 选择一个标准字体对照表
standardFont = TTFont("standard_font.woff")
# 使用 "FontCreator字体查看软件" 查看字体的对应关系，然后设置对应关系
standardNumList = ["1", "6", "8", "0", "3", "4", "7", "5", "9", "2"]
standardUnicodeList = ["uniE3CA", "uniF2E0", "uniE667", "uniF6F5", "uniE123","uniF778", "uniE373", "uniF214", "uniE7BB", "uniF19C"]

def parse_font(s, record=False):
    data = base64.b64decode(s)
    maoYanFont = TTFont(io.BytesIO(data))
    if record:
        font.saveXML("maoyan.xml")
        font.save("maoyan.woff")
        # maoYanFont = TTFont("maoyan.woff")
    maoYanUnicodeList = maoYanFont["cmap"].tables[0].ttFont.getGlyphOrder()[2:]
    comparisonTable = {".": "."}

    for i in range(10):
        maoYanGlyph = maoYanFont["glyf"][maoYanUnicodeList[i]]
        for j in range(10):
            baseGlyph = standardFont["glyf"][standardUnicodeList[j]]
            if maoYanGlyph == baseGlyph:
                comparisonTable[maoYanUnicodeList[i][3:].lower()]=standardNumList[j]
                break
    return comparisonTable

def convert(unistring, comparisonTable):
    sl = repr(unistring).strip("'").split(r"\u")[1:]
    return "".join([comparisonTable[i] for i in sl])

if __name__ == '__main__':
    main()
    print(parse_font("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"))
