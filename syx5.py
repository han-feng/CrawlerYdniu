#!/usr/bin/python
# python 3.7
# YDNIU 彩票数据抓取工具

import os
import sys
import json
import zipfile
from datetime import datetime

import txtfile
import fileIndex

# requirements: pytz, requests, bs4, lxml
import pytz
import requests
from bs4 import BeautifulSoup

# const
baseUrl = "https://chart.ydniu.com/trend/"
servicePrefix = "syx5"
outDir = "target/"

provinces = {"sd": "山东", "gd": "广东", "js": "江苏", "jx": "江西", "sh": "上海"}
changedFiles = {}


# 批量建立文件夹
def makeDirs(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

# makeDirs end


# 获取省份字典数据
def getProvinces():
    url = "".join([baseUrl, servicePrefix, "sd/"])
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.select("#divMain>div.Lottery>li:nth-child(1)>label>a")
    links += soup.select(
        "#divMain>div.Lottery>li:nth-child(1)>label>div>a")
    ps = {}
    for link in links:
        name = link.get_text().strip()[:-4]
        id = link.get("href").strip()[11:-1]
        ps[id] = name
    return ps
# getProvinces end


# 更新 Dict 类型数据文件
def updateDictTxtFile(file, dict):
    txtFile = file + ".txt"
    filePath = outDir + txtFile
    txtfile.appendDict(filePath, dict)
    # 记录本次改变文件
    changedFiles[txtFile] = {
        "fileName":
        txtFile,
        "createTime":
        datetime.now(
            pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %Z%z")
    }
# updateDictTxtFile end


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
# updateIndexFile end


# 更新指定省的数据
def updateProvinceData(province):
    datas = getProvinceData(province)
    # 按月份分文件处理
    for month in datas.keys():
        fileName = province + month
        data = datas[month]
        # updateDictFile(fileName, data)
        updateDictTxtFile(fileName, data)
# updateProvinceData end


# main
makeDirs(outDir)

provinces.update(getProvinces())

for province in provinces.keys():
    updateProvinceData(province)

updateIndexFile()
fileIndex.create(outDir)

# main end
