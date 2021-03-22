# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join #连接list各项


class ArticleItemLoader(ItemLoader):
    # 默认让itemloader将item的每个属性结果的list只取第一个项的值
    default_output_processor = TakeFirst()


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    # 将日期的字符串格式改为datetime
    try:
        value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        value = datetime.datetime.now()
    return value


def return_value(value):
    return value


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
