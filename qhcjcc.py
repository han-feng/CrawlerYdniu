#!/usr/bin/python
# python 3.7
# 期货成交持仓

import json

import requests


def get_url_duo(date):
    url = "http://m.data.eastmoney.com/api/futures/GetQhcjcc?market=069001007&date=" \
        + date \
        + "&contract=A2105&name=%E5%A4%9A%E5%A4%B4%E6%8C%81%E4%BB%93%E9%BE%99%E8%99%8E%E6%A6%9C&page=1"
    return url


def get_url_kong(date):
    url = "http://m.data.eastmoney.com/api/futures/GetQhcjcc?market=069001007&date=" \
        + date \
        + "&contract=A2105&name=%E7%A9%BA%E5%A4%B4%E6%8C%81%E4%BB%93%E9%BE%99%E8%99%8E%E6%A6%9C&page=1"
    return url


def get_datas(url):
    response = requests.get(url)
    datas = json.loads(response.text)
    for data in datas:
        print(data["Code"], data["Name"], data["Ddl"],
              data["DdlZJ"], data["Kdl"], data["KdlZJ"])

get_datas(get_url_duo("2020-12-16"))
print()
get_datas(get_url_kong("2020-12-16"))
