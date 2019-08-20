#!/usr/bin/python
# python 3.7
# 删除json格式数据文件

import os
import json
import txtfile

baseDir = "target"


for dirpath, dirnames, filenames in os.walk(baseDir):
    for filename in filenames:
        if filename != "index.json" and os.path.splitext(filename)[1] == ".json":
            filename = os.path.join(dirpath, filename)
            os.remove(filename)
    break

indexJsonFile = os.path.join(baseDir, "index.json")
if os.path.exists(indexJsonFile):
    with open(indexJsonFile, "r", encoding='utf-8') as f:
        data = json.load(f)
    newData = {}
    for name in data.keys():
        if os.path.splitext(name)[1] != ".json":
            newData[name] = data[name]
    with open(indexJsonFile, "w", encoding='utf-8') as f:
        json.dump(newData, f)
