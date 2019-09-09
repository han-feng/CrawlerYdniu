#!/usr/bin/python
# python 3.7
# 11选5 彩票数据抓取工具

import os
import txtfile
import fileIndex

# requirements: pytz, requests, bs4, lxml
import requests
from bs4 import BeautifulSoup

# const
baseUrl = "https://www.55128.cn/zs/"
outDir = "target/11-5/"

provinces = {"sd": "山东", "gd": "广东", "js": "江苏",
             "jx": "江西", "sh": "上海", "ah": "安徽"}

provinceUrls = {"sd": "80_467.htm",
                "gd": "80_467.htm",
                "jx": "77_440.htm",
                "js": "76_431.htm",
                "sh": "81_476.htm",
                "ah": "70_378.htm"}


# 批量建立文件夹
def makeDirs(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

# makeDirs end


# 获取指定省的数据
def getProvinceData(province):
    provinceUrl = provinceUrls[province]
    url = "".join([baseUrl, provinceUrl])
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.select("#chartData>tr")
    datas = {}
    for item in rows:
        cols = item.select("td:nth-child(-n+6)")
        if len(cols) < 6:
            continue
        key = "20" + cols[0].get_text().strip()
        values = []
        for col in cols[1:]:
            values.append(col.get_text().strip())
        monthDatas = datas.setdefault(key[:6], {})
        monthDatas[key] = values
    #
    return datas
# getProvinceData end


# 更新指定省的数据
def updateProvinceData(province):
    datas = getProvinceData(province)
    # 按月份分文件处理
    for month in datas.keys():
        fileName = province + month + ".txt"
        data = datas[month]
        txtfile.appendDict(os.path.join(outDir, fileName), data)
# updateProvinceData end


# main
makeDirs(outDir)

for p in provinces.keys():
    updateProvinceData(p)

fileIndex.create(outDir, provinces)

# main end
