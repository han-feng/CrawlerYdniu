#!/usr/bin/python
# python 3.7
# 指定目录下文件索引页生成工具
import os
from datetime import datetime
import txtfile

# requirements: pytz
import pytz


# 默认的TitleGetter实现
def _defaultTitleGetter(filename):
    return filename
# _defaultTitleGetter end


# 创建索引
def create(baseDir, *, titleGetter=_defaultTitleGetter):
    filenames = _getTxtFiles(baseDir)
    filenames.sort()
    links = "  <table>\n  <tr><th>数据名称</th><th>(10,<s>11</s>) or (<s>10</s>,11)</th><th>(10,11) or (<s>10</s>,<s>11</s>)</th><th>更新时间</th></tr>\n"
    for filename in filenames:
        # 获取标题
        title = titleGetter(filename)
        # 获取更新时间
        t = os.stat(os.path.join(baseDir, filename)).st_mtime
        t = datetime.fromtimestamp(t, pytz.timezone(
            "Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
        # 统计数据
        counter = _count10And11(os.path.join(baseDir, filename))
        # 输出
        links += '    <tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>\n' % (
            filename, title, counter[0], counter[1], t)
    links += "  </table>"
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
%s
</body>
</html>
''' % links
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
def _count10And11(filename):
    dict = txtfile.loadDict(filename)
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
    return counter._counters
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
