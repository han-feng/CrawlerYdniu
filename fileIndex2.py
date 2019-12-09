#!/usr/bin/python
# python 3.7
# 指定目录下文件索引页生成工具
import os
from datetime import datetime
import txtfile

# requirements: pytz
import pytz

startIndex = 14
endIndex = 21
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

    table1 = "  <table>\n  <tr><th>省份</th>"
    for i in dataIndexs:
        table1 += "<th>%s</th>" % i
    table1 += "<th>期数</th><th>起始期次</th><th>结束期次</th><th>异常</th></tr>\n"
    for province in province_file.keys():
        files = province_file[province]
        province_name = provinces[province]
        # 统计数据
        newfiles = []
        for file in files:
            newfiles.append(os.path.join(baseDir, file))
        (counter, keylen, startkey, endkey, error) = _count(newfiles)
        if error != "":
            error = "<ul style='color:red'>" + error + "</ul>"
        # 输出
        table1 += '    <tr><td>%s</td>' % province_name
        for i in dataIndexs:
            c = counter[i - startIndex]
            s = "(%s/%s)" % (c[0], c[1])
            if c[1] > 0:
                s = "%s %s" % (c[0]*100//c[1], s)
            table1 += "<td>%s</td>" % s
        table1 += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n' % (
            keylen, startkey, endkey, error)
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
    for datas in dict.values():
        counter.add(datas)
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
        self._counters = []
        for i in dataIndexs:
            self._counters.append([0, 0])

    def add(self, values):
        # print("[datas] %s" % values)
        pass
