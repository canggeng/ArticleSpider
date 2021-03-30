import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ArticleSpider.items import BaseItemLoader, LagouJobItem
from ArticleSpider.utils.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=("gongsi/v1/j/\w+.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html.*'), callback='parse_job', follow=True),
    )

    def parse_job(self, response):
        job_item = BaseItemLoader(item=LagouJobItem(), response=response)

        job_item.add_css('title', '.job-name::attr(title)')
        job_item.add_value('url', response.url)
        job_item.add_value('url_object_id', get_md5(response.url))
        job_item.add_xpath('salary', '//*[@class=job_request]/h3/span[1]/text()')
        job_item.add_xpath('job_city', '//*[@class=job_request]/h3/span[2]/text()')
        job_item.add_xpath('work_years', '//*[@class=job_request]/h3/span[3]/text()')
        job_item.add_xpath('degree_need', '//*[@class=job_request]/h3/span[4]/text()')
        job_item.add_xpath('job_type', '//*[@class=job_request]/h3/span[5]/text()')
        job_item.add_css('publish_time', '.publish_time::text')
        job_item.add_css('job_advantage', '.job-advantage p::text')
        job_item.add_css('job_desc', '.job-detail::text')
        job_item.add_css('job_addr', '.work_addr::text')
        job_item.add_css('company_name', '.b2::attr(alt)')
        job_item.add_css('company_url', 'a[data-lg-tj-track-code="jobs_logo"]::attr(href)')
        job_item.add_css('tags', '.position-label li::text')

        item = job_item.load_item()
        return item
