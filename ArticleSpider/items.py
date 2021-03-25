# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join  # 连接list各项
from scrapy.loader import ItemLoader


def date_convert(value):
    # 将日期的字符串格式改为datetime
    try:
        value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        value = datetime.datetime.now()
    return value


def return_value(value):
    return value


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
