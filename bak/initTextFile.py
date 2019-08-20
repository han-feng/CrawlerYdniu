#!/usr/bin/python
# python 3.7
# 文本文件数据初始化工具：自动搜索target目录下json数据文件，并转换成txt格式数据文件

import os
import json
import txtfile

baseDir = "target"


def conver(filename):
    with open(filename + ".json", "r", encoding='utf-8') as f:
        data = json.load(f)
    txtfile.appendDict(filename+".txt", data)


for dirpath, dirnames, filenames in os.walk(baseDir):
    for filename in filenames:
        if filename != "index.json" and os.path.splitext(filename)[1] == ".json":
            filename = os.path.join(dirpath, filename)
            filename = os.path.splitext(filename)[0]
            conver(filename)
    break
