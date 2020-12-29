#!/usr/bin/python
# python 3.9
# 期货成交持仓
# 数据来源：http://m.data.eastmoney.com/futures/cjcc/
#         http://m.data.eastmoney.com/api/futures/basedata?str=904  全部期货类型
#         http://m.data.eastmoney.com/api/futures/GetContract?market=&date=2020-12-25  合约查询
import os
import shutil
import time
from datetime import datetime

import demjson
import pytz
import requests

import txtfile

cache_url = "https://han-feng.github.io/CrawlerYdniu/qhcjcc.zip"
temp_dir = "target/qhcjcc"
dist_dir = "dist"
sleepTime = 0
lastUpdated = {}
lastlogfile = os.path.join(temp_dir, ".lastupdated")

defaultStartDate = "20200101"

contracts = {
    "A2101": "069001007",  # 大豆
    "A2105": "069001007",
    "HC2101": "069001005",  # 热卷
    "HC2105": "069001005",
    "OI2101": "069001008",  # 菜籽油
    "OI2105": "069001008",
    "Y2101": "069001007",  # 豆油
    "Y2105": "069001007",
    "Y2107": "069001007",
    "Y2109": "069001007"
}


def makeDirs(dirPath):
    """批量建立文件夹"""
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)


def get_contract(date):
    """获得指定日期的可交易合约信息"""
    url = "http://m.data.eastmoney.com/api/futures/GetContract?market=&date=" + date
    response = requests.get(url)
    datas = demjson.decode(response.text)
    datas = demjson.decode(datas)
    result = {}
    if datas is None:
        return result
    for data in datas:
        result[data["value"]] = [d[1] for d in data["data"]]
    return result


def get_datas(date, contract, duo=True):
    name = ""
    if duo:
        name = "%E5%A4%9A%E5%A4%B4%E6%8C%81%E4%BB%93%E9%BE%99%E8%99%8E%E6%A6%9C"
    else:
        name = "%E7%A9%BA%E5%A4%B4%E6%8C%81%E4%BB%93%E9%BE%99%E8%99%8E%E6%A6%9C"
    url = "http://m.data.eastmoney.com/api/futures/GetQhcjcc?market=" \
        + contracts[contract] \
        + "&date=" \
        + date \
        + "&contract=" \
        + contract \
        + "&name=" \
        + name \
        + "&page=1"
    print("🦎 GET %s %s %s" % (date, contract, str(duo)))
    response = requests.get(url)
    datas = demjson.decode(response.text)
    result = {}
    if datas is None:
        return result
    i = 1
    for data in datas:
        result["%s,%02d" % (date, i)] = [
            data["Code"],
            data["Name"],
            str(data["Ddl"]),
            str(data["DdlZJ"]),
            str(data["Kdl"]),
            str(data["KdlZJ"])
        ]
        i = i+1
    return result


def writeTxtFile(prefix, datas):
    """按月份分文件处理"""
    i = 0  # debug
    # print(datas)
    for month in datas.keys():
        fileName = "".join([prefix, "-", "20", month, ".txt"])
        data = datas[month]
        print(">>>>>> 💾", fileName)
        txtfile.appendDict(os.path.join(temp_dir, fileName), data)
        if i > 0:  # debug
            print(">>> ⚠️ Warning!")  # debug
        i += 1  # debug


def updateContractData(contract):
    """更新指定合约、指定起始日期的数据"""
    beginDate = datetime.datetime.strptime(
        lastUpdated.get(contract, [defaultStartDate])[0], "%Y%m%d").date()
    endDate = datetime.date.today()
    duo_datas = {}
    kong_datas = {}
    print("🛰 Update %s ~ %s %s ……" % (beginDate, endDate, contract))
    try:
        for i in range((endDate - beginDate).days + 1):
            day = beginDate + datetime.timedelta(days=i)
            key = day.strftime("%y%m%d")
            if i > 0:
                if day.day == 1:  # 每月开始，保存上月数据
                    writeTxtFile(contract+"-D", duo_datas)
                    writeTxtFile(contract+"-K", kong_datas)
                    txtfile.saveDict(lastlogfile, lastUpdated)
                    duo_datas = {}
                    kong_datas = {}
                if sleepTime > 0:
                    time.sleep(sleepTime)
            """
            TODO
            FIXME
            """
            dayStr = day.strftime("%Y-%m-%d")
            dayDatas = get_datas(dayStr, contract)
            if len(dayDatas) > 0:
                monthDatas = duo_datas.setdefault(key[:4], {})
                monthDatas.update(dayDatas)
            dayDatas = get_datas(dayStr, contract, duo=False)
            if len(dayDatas) > 0:
                monthDatas = kong_datas.setdefault(key[:4], {})
                monthDatas.update(dayDatas)
            lastUpdated[contract] = [day.strftime("%Y%m%d")]
    except requests.exceptions.RequestException as e:
        print("🔥 Error: ", e)
    finally:
        if len(duo_datas) > 0:
            writeTxtFile(contract+"-D", duo_datas)
        if len(kong_datas) > 0:
            writeTxtFile(contract+"-K", kong_datas)
        txtfile.saveDict(lastlogfile, lastUpdated)


# main
print("⏱", datetime.now(pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S"))

# makeDirs(temp_dir)
# makeDirs(dist_dir)

# response = requests.get(cache_url)
# if response.status_code == 200:
#     zipFile = "%s.zip" % temp_dir
#     with open(zipFile, "wb") as code:
#         code.write(response.content)
#     shutil.unpack_archive(zipFile, temp_dir)

# if os.path.exists(lastlogfile):
#     lastUpdated = txtfile.loadDict(lastlogfile)

# """TODO 调整为日期循环"""
# for contract in contracts:
#     updateContractData(contract)

# shutil.make_archive(dist_dir+"/qhcjcc", "zip", root_dir=temp_dir)
