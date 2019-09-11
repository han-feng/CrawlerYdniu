#!/usr/bin/python
# python 3.7
# 指定目录下文件索引页生成工具
import os

# requirements: Jinja2
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
defaultTemplate = env.get_template('default.html')


def create(root, context={}, *, encoding="utf-8"):
    '''创建指定目录下的索引文件（index.html)
    :param root: 要生成索引文件的根目录
    :param context: 上线文参数，可以在模板文件（index.tmpl）中使用
    :param encoding: 索引文件编码格式
    '''
    for dirpath, dirnames, filenames in os.walk(root):
        files = []
        subdirs = []
        for subdir in dirnames:
            subdirs.append(subdir)
        for filename in filenames:
            if filename != "index.html":
                files.append(filename)
        # TODO 补充数据：相对于 root 的文件全路径名称，文件绝对路径名称，文件修改时间......
        # 排序：文件名、大小、修改时间
        text = defaultTemplate.render(
            {"context": context, "files": files, "subdirs": subdirs})
        with open(os.path.join(dirpath, "index.html"), "w", encoding=encoding) as f:
            f.write(text)


def listFiles(root, filterString, sort, subdir):

    pass


create("target")
