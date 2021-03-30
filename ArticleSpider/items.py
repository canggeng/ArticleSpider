# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from w3lib.html import remove_tags
from itemloaders.processors import TakeFirst, MapCompose, Join  # 连接list各项
from scrapy.loader import ItemLoader

from ArticleSpider.models.ex_types import ArticleType
from elasticsearch_dsl.connections import connections

es = connections.create_connection(ArticleType._doc_type.using)


def date_convert(value):
    # 将日期的字符串格式改为datetime
    try:
        value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        value = datetime.datetime.now()
    return value


def return_value(value):
    return value


# 根据字符串生成搜索建议数组
def gen_suggests(index, info_tuple):
    # 为了去重，用set；当对不同field的分词打分后，需要忽略已经打分的结果
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]}, body=text)
            # >1是因为单个词不做考虑
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            # set求差集，过滤重复的词
            new_words = anylyzed_words - used_words
            used_words = used_words | new_words
        else:
            new_words = set()
        if new_words:
            # [{"input": [], "weight": 分数}, ...]这是es规定的搜索建议的格式要求
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests


class BaseItemLoader(ItemLoader):
    # 默认让itemloader将item的每个属性结果的list只取第一个项的值
    default_output_processor = TakeFirst()


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    # MapCompose(cb1, cb2, cb3...)可以实现多个回调函数的依次调用，每个回调的参数是ItemLoader中各项的List的单项的值
    create_date = scrapy.Field(input_processor=MapCompose(date_convert))
    url = scrapy.Field()
    # url的md5加密，这样url的变长就变为恒长了
    url_object_id = scrapy.Field()
    # 保留List格式
    front_image_url = scrapy.Field(output_processor=MapCompose(return_value))
    # 封面图本地保存路径
    front_image_path = scrapy.Field()
    read_nums = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        insert_sql = '''
                            insert into article(url_object_id, title, url, create_date, read_nums, content)
                            value (%s, %s, %s, %s, %s, %s)
                        '''
        params = (
            self['url_object_id'], self['title'], self['url'], self['create_date'], self['read_nums'], self['content'])
        return insert_sql, params

    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.create_date = self["create_date"]
        article.url = self["url"]
        # es的id是保存在meta.id中
        article.meta.id = self["url_object_id"]

        article.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            article.front_image_path = self["front_image_path"]
        article.read_nums = self["read_nums"]
        article.content = remove_tags(self["content"])
        article.tags = self["tags"]

        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title, 10), (article.tags, 7)))

        article.save()

        # redis_cli.incr("jobbole_count")

        return


def zhihu_date_convert(value):
    # (1292, "Incorrect datetime value: '2015-04-28T17:35:32.000Z' for column 'create_time' at row 1")
    mathched = re.match(r'(.*)T(.*)\..*', value)
    if mathched:
        d = mathched.group(1)
        t = mathched.group(2)
        return date_convert(d + ' ' + t)
    return datetime.datetime.now()


class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题 item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    create_time = scrapy.Field(input_processor=MapCompose(zhihu_date_convert))
    update_time = scrapy.Field(input_processor=MapCompose(zhihu_date_convert))
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, create_time, update_time, answer_num, 
            comments_num, watch_user_num, click_num, crawl_time, crawl_update_time
            ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) on DUPLICATE KEY UPDATE answer_num=VALUES(answer_num), comments_num=VALUES(comments_num), 
            watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num), crawl_update_time=VALUES(crawl_update_time)
        """

        params = (self['zhihu_id'], self['topics'], self['url'], self['title'], self['content'], self['create_time'],
                  self['update_time'], self['answer_num'], self['comments_num'], self['watch_user_num'],
                  self['click_num'], self['crawl_time'], datetime.datetime.now())

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, parise_num, comments_num, 
            create_time, update_time, crawl_time, crawl_update_time
            ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) on DUPLICATE KEY UPDATE parise_num=VALUES(parise_num), comments_num=VALUES(comments_num), 
            crawl_update_time=VALUES(crawl_update_time)
        """

        params = (self['zhihu_id'], self['url'], self['question_id'], self['author_id'], self['content'],
                  self['parise_num'], self['comments_num'], self['create_time'], self['update_time'],
                  self['crawl_time'], datetime.datetime.now())

        return insert_sql, params


def remove_splash(value):
    # 去除斜杠
    return value.replace('/', '')


def strip(value):
    # 去空格
    return value.strip()


def handle_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [addr.strip() for addr in addr_list if addr.strip() != '查看地图']
    return ''.join(addr_list)


class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash, strip),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash, strip),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash, strip),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        """
        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"],
            self["publish_time"], self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_name"], self["company_url"],
            self["job_addr"], self["crawl_time"],
        )

        return insert_sql, params
