#!/usr/bin/python
# python 3.7
# 文本文件操作工具


# 从文本文件加载 Dictionary 对象
def loadDict(filePath):
    dict = {}
    for line in open(filePath):
        line = line.strip()
        if len(line) <= 0 or line.find(",") < 0:
            continue
        data = line.split(",")
        dict[data[0].strip()] = data[1:]
    return dict

# 保存 Dictionary 到文本文件


def saveDict(filePath, dict):
    pass
