#! /bin/bash

__author__ = 'zzj'

import json
from http import cookiejar

import requests
import http.cookies


def is_login(header, session):
    setting_url = 'http://www.niaogebiji.com/pc/center/setting/'
    response = session.get(setting_url, headers=header, allow_redirects=False)
    if response.status_code == '200':
        return True
    return False


def niaogebiji_login(header, session):
    # 手机验证码登录
    post_url = 'https://account.niaogebiji.com/account/loginViaPwd/'
    post_data = {
        'username': '13677647398',
        'password': '8evykxio'
    }
    response = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()


def common_header():
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57'

    return {
        "HOST": "www.niaogebiji.com",
        'User-Agent': user_agent,
    }


def login_header():
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57'

    return {
        "HOST": "account.niaogebiji.com",
        "Referer": "https://account.niaogebiji.com/account/login?redirect=http://www.niaogebiji.com/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        'User-Agent': user_agent,
    }


def niaogebiji_myorder(header, session):
    myorder_ur = 'https://order.niaogebiji.com/myorder'
    response = session.get(myorder_ur, headers=header)
    pass


def init_session():
    session = requests.session()
    session.cookies = cookiejar.LWPCookieJar(filename="cookies.txt")
    # 加载本地cookie文件
    try:
        session.cookies.load("cookies.txt")
    except:
        print("cookie未能加装")
    finally:
        return session


if __name__ == '__main__':
    common_header = common_header()
    login_header = login_header()
    session = init_session()

    if not is_login(common_header, session):
        niaogebiji_login(login_header, session)
        print(is_login(common_header, session))
