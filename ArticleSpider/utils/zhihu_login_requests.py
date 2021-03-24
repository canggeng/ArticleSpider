#! /bin/bash

__author__ = 'zzj'

from time import sleep

from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

settings = get_project_settings()


def login(browser, url):
    browser.get(url=url)

    # sleep(2)
    # browser.find_element_by_css_selector('input[name="username"]').send_keys("13677647398")
    # sleep(5)
    # browser.find_element_by_css_selector('input[name="password"]').send_keys("8evykxio")
    # sleep(5)
    # browser.find_element_by_css_selector('button[type="submit"]').submit()
    # sleep(2)

    try:
        sleep(2)
        browser.find_element_by_xpath('//div[@class="SignFlow-tab"]').click()
        sleep(2)

        # 获取登录用户名
        elem = browser.find_element_by_name("username")
        elem.clear()  # 清空
        elem.send_keys("13677647398")  # 自动填值
        elem.send_keys(Keys.RETURN)  # 回车

        sleep(3)

        # 获取登录密码
        elem = browser.find_element_by_name("password")
        elem.clear()
        elem.send_keys("8evykxio")
        elem.send_keys(Keys.RETURN)  # 回车

        sleep(2)

        print("开始登陆...")
        # Button SignFlow-submitButton Button--primary Button--blue
        # elem = browser.find_element_by_css_selector(".Button.SignFlow-submitButton.Button--primary.Button--blue")
        browser.find_element_by_css_selector('button[type="submit"]').submit()
        # elem = browser.find_element_by_xpath(r'//button[@class="Button SignFlow-submitButton Button--primary Button--blue"]')
        # elem.click()

        print("开始休眠...")
        # 显示等待   选择“首页”选项
        element = WebDriverWait(browser, 15).until(EC.title_contains(u'首页'))
        print("已选择...")

    except TimeoutException:
        print("Time Out")
    except NoSuchElementException:
        print("No Element")





if __name__ == '__main__':
    options = Options()
    # 隐藏 正在受到自动软件的控制 这几个字
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")

    browser = webdriver.Chrome(executable_path=settings['CHROME_DRIVER'], options=options)
    # url = 'https://www.zhihu.com/signin?next=%2F'
    url = 'https://bot.sannysoft.com/'
    login(browser, url)