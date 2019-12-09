#!/usr/bin/python
# python 3.7
# 11选5 彩票数据抓取工具

import os
import time
import datetime
import txtfile
import fileIndex2

# requirements: pytz, requests, bs4, lxml
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup

# const
baseUrl = "https://www.55128.cn/zs/"
outDir = "target/11-5"
sleepTime = 0
timeOut = 60 * 40
lastUpdated = {}

startTime = datetime.datetime.now()

provinces = {"sd": "山东", "gd": "广东", "js": "江苏",
             "jx": "江西", "sh": "上海", "ah": "安徽"}

provinceUrls = {"sd": "80_467.htm",
                "gd": "72_396.htm",
                "jx": "77_440.htm",
                "js": "76_431.htm",
                "sh": "81_476.htm",
                "ah": "70_378.htm"}

dateParamName = "searchTime"
dateParamValueFormat = "%Y-%m-%d"
defaultStartDate = "20180101"


# 批量建立文件夹
def makeDirs(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

# makeDirs end


# 获取指定省、指定日期的数据
def getProvinceData(province, date, session):
    provinceUrl = provinceUrls[province]
    url = "".join([baseUrl, provinceUrl])
    if date != None:
        url = "".join([url, "?", dateParamName, "=",
                       date.strftime(dateParamValueFormat)])
    print(url)
    response = session.get(url, timeout=20)
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.select("#chartData>tr")
    datas = {}
    for item in rows:
        cols = item.select("td:nth-child(-n+6)")
        if len(cols) < 6:
            continue
        key = cols[0].get_text().strip()
        values = []
        for col in cols[1:]:
            values.append(col.get_text().strip())
        datas[key] = values
    #
    return datas
# getProvinceData end


def writeTxtFile(province, datas):
    # 按月份分文件处理
    i = 0  # debug
    for month in datas.keys():
        fileName = "".join([province, "20", month, ".txt"])
        data = datas[month]
        print(">>>>>>", fileName)
        txtfile.appendDict(os.path.join(outDir, fileName), data)
        if i > 0:  # debug
            print(">>> Warning!")  # debug
        i += 1  # debug


# 更新指定省份、指定起始日期的数据
def updateProvinceData(province):
    beginDate = datetime.datetime.strptime(
        lastUpdated.get(province, [defaultStartDate])[0], "%Y%m%d").date()
    endDate = datetime.date.today()
    datas = {}
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=3))
    session.mount('https://', HTTPAdapter(max_retries=3))

    try:
        for i in range((endDate - beginDate).days+1):
            t = datetime.datetime.now() - startTime
            if t.seconds > timeOut:  # 超时退出
                print("超时退出", t)
                break
            day = beginDate + datetime.timedelta(days=i)
            key = day.strftime("%y%m%d")
            if i > 0:
                if day.day == 1:  # 每月开始，保存上月数据
                    writeTxtFile(province, datas)
                    txtfile.saveDict(lastlogfile, lastUpdated)
                    datas = {}
                if sleepTime > 0:
                    time.sleep(sleepTime)
            dayDatas = getProvinceData(province, day, session)
            if len(dayDatas) > 0:
                lastUpdated[province] = [day.strftime("%Y%m%d")]
            monthDatas = datas.setdefault(key[:4], {})
            monthDatas.update(dayDatas)
    except requests.exceptions.RequestException as e:
        print("Error: ", e)
    finally:
        session.close()
        if len(datas) > 0:
            writeTxtFile(province, datas)
            txtfile.saveDict(lastlogfile, lastUpdated)
# updateProvinceData end


# main
makeDirs(outDir)

# # 临时代码：对已有数据进行排序
# filenames = fileIndex._getTxtFiles(outDir)
# filenames.sort()
# for filename in filenames:
#     file = os.path.join(outDir, filename)
#     print(file)
#     dict = txtfile.loadDict(file)
#     txtfile.saveDict(file, dict)
# # 临时代码结束

lastlogfile = os.path.join(outDir, "lastupdated.dat")
if os.path.exists(lastlogfile):
    lastUpdated = txtfile.loadDict(lastlogfile)

for p in provinces.keys():
    t = datetime.datetime.now() - startTime
    if t.seconds > timeOut:  # 超时退出
        print("超时退出", t)
        break
    updateProvinceData(p)

txtfile.saveDict(lastlogfile, lastUpdated)

fileIndex2.create(outDir, provinces)

# main end
