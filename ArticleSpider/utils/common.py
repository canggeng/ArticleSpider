#! /bin/bash

__author__ = 'zzj'

import datetime
import hashlib
import json


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