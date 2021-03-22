# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    # url的md5加密，这样url的变长就变为恒长了
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    # 封面图本地保存路径
    front_image_path = scrapy.Field()
    read_nums = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()