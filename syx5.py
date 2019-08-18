#!/usr/bin/python
# python 3.7
# YDNIU 彩票数据抓取工具

import os
import sys
import json
import zipfile
from datetime import datetime
import pytz

# requirements: requests bs4 lxml
import requests
from bs4 import BeautifulSoup

# const
baseUrl = "https://chart.ydniu.com/trend/"
servicePrefix = "syx5"
outDir = "target/"

provinces = {"sd": "山东", "gd": "广东", "js": "江苏", "jx": "江西", "sh": "上海"}
changedFiles = {}


#
def makeDirs(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
# makeDirs end


# 更新 Dict 类型数据文件
def updateDictFile(file, dict):
    jsonFile = file + ".json"
    filePath = outDir + jsonFile
    if os.path.exists(filePath):
        try:
            with open(filePath, "r", encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
    else:
        data = {}
    #
    data.update(dict)
    with open(filePath, "w", encoding='utf-8') as f:
        json.dump(data, f)
    # 记录本次改变文件
    changedFiles[jsonFile] = {
        "fileName": jsonFile,
        "createTime": datetime.now(pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    }
# updateDictFile end


# 获取指定省的数据
def getProvinceData(province):
    url = "".join([baseUrl, servicePrefix, province, "/"])
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.select("#tabtrend>tbody>tr")
    datas = {}
    for item in rows:
        cols = item.select("td:nth-child(-n+6)")
        key = cols[0].get_text().strip()
        values = []
        for col in cols[1:]:
            values.append(col.get_text().strip())
        monthDatas = datas.setdefault(key[:6], {})
        monthDatas[key] = values
    #
    return datas
# getProvinceData end


# 更新输出文件索引
def updateIndexFile():
    indexJsonFile = outDir + "index.json"
    if os.path.exists(indexJsonFile):
        try:
            with open(indexJsonFile, "r", encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
    else:
        data = {}
    data.update(changedFiles)
    with open(indexJsonFile, "w", encoding='utf-8') as f:
        json.dump(data, f)
    #
    links = "  <ul>\n"
    for item in data.values():
        t = item["createTime"]
        file = item["fileName"]
        links += '    <li><a href="%s">%s (%s)</a></li>\n' % (file, file, t)
    links += "  </ul>"
    lines = '''
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no"/>
</head>
<body>
%s
</body>
</html>
''' % links
    #
    with open(outDir + "index.html", "w", encoding='utf-8') as f:
        f.write(lines)
# updateIndexFile end


# 更新指定省的数据
def updateProvinceData(province):
    provinceName = provinces[province]
    datas = getProvinceData(province)
    # 按月份分文件处理
    for month in datas.keys():
        fileName = province + month
        data = datas[month]
        updateDictFile(fileName, data)
# updateProvinceData end


# main
makeDirs(outDir)

for province in provinces.keys():
    updateProvinceData(province)  # 测试

updateIndexFile()
