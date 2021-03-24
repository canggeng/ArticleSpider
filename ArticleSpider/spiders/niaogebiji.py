import json

import scrapy
from scrapy import Request, FormRequest


class NiaogebijiSpider(scrapy.Spider):
    name = 'niaogebiji'
    allowed_domains = ['www.niaogebiji.com']
    start_urls = ['http://www.niaogebiji.com/']

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57'

    common_header = {
        "HOST": "www.niaogebiji.com",
        'User-Agent': user_agent,
    }

    login_header = {
        "HOST": "account.niaogebiji.com",
        "Referer": "https://account.niaogebiji.com/account/login",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        'User-Agent': user_agent,
    }

    def parse(self, response):
        pass

    # spider都是以start_requests()作为开始入口
    def start_requests(self):
        post_url = 'https://account.niaogebiji.com/account/loginViaPwd/'
        post_data = {
            'username': '13677647398',
            'password': '8evykxio'
        }
        yield from [FormRequest(url=post_url, formdata=post_data, headers=self.login_header, callback=self.check_login)]

    def check_login(self, response):
        result = json.loads(response.text)
        if result['return_code'] == '200' and result['return_msg'] == 'success':
            for url in self.start_urls:
                yield Request(url, dont_filter=True, headers=self.common_header)