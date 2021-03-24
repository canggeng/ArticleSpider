from time import sleep

import scrapy
from scrapy import Selector
from scrapy.utils.project import get_project_settings
from selenium import webdriver


class AiqichaSpider(scrapy.Spider):
    name = 'aiqicha'
    allowed_domains = ['aiqicha.baidu.com']
    start_urls = ['https://aiqicha.baidu.com/company_detail_32385292822723']

    def parse(self, response):
        pass

settings = get_project_settings()
chromedriver = settings.get('CHROME_DRIVER')
def login_blogs(url,name,password):
    # 创建一个driver对象
    driver = webdriver.Chrome(executable_path=chromedriver)
    try:
        driver.get(url)
        sleep(1)
        # 找到输入框和密码框，将用户名和密码输入
        # driver.find_element_by_id("LoginName").send_keys(name)
        # t = driver.find_element_by_link_text('更多 >').click()
        t = driver.find_element_by_css_selector('.zx-detail-basic-table')
        t = driver.find_element_by_css_selector('.zx-detail-basic-table').text
        t_list = t.split('\n')
        print(t_list)
        # driver.find_element_by_id("Password").send_keys(password)
        # # 找到登录按钮
        # driver.find_element_by_id("submitBtn").click()
        sleep(1)
        # 破解滑动验证码
        # crack_code(driver)
        sleep(5)
    finally:
        driver.close()


if __name__ == '__main__':
    # url = "https://aiqicha.baidu.com/company_detail_32385292822723"
    url = 'https://bot.sannysoft.com/'
    login_blogs(url,"qwer","1234")

# browser = webdriver.Chrome(executable_path=chromedriver)
#
# browser.get("https://www.zhihu.com/#signin")