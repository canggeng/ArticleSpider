#! /bin/bash

__author__ = 'zzj'

import datetime
import hashlib
import json

import MySQLdb
from scrapy.utils.project import get_project_settings
from selenium.webdriver.chrome.options import Options
from twisted.enterprise import adbapi

settings = get_project_settings()


def get_md5(url):
    # 如果为str就是unicode，需要编码
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def serilize_date(item):
    for key, obj in item.items():
        if isinstance(obj, datetime.datetime):
            item[key] = obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            item[key] = obj.strftime('%Y-%m-%d')
    return item


def unserilize_date(item):
    for key, obj in item.items():
        try:
            item[key] = datetime.datetime.strptime(obj, "%Y-%m-%d %H:%M:%S")
        except Exception as e1:
            try:
                item[key] = datetime.datetime.strptime(obj, "%Y-%m-%d")
            except Exception as e2:
                continue
    return item


def css_none_to_empty_str(value):
    if not value:
        value = ' '

    return value


def get_mysql_conn():
    conn = MySQLdb.connect(host=settings['MYSQL_HOST'], user=settings['MYSQL_USER'],
                           password=settings['MYSQL_PASSWORD'], database=settings['MYSQL_DBNAME'],
                           port=settings['MYSQL_PORT'], charset="utf8")

    return conn


def get_dbpool():
    dbparams = dict(
        host=settings['MYSQL_HOST'],
        db=settings['MYSQL_DBNAME'],
        user=settings['MYSQL_USER'],
        passwd=settings['MYSQL_PASSWORD'],
        port=settings['MYSQL_PORT'],
        charset='utf8',
        cursorclass=MySQLdb.cursors.DictCursor,
        use_unicode=True,
    )
    # 异步数据连接池
    # 第一个参数是要用到的mysql驱动模块
    dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
    return dbpool


def reliable_chrome_options():
    options = Options()
    # 隐藏 正在受到自动软件的控制 这几个字
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # 防止被识别出来使用的selenium
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument('--headless')

    return options