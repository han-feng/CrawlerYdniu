#!/usr/bin/python
# python 3.7
# 指定目录下文件索引页生成工具
import os
from datetime import datetime
import txtfile

# requirements: pytz
import pytz

startIndex = 10
endIndex = 25
dataIndexs = range(startIndex, endIndex+1)


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

    table1 = "  <table>\n  <tr><th>省份</th><th></th><th>期次号</th>"
    for i in dataIndexs:
        table1 += "<th>%s</th>" % i
    table1 += "</tr>\n"
    for province in province_file.keys():
        files = province_file[province]
        province_name = provinces[province]
        # 统计数据
        newfiles = []
        for file in files:
            newfiles.append(os.path.join(baseDir, file))
        (counters, keylen, startkey, endkey, error) = _count(newfiles)
        l = len(counters)
        if error != "":
            error = "<ul style='color:red'>" + error + "</ul>"
        # 输出
        table1 += '    <tr><td rowspan="%d">%s</td>' % (l, province_name)
        table1 += '<td rowspan="%d">共%s期<br>(%s ~ %s)<br>%s</td>' % (
            l, keylen, startkey, endkey, error)
        for i, counter in enumerate(counters):
            if i > 0:
                table1 += "<tr>"
            table1 += "<td>%d~%d</td>" % (i*3+1, i*3+3)
            for i in dataIndexs:
                c = counter[i - startIndex]
                table1 += "<td>%s</td>" % c.percent()
            table1 += '</tr>\n'
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


# 按省份全量统计
def _count(files):
    dict = {}
    for file in files:
        dict.update(txtfile.loadDict(file))

    counter = _R8Counter()
    for key, value in dict.items():
        counter.add(key, value)
    keys = list(dict.keys())
    # 数据连贯性检查
    error = keyscheck(keys)
    return (counter._counters, len(keys), keys[0], keys[-1], error)
# _count end


# 日期格式转换
def strpdate(strdate):
    if len(strdate) >= 8:
        date = datetime.strptime(strdate[:8], "%Y%m%d")
    else:
        date = datetime.strptime(strdate[:6], "%y%m%d")
    return date


# 数据连贯性检查
def keyscheck(keys):
    oldkey = ""
    error = ""
    for key in keys:
        key = key.strip()
        if key == "":
            continue
        if oldkey == "":
            oldkey = key
            continue
        # 日期连贯
        # if key[-2:] == "01":
            # olddate = strpdate(oldkey[:-2])
            # date = strpdate(key[:-2])
            # if (date - olddate).days != 1:
            #     error += "<li>期数不连贯 %s, %s</li>" % (oldkey, key)
        # else:
        if key[-2:] != "01":
            # 末尾数字连贯
            oldnum = int(oldkey[-2:])
            num = int(key[-2:])
            if oldnum + 1 != num:
                error += "<li>期数不连贯 %s, %s</li>" % (oldkey, key)
        oldkey = key
    return error
# keyscheck end


class _R8Counter:

    def __init__(self):
        self._composeIndex = {}
        self._counters = []

    def _createCounters(self):
        counters = []
        for i in dataIndexs:
            counters.append(self.Counter())
        return counters

    def add(self, no, values):
        # print("[datas] %s" % values)
        values.sort()
        # 列举组合
        l = len(values)
        for i in range(0, l):
            for j in range(i+1, l):
                for k in range(j + 1, l):
                    key = "%s-%s-%s" % (values[i], values[j], values[k])
                    keys = set([values[i], values[j], values[k]])
                    # 创建 Compose 对象
                    self._composeIndex.setdefault(
                        key, self.Compose(keys, self))
        # 遍历所有 compose
        for compose in self._composeIndex.values():
            compose.add(no, values)

    # 统计计数器加一，isAll：全中或全不中
    def _addCount(self, no, count, isAll):
        if not dataIndexs.__contains__(count):
            return
        # 计算时段
        i = (int(no[-2:]) - 1) // 3
        while len(self._counters) <= i:
            self._counters.append(self._createCounters())
        # 获取 counters
        counters = self._counters[i]
        c = counters[count - startIndex]
        c.add(isAll)

    class Counter:
        count = 0
        total = 0

        def add(self, isAll):
            self.total += 1
            if isAll:
                self.count += 1

        def percent(self):
            s = ""  # "(%s/%s)" % (self.count, self.total)
            if self.total != 0:
                s = "%.2f%% %s" % (self.count * 100 / self.total, s)
            return s

    class Compose:

        def __init__(self, keys, r8counter):
            self._keys = keys.copy()
            self._currCount = 1
            self.parent = r8counter

        def add(self, no, values):
            c = self._keys.intersection(values)  # 计算交集
            if len(c) == 0:
                if self._currCount > 0:
                    # 全不中的情况，计数终止，重置
                    self.parent._addCount(no, self._currCount, True)
                    self._currCount = 0
            elif len(c) == 3:
                # 全中的情况
                self.parent._addCount(no, self._currCount, True)
                self._currCount += 1
            else:
                # 部分中的情况
                self.parent._addCount(no, self._currCount, False)
                self._currCount += 1
