#!/usr/bin/python
# python 3.7
# 数据检查工具
import os
import operator
import fileIndex
import txtfile

dataDir = ["target", "target/11-5"]


def formatValue(x):
    if len(x) == 1:
        return "0" + x
    else:
        return x


def check():
    # 遍历数据目录1，核对数据目录2中的同名文件
    filenames = fileIndex._getTxtFiles(dataDir[0])
    for filename in filenames:
        data1 = txtfile.loadDict(os.path.join(dataDir[0], filename))
        file2 = os.path.join(dataDir[1], filename)
        if os.path.exists(file2):
            data2 = txtfile.loadDict(file2)
            # 只需核对 data1 中的数据在 data2 中是否存在即可
            for (key, value) in data1.items():
                key = key[2:]
                if not data2.__contains__(key):
                    print(file2, "缺少数据", key)
                else:
                    value2 = list(map(formatValue, data2[key]))
                    if operator.ne(value, value2):
                        print(filename, value, value2, key)


check()
