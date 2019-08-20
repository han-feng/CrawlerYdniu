#!/usr/bin/python
# python 3.7
# 指定目录下文件索引页生成工具
import os
import json
from datetime import datetime

# requirements: pytz
import pytz


# 创建索引
def create(baseDir):
    filenames = _getTxtFiles(baseDir)
    filenames.sort()

    # 加载 index.json
    with open(os.path.join(baseDir, "index.json"), "r", encoding='utf-8') as f:
        data = json.load(f)

    links = "  <ul>\n"
    for filename in filenames:
        t = os.stat(os.path.join(baseDir, filename)).st_mtime
        t = datetime.fromtimestamp(t, pytz.timezone(
            "Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %Z%z")
        t2 = data[filename]["createTime"]
        links += '    <li><a href="%s">%s</a> (%s - %s)</li>\n' % (
            filename, filename, t, t2)
    links += "  </ul>"
    lines = '''
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no"/>
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
