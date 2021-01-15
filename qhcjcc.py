#!/usr/bin/python
# python 3.9
# 期货成交持仓
# 数据来源：http://m.data.eastmoney.com/futures/cjcc/
#         http://m.data.eastmoney.com/api/futures/basedata?str=904  全部期货类型
#         http://m.data.eastmoney.com/api/futures/GetContract?market=&date=2020-12-25  合约查询
import os
import shutil
import time
from datetime import datetime, timedelta
from functools import lru_cache

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

defaultStartDate = "20200701"

contract_types = {
    "A": {
        "name": "大豆",
        "market": "069001007"
    },
    "HC": {
        "name": "热卷",
        "market": "069001005"
    },
    "OI": {
        "name": "菜籽油",
        "market": "069001008"
    },
    "Y": {
        "name": "豆油",
        "market": "069001007"
    },
}


def make_dirs(dirPath):
    """批量建立文件夹"""
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)


_http_get_last_time_ = 0


def http_get(url):
    global _http_get_last_time_
    if sleepTime > 0 and time.time()-_http_get_last_time_ < sleepTime:
        s = _http_get_last_time_+sleepTime-time.time()
        print("🐞 sleep %f" % s)
        time.sleep(s)
    response = requests.get(url)
    _http_get_last_time_ = time.time()  # 秒
    return response


@lru_cache(maxsize=366)  # 缓存一年数据
def get_contracts(day):
    """获得指定日期的可交易合约信息"""
    url = f"http://m.data.eastmoney.com/api/futures/GetContract?market=&date={day}"
    print("  🕷 Get contract %s" % day)
    response = http_get(url)
    datas = response.text
    if len(datas.strip()) == 0:
        return {}
    datas = demjson.decode(datas)
    if len(datas.strip()) == 0:
        return {}

    datas = demjson.decode(datas)
    if datas is None:
        return {}

    result = {}
    for data in datas:
        result[data["value"]] = [d[1] for d in data["data"]]
    return result


def get_contracts_data(day, market, contracts, duo=True):
    """获取指定日期、指定合约集合的汇总数据"""
    ddl = 0
    ddlzj = 0
    kdl = 0
    kdlzj = 0
    i = 0
    for contract in contracts:
        datas = get_contract_data(day, market, contract, duo)
        for data in datas:
            i += 1
            ddl += data["Ddl"]
            ddlzj += data["DdlZJ"]
            kdl += data["Kdl"]
            kdlzj += data["KdlZJ"]
    if i > 0:
        return {
            day: [str(ddl), str(ddlzj), str(kdl), str(kdlzj)]
        }
    return None


def get_contract_data(day, market, contract, duo=True):
    """获取指定日期指定合约的明细数据"""
    name = ""
    if duo:
        name = r"%E5%A4%9A%E5%A4%B4%E6%8C%81%E4%BB%93%E9%BE%99%E8%99%8E%E6%A6%9C"
    else:
        name = r"%E7%A9%BA%E5%A4%B4%E6%8C%81%E4%BB%93%E9%BE%99%E8%99%8E%E6%A6%9C"
    url = f"http://m.data.eastmoney.com/api/futures/GetQhcjcc?market={market}&date={day}&contract={contract}&name={name}&page=1"
    print("  🕷 Get %s %s %s" % (day, contract, ("D" if duo else "K")))
    response = http_get(url)
    datas = demjson.decode(response.text)
    if datas is None:
        return []
    return datas


def write_txtfile(prefix, datas):
    """按月份分文件处理"""
    i = 0  # debug
    # print(datas)
    for month in datas.keys():
        fileName = "".join([prefix, "-", "20", month, ".txt"])
        data = datas[month]
        txtfile.appendDict(os.path.join(temp_dir, fileName), data, cover=True)
        if i > 0:  # debug
            print("  ⚠️ Warning!")  # debug
        i += 1  # debug


def update_contract_data(type):
    """更新指定合约类型数据"""
    beginDate = datetime.strptime(lastUpdated.get(
        type, [defaultStartDate])[0], "%Y%m%d").date()
    endDate = datetime.now(pytz.timezone("Asia/Shanghai")).date()
    duo_datas = {}
    kong_datas = {}
    print("🛰 Update %s ~ %s %s ……" % (beginDate, endDate, type))
    try:
        for i in range((endDate - beginDate).days + 1):
            day = beginDate + timedelta(days=i)
            key = day.strftime("%y%m")
            if i > 0:
                if day.day == 1:  # 每月开始，保存上月数据
                    write_txtfile(type+"-D", duo_datas)
                    write_txtfile(type+"-K", kong_datas)
                    txtfile.saveDict(lastlogfile, lastUpdated)
                    duo_datas = {}
                    kong_datas = {}

            if day.isoweekday() in [6, 7]:
                print("  💤 %s Weekend off" % day)
                lastUpdated[type] = [day.strftime("%Y%m%d")]
                continue

            dayStr = day.strftime("%Y-%m-%d")
            types = get_contracts(dayStr)  # 获取指定日期的可交易合约集合
            contracts = types.get(type)
            if contracts is None:
                lastUpdated[type] = [day.strftime("%Y%m%d")]
                print("  %s %s no contract" % (dayStr, type))
                continue

            market = contract_types[type]["market"]
            print("▶️ %s %s[%s] contracts：" %
                  (dayStr, type, market), contracts)

            dayDatas = get_contracts_data(dayStr, market, contracts)
            if dayDatas is not None:
                monthDatas = duo_datas.setdefault(key, {})
                monthDatas.update(dayDatas)
            dayDatas = get_contracts_data(
                dayStr, market, contracts, duo=False)
            if dayDatas is not None:
                monthDatas = kong_datas.setdefault(key, {})
                monthDatas.update(dayDatas)
            lastUpdated[type] = [day.strftime("%Y%m%d")]
    except requests.exceptions.RequestException as e:
        print("  🔥 Error: ", e)
    finally:
        if len(duo_datas) > 0:
            write_txtfile(type+"-D", duo_datas)
        if len(kong_datas) > 0:
            write_txtfile(type+"-K", kong_datas)
        txtfile.saveDict(lastlogfile, lastUpdated)


# main
print(datetime.now(pytz.timezone("Asia/Shanghai")
                   ).strftime("📅 %Y-%m-%d %A\n⏰ %H:%M:%S %Z"))

make_dirs(temp_dir)
make_dirs(dist_dir)

response = requests.get(cache_url)
if response.status_code == 200:
    zipFile = "%s.zip" % temp_dir
    with open(zipFile, "wb") as code:
        code.write(response.content)
    shutil.unpack_archive(zipFile, temp_dir)

if os.path.exists(lastlogfile):
    lastUpdated = txtfile.loadDict(lastlogfile)

for type in contract_types:
    update_contract_data(type)

shutil.make_archive(dist_dir+"/qhcjcc", "zip", root_dir=temp_dir)
