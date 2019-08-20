#!/usr/bin/python
# python 3.7
# 检查数据文件

import os
import operator
import json
import txtfile

baseDir = "target"


def checkData(filename):
    with open(filename + ".json", "r", encoding='utf-8') as f:
        data1 = json.load(f)
    data2 = txtfile.loadDict(filename+".txt")
    if not operator.eq(data1, data2):
        print(">>>> check error ", filename)


for dirpath, dirnames, filenames in os.walk(baseDir):
    for filename in filenames:
        if filename != "index.json" and os.path.splitext(filename)[1] == ".json":
            filename = os.path.join(dirpath, filename)
            filename = os.path.splitext(filename)[0]
            checkData(filename)
    break
