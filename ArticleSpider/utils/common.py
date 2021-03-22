#! /bin/bash

__author__ = 'zzj'

import hashlib


def get_md5(url):
    # 如果为str就是unicode，需要编码
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == "__main__":
    print(get_md5("http://www.sina.com.cn".encode("utf-8")))