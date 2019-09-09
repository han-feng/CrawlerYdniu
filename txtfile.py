#!/usr/bin/python
# python 3.7
# 文本文件操作工具
import os


# 从文本文件加载 Dictionary 对象
def loadDict(filePath):
    dict = {}
    for line in open(filePath, "r", encoding='utf-8'):
        line = line.strip()
        if len(line) <= 0 or line.find(",") < 0:
            continue
        data = line.split(",")
        dict[data[0].strip()] = data[1:]
    return dict
# loadDict end


# 转换 Dictionary 为文本内容
def _dictToLines(dict):
    lines = []
    for key in dict.keys():
        value = [key] + dict[key]
        line = ",".join(value)+"\n"
        lines.append(line)
    return lines
# _dictToLines end


# 保存 Dictionary 到文本文件
def saveDict(filePath, dict):
    lines = _dictToLines(dict)
    with open(filePath, "w", encoding='utf-8') as f:
        f.writelines(lines)
    pass
# saveDict end


# 追加 Dictionary 到文本文件，不会覆盖已存在的相同 key 值数据
def appendDict(filePath, dict):
    if not os.path.exists(filePath):
        saveDict(filePath, dict)
        return
    oldDict = loadDict(filePath)
    newDict = {}
    for key in dict.keys():
        if not oldDict.__contains__(key):
            newDict[key] = dict[key]
    lines = _dictToLines(newDict)
    with open(filePath, "a", encoding='utf-8') as f:
        f.writelines(lines)
# appendDict end


# 批量建立文件夹
def _makeDirs(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
# makeDirs end


# Test
def _test():
    _makeDirs("target/test")

    dict = {}
    for n in range(10):
        value = []
        for i in range(n, n+10):
            value.append("V"+str(i))
        dict["K"+str(n)] = value
    saveDict("target/test/test.txt", dict)
    print(loadDict("target/test/test.txt"))

    dict = {}
    for n in range(5, 15):
        value = []
        for i in range(n, n+10):
            value.append("V"+str(i))
        dict["K"+str(n)] = value
    appendDict("target/test/test.txt", dict)
    print(loadDict("target/test/test.txt"))
