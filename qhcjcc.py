#!/usr/bin/python
# python 3.9
# 期货成交持仓
# 数据来源：http://m.data.eastmoney.com/futures/cjcc/

import datetime
import json
import os
import shutil
import time

import requests

import txtfile

outDir = "target/qhcjcc"
sleepTime = 0
# timeOut = 60 * 40
lastUpdated = {}

defaultStartDate = "20200101"

contracts = {
    # "A2101": "069001007",  # 大豆
    # "A2105": "069001007",
    # "HC2101": "069001005",  # 热卷
    # "HC2105": "069001005",
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
    print("GET " + url)
    response = requests.get(url)
    datas = json.loads(response.text)
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
        print(">>>>>>", fileName)
        txtfile.appendDict(os.path.join(outDir, fileName), data)
        if i > 0:  # debug
            print(">>> Warning!")  # debug
        i += 1  # debug


def updateContractData(contract):
    """更新指定合约、指定起始日期的数据"""
    beginDate = datetime.datetime.strptime(
        lastUpdated.get(contract, [defaultStartDate])[0], "%Y%m%d").date()
    endDate = datetime.date.today()
    duo_datas = {}
    kong_datas = {}

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
        print("Error: ", e)
    finally:
        if len(duo_datas) > 0:
            writeTxtFile(contract+"-D", duo_datas)
        if len(kong_datas) > 0:
            writeTxtFile(contract+"-K", kong_datas)
        txtfile.saveDict(lastlogfile, lastUpdated)


# main
makeDirs(outDir)


lastlogfile = os.path.join(outDir, "lastupdated.dat")
if os.path.exists(lastlogfile):
    lastUpdated = txtfile.loadDict(lastlogfile)

for contract in contracts:
    updateContractData(contract)

shutil.make_archive(outDir, "zip", root_dir=outDir)
