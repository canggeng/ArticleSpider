#! /bin/bash

__author__ = 'zzj'

# pycharm不直接支持scrapy，所以用main来调用函数的方式，进行各种调试
from scrapy.cmdline import execute

import sys
import os

# 获取此文件父目录的路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute(["scrapy", "crawl", "jobbole"])