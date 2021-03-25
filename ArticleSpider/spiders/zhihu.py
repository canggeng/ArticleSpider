import datetime
import json
import re
from time import sleep

import scrapy
from scrapy import Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ArticleSpider.items import ZhihuQuestionItem, BaseItemLoader, ZhihuAnswerItem
from ArticleSpider.utils.common import css_none_to_empty_str


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
        sleep(1)
        browser.find_element_by_xpath('//div[@class="SignFlow-tab"]').click()
        sleep(1)

        # 获取登录用户名
        elem = browser.find_element_by_name("username")
        elem.clear()  # 清空
        elem.send_keys("13677647398")  # 自动填值
        # elem.send_keys(Keys.RETURN)  # 回车

        sleep(1)

        # 获取登录密码
        elem = browser.find_element_by_name("password")
        elem.clear()
        elem.send_keys("8evykxio")
        # elem.send_keys(Keys.RETURN)  # 回车

        sleep(1)

        print("开始登陆...")
        # Button SignFlow-submitButton Button--primary Button--blue
        # elem = browser.find_element_by_css_selector(".Button.SignFlow-submitButton.Button--primary.Button--blue")
        browser.find_element_by_css_selector('button[type="submit"]').submit()
        # elem = browser.find_element_by_xpath(r'//button[@class="Button SignFlow-submitButton Button--primary Button--blue"]')
        # elem.click()

        print("开始休眠...")

        # 显示等待   选择“首页”选项
        element = WebDriverWait(browser, 15).until(EC.title_contains(u'首页'))
        return element

        print("已选择...")

    except TimeoutException:
        print("Time Out")
    except NoSuchElementException:
        print("No Element")


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    # question的第一页answer的请求url
    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled&limit={1}&offset={2}&platform=desktop&sort_by=default'

    def parse(self, response):
        all_urls = response.css('a::attr(href)').extract()
        all_urls = self.available_urls(all_urls)
        for url in all_urls:
            match_obj = re.match('(.*question/(\d+))(/|$)', url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                yield Request(request_url, headers=self.header, cookies=self.requests_cookies,
                              callback=self.parse_question)
                break
            # else:
            # 如果不是question页面则直接进一步跟踪
            # yield Request(url, headers=self.header, cookies=self.requests_cookies, callback=self.parse)

    def parse_question(self, response):
        item_loader = BaseItemLoader(item=ZhihuQuestionItem(), response=response)
        zhihu_id = re.match('(.*question/(\d+))(/|$)', response.url).group(2)
        item_loader.add_value('zhihu_id', zhihu_id)
        item_loader.add_css('topics', '.QuestionPage > meta[itemprop=keywords]::attr(content)')
        item_loader.add_value('url', response.url)
        item_loader.add_css('title', '.QuestionPage > meta[itemprop=name]::attr(content)')
        item_loader.add_css('content', '.css-eew49z span::text', css_none_to_empty_str)
        item_loader.add_css('create_time', '.QuestionPage > meta[itemprop=dateCreated]::attr(content)')
        item_loader.add_css('update_time', '.QuestionPage > meta[itemprop=dateModified]::attr(content)')
        item_loader.add_css('answer_num', '.QuestionPage > meta[itemprop=answerCount]::attr(content)')
        item_loader.add_css('comments_num', '.QuestionPage > meta[itemprop=commentCount]::attr(content)')
        item_loader.add_css('watch_user_num', '.QuestionPage > meta[itemprop="zhihu:followerCount"]::attr(content)')
        item_loader.add_css('click_num', '.NumberBoard > div.NumberBoard-item strong::attr(title)')
        item_loader.add_value('crawl_time', datetime.datetime.now())

        yield Request(self.start_answer_url.format(zhihu_id, 20, 0), headers=self.header, cookies=self.requests_cookies,
                      callback=self.parse_answer)
        yield item_loader.load_item()

    def parse_answer(self, response):
        response_data = json.loads(response.text)
        is_end = response_data['paging']['is_end']
        next_page = response_data['paging']['next']

        for data in response_data['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = data['id']
            answer_item['url'] = data['url']
            answer_item['question_id'] = data['question']['id']
            answer_item['author_id'] = data['author']['id'] if data['author']['id'] else 0
            answer_item['content'] = data['content']
            answer_item['parise_num'] = data['voteup_count']
            answer_item['comments_num'] = data['comment_count']
            answer_item['create_time'] = datetime.datetime.fromtimestamp(int(data['created_time']))
            answer_item['update_time'] = datetime.datetime.fromtimestamp(int(data['updated_time']))
            answer_item['crawl_time'] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield Request(next_page, headers=self.header,
                          cookies=self.requests_cookies,
                          callback=self.parse_answer)

    def start_requests(self):
        self.header = {
            "HOST": "www.zhihu.com",
            "Referer": "https://www.zhizhu.com",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57'
        }
        self.requests_cookies = {}
        self.cookies_loaded = False

        self.load_cookies()
        yield Request(self.start_urls[0], headers=self.header, cookies=self.requests_cookies, callback=self.check_login)

    def load_cookies(self):
        try:
            with open('zhihu_cookies.txt', 'r') as f:
                cookies = f.read()
                self.requests_cookies = json.loads(cookies)
                return True
        except:
            return False

    def save_cookies(self):
        with open('zhihu_cookies.txt', 'w') as f:
            f.write(json.dumps(self.requests_cookies))

    def check_login(self, response):
        title = response.css('title').extract_first()
        if title.find('首页') == -1:
            self.login()
        for url in self.start_urls:
            yield Request(url, dont_filter=True, headers=self.header, cookies=self.requests_cookies)

    def is_index(self, response):
        title = response.css('title').extract()
        print(title)

    def login(self):
        options = Options()
        # 隐藏 正在受到自动软件的控制 这几个字
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # 防止被识别出来使用的selenium
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument('--headless')

        browser = webdriver.Chrome(executable_path=self.settings.get('CHROME_DRIVER'), options=options)
        url = 'https://www.zhihu.com/signin?next=%2F'
        # url = 'https://bot.sannysoft.com/'
        if login(browser, url):
            cookies = browser.get_cookies()
            url = browser.current_url
            agent = browser.execute_script("return navigator.userAgent")
            self.header['User-Agent'] = agent
            browser.quit()

            for cookie in cookies:
                self.requests_cookies[cookie['name']] = cookie['value']
                self.save_cookies()

        else:
            browser.quit()

    def available_urls(self, all_urls):
        all_urls = list(filter(lambda url: False if url == '/' else True, all_urls))
        all_urls = list(map(self.fit_url, all_urls))
        return all_urls

    def fit_url(self, url):
        if url.startswith('//'):
            url = url.replace('//', 'https://')
        elif re.match('/.*', url):
            url = re.sub('^/?', 'https://www.zhihu.com/', url, 1)
        return url
