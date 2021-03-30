#! /bin/bash

__author__ = 'zzj'

# https://www.kuaidaili.com/free/

# 代理地址爬取和存入数据库
import re
from time import sleep

import requests
from scrapy import Selector

from ArticleSpider.utils.common import get_mysql_conn, settings


class CrawlKuaidaili:
    def __init__(self):
        self.url = 'https://www.kuaidaili.com/free/inha/{0}/'
        self.headers = {
            'User-Agent': settings['USER_AGENT']
        }
        self.page_nums = self.get_page_nums()

    def get_page_nums(self):
        # 获取需要爬取的页数
        res = requests.get(self.url.format(1), headers=self.headers)
        selector = Selector(text=res.text)
        page_nums = int(selector.xpath('//div[@id="listnav"]//li[last()-1]/a/text()').extract_first())
        return page_nums

    def crawl_kuaidaili(self):
        # 爬取整个网站
        for i in range(1, self.page_nums + 1):
            self.crawl_page(i)

    def crawl_page(self, page_num):
        # 爬取单独一个页面
        sleep(1)
        res = requests.get(self.url.format(page_num), headers=self.headers, allow_redirects=False)
        selector = Selector(text=res.text)
        ips = selector.css('tbody td[data-title="IP"]::text').extract()
        ports = selector.css('tbody td[data-title="PORT"]::text').extract()
        speeds = selector.css('tbody td[data-title="响应速度"]::text').extract()
        speeds = self.convert_speed(speeds)
        proxy_types = selector.css('tbody td[data-title="类型"]::text').extract()

        self.save_proxy_ip(ips, ports, speeds, proxy_types)

    def save_proxy_ip(self, ips, ports, speeds, proxy_types):
        # 保存每行数据到数据库
        if len(ips) == len(ports) == len(speeds) == len(proxy_types):
            for i in range(len(ips)):
                proxy_ip = ProxyIP(ips[i], ports[i], speeds[i], proxy_types[i])
                proxy_ip.save()

    def convert_speed(self, speeds):
        s = []
        for speed in speeds:
            matched = re.match(r"(.*)秒", speed)
            if matched:
                s.append(float(matched.group(1)))
        return s


# 代理地址数据库读取和格式化组装
class GetProxyIP:
    @staticmethod
    def get_random_ip():
        proxy_ip = ProxyIP.get_random()
        return str(proxy_ip)


class ProxyIP:
    def __init__(self, ip='0.0.0.0', port='8080', speed=0, proxy_type='HTTP'):
        # 创建数据库连接，获取光标
        self.ip = ip
        self.port = port
        self.speed = speed
        self.proxy_type = proxy_type

    def __str__(self):
        return f'http://{self.ip}:{self.port}'

    def get_properties(self):
        return [p for p in dir(self) if not p.startswith('_') and not callable(getattr(self, p))]

    @staticmethod
    def query(sql, params=tuple(), commit=False, fetchone=True):
        conn = get_mysql_conn()
        cursor = conn.cursor()
        try:
            res_num = cursor.execute(sql, params)
            if commit:
                conn.commit()
            elif fetchone:
                one = cursor.fetchone()
                return one
            else:
                all = cursor.fetchall()
                return all
        except Exception as e:
            print(e)
        finally:
            conn.close()

    def save(self):
        properties = self.get_properties()
        columns = ''
        values = ''
        update = ''
        params = []
        for p in properties:
            columns += (p + ', ') if p != properties[-1] else p
            values += '%s, ' if p != properties[-1] else '%s'
            update += (p + '=values(' + p + '), ') if p != properties[-1] else (p + '=values(' + p + ')')
            params.append(getattr(self, p, ''))

        insert_sql = """
                            insert into proxy_ip({0}) values({1}) ON DUPLICATE KEY UPDATE 
                            {2}
                        """.format(columns, values, update)

        self.query(insert_sql, params, commit=True)

    @classmethod
    def get(cls, ip):
        query_sql = """
            select * from proxy_ip where ip=%s
        """
        params = (ip,)
        one = cls.query(query_sql, params)
        return cls(*one)

    @classmethod
    def get_random(cls):
        query_sql = """
            select * from proxy_ip order by RAND() limit 1
        """
        rand = cls.query(query_sql)
        return cls(*rand)

    @classmethod
    def get_all(cls, limit=100):
        query_sql = """
                select * from proxy_ip limit %s
            """
        params = (limit, )
        all = cls.query(query_sql, params, fetchone=False)
        item_list = []
        for one in all:
            item = cls(*one)
            item_list.append(item)
        return item_list

# if __name__ == '__main__':
#     # crawl = CrawlKuaidaili()
#     # crawl.crawl_kuaidaili()
#     p = ProxyIP('10.10.10.10', 123, 3.13, 'http')
#     c = ProxyIP.get_all()
#     pass
    # print(dir(ProxyIP))
    # print('----------------------------')
    # print(dir(p))
    # print('----------------------------')
    # print(ProxyIP.__dict__)
    # print('----------------------------')
    # print(p.__dict__)
    # p.save()
