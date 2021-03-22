import scrapy
import requests
import re
from urllib import parse

from ArticleSpider.items import JobBoleArticleItem
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['www.jobbole.com']
    start_urls = ['http://www.jobbole.com/keji/']

    def parse(self, response):
        # 1.解析列表页面的所有rul并交给scrapy下载后进行解析
        post_nodes = response.css('#stock-left-graphic .list-item')
        for post_node in post_nodes:
            image_url = post_node.css('img ::attr(src)').extract_first('')
            post_url = post_node.css('.content a::attr(href)').extract_first('')
            # Rquest()可以用meta={}字典项response中传递参数
            yield scrapy.Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': image_url},
                                 callback=self.parse_detail)
        # 2.提取下一页并交给scrapy进行下载
        front_next = response.css('.a1')
        for i in front_next:
            j = i.css('::text').extract_first()
            if j == '下一页' and i.css('::attr(href)').extract_first() != 'javascript:;':
                next_url = i.css('::attr(href)').extract_first()
                yield scrapy.Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 提取文章具体字段
        front_image_url = response.meta.get('front_image_url', '')
        header = response.xpath('//div[@class="article-head"]')[0]
        title = header.xpath('//h1[@class="title"]/text()').extract()[0]
        create_date = header.xpath('//div[@class="date"]/span[1]/text()').extract()[0]
        read_request = 'http://' + self.allowed_domains[0] + \
                       header.xpath('//div[@class="date"]/span[2]/script/@src').extract()[0]
        read_response = requests.get(read_request)
        read_response_content = read_response.text
        r = re.match(r".*?(\d+)", read_response_content)
        if r:
            read_nums = int(r.group(1))
        else:
            read_nums = 0
        # read_nums = read_nums.xpath('name(@src)')
        content = response.xpath('//div[@class="article-main"]')
        tags = response.xpath('//span[@id="51580"]/text()').extract()[0]

        article = JobBoleArticleItem()

        article['title'] = title
        article['create_date'] = create_date
        article['url'] = response.url
        article['url_object_id'] = get_md5(response.url)
        article['front_image_url'] = [front_image_url]
        article['read_nums'] = read_nums
        article['content'] = content
        article['tags'] = tags

        yield article
