#!/usr/bin/python
# python 3.7
# 指定目录下文件索引页生成工具
import os
from datetime import datetime
import txtfile

# requirements: pytz
import pytz


# 创建索引
def create(baseDir, provinces):
    filenames = _getTxtFiles(baseDir)
    filenames.sort()

    # 形成省份与文件关系dict
    province_file = {}
    for filename in filenames:
        province = os.path.splitext(filename)[0][:-6]
        files = province_file.setdefault(province, [])
        files.append(filename)

    table1 = "  <table>\n  <tr><th>省份</th><th>(10,<s>11</s>) or (<s>10</s>,11)</th><th>(10,11) or (<s>10</s>,<s>11</s>)</th><th>期数</th><th>起始期次</th><th>结束期次</th></tr>\n"
    for province in province_file.keys():
        files = province_file[province]
        province_name = provinces[province]
        # 统计数据
        newfiles = []
        for file in files:
            newfiles.append(os.path.join(baseDir, file))
        (counter, keylen, startkey, endkey) = _count10And11(newfiles)
        # 输出
        table1 += '    <tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n' % (
            province_name, counter[0], counter[1], keylen, startkey, endkey)
    table1 += "  </table>"

    table2 = "  <table>\n  <tr><th>数据名称</th><th>更新时间</th></tr>\n"
    for filename in filenames:
        # 获取标题
        name = os.path.splitext(filename)[0]
        province = name[:-6]
        month = name[-6:]
        title = provinces[province] + " " + month
        # 获取更新时间
        t = os.stat(os.path.join(baseDir, filename)).st_mtime
        t = datetime.fromtimestamp(t, pytz.timezone(
            "Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
        # 输出
        table2 += '    <tr><td><a href="%s">%s</a></td><td>%s</td></tr>\n' % (
            filename, title, t)
    table2 += "  </table>"
    lines = '''
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no"/>
<style>
table {
    border-collapse:collapse;
}
td,th {
    border: 1px solid #ccc;
    padding: 2px 15px;
    text-align: center;
}
tr:nth-child(odd) {
    background: #eff;
}
s {
    color: #ccc;
}
</style>
</head>
<body>
<h3>统计数据</h3>
%s
<h3>原始数据</h3>
%s
</body>
</html>
''' % (table1, table2)
    #
    with open(os.path.join(baseDir, "index.html"), "w", encoding='utf-8') as f:
        f.write(lines)
# create end


# 获取指定目录下的txt文件名列表
def _getTxtFiles(baseDir):
    files = []
    for dirpath, dirnames, filenames in os.walk(baseDir):
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".txt":
                files.append(filename)
        break
    return files
# getTxtFiles end


# 10&11统计
def _count10And11(files):
    dict = {}
    for file in files:
        dict.update(txtfile.loadDict(file))

    keys = list(dict.keys())
    counter = _10And11Counter()
    for datas in dict.values():
        e10 = False
        e11 = False
        for data in datas:
            if data == "10":
                e10 = True
            elif data == "11":
                e11 = True
        if e10 == True and e11 == False:
            symbol = "A"
        elif e10 == False and e11 == True:
            symbol = "A"
        else:
            symbol = "B"
        counter.add(symbol)
    counter.end()
    return (counter._counters, len(keys), keys[0], keys[-1])
# _count10And11 end


class _10And11Counter:
    _symbols = ["A", "B"]

    def __init__(self):
        self._counters = [[0, 0, 0], [0, 0, 0]]
        self._curSymbolIndex = 0
        self._curCounter = 0

    def _switch(self):
        if self._curCounter > 0:
            counters = self._counters[self._curSymbolIndex]
            # 填充计数器位置
            if self._curCounter > 3:
                while len(counters) < self._curCounter:
                    counters.append(0)
            counters[self._curCounter-1] += 1

        self._curCounter = 1
        if self._curSymbolIndex == 0:
            self._curSymbolIndex = 1
        else:
            self._curSymbolIndex = 0

    def add(self, symbol):
        if not symbol in self._symbols:
            print("无效的符号‘%s’" % symbol)
            return
        if self._symbols[self._curSymbolIndex] == symbol:
            self._curCounter += 1
        else:
            self._switch()

    def end(self):
        self._switch()
        self._curCounter = 0
