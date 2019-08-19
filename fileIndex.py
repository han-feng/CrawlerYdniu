#!/usr/bin/python
# python 3.7
# 指定目录下文件索引页生成工具


# 默认 titleGetter 函数
def _defaultTitleGetter(title):
    return title


# 创建索引
def create(baseDir, excludes=["index.*"], *, titleGetter=_defaultTitleGetter):
    print(titleGetter("sd201908"))
# create end


create("target")
