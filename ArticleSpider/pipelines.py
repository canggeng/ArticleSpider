# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import codecs
import json

import MySQLdb
import MySQLdb.cursors
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
from contextlib import suppress

from twisted.enterprise import adbapi

from ArticleSpider.items import JobBoleArticleItem
from ArticleSpider.utils.common import serilize_date, unserilize_date


class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline:
    # 自定义json文件到处
    def __init__(self):
        # 打开json文件
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        # json无法实现时间、日期的序列化，需人工转为字符串
        serilize_date(item)
        # ensure_ascii为了支持中文
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        # 将人工转为字符串的时间、日期转为相关对象
        unserilize_date(item)
        return item

    def close_spider(self, spider):
        # 关闭文件资源
        self.file.close()


class JsonExporterPipeline:
    # 调用scrapy提供的json exporter到处json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        # 关闭文件资源
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline:
    # 同步保存到Mysql数据库
    def __init__(self):
        # port必须是数字不能是字符串，否则报错
        # charset使用utf8，而不是utf-8
        self.conn = MySQLdb.connect(host='124.71.97.56', user='root', password='9012345', database='article_spider',
                                    port=3316, charset="utf8")
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # 用'''，可以看出sql的语法格式
        insert_sql = '''
            insert into article(url_object_id, title, url, create_date, read_nums, content)
            value (%s, %s, %s, %s, %s, %s)
        '''
        self.cursor.execute(insert_sql, (
            item['url_object_id'], item['title'], item['url'], item['create_date'], item['read_nums'], item['content']))
        self.conn.commit()

        return item

    def close_spider(self, spider):
        self.conn.close()


class MysqlTwistedPipeline:
    # 异步保存到Mysql数据库，连接池，是由Twisted提供一个异步的容器，并将对应的mysql驱动放入
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    # 被scrapy调用，将整个项目的settings传递进来，在__init__前被调用
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            port=settings['MYSQL_PORT'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        # 异步数据连接池
        # 第一个参数是要用到的mysql驱动模块
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        # 下面方法进行数据操作的异步调用，第一个参数为回调函数，第二个以及以后为要传递给回调函数的参数
        # 返回值为数据库操作的结果或者错误
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 添加错误处理函数
        query.addErrback(self.handle_error, item, spider)

    # 除第一个参数外，其他由addErrorback函数传入
    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    # 第一个参数cursor是一个adbapi.Transaction，采用cursorclass的类创建
    # 第二个以及以后为runInteraction函数中传递给回调函数的参数
    def do_insert(self, cursor, item):
        insert_sql = '''
                    insert into article(url_object_id, title, url, create_date, read_nums, content)
                    value (%s, %s, %s, %s, %s, %s)
                '''
        cursor.execute(insert_sql, (
            item['url_object_id'], item['title'], item['url'], item['create_date'], item['read_nums'], item['content']))
        # 不需要commit，自动提交


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        # results是一个list，每一个元素是touple
        if 'front_image_url' in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        # 必须返回item，供其他pipeline处理
        return item

    # def item_completed(self, results, item, info):
    #     with suppress(KeyError):
    #         ItemAdapter(item)[self.images_result_field] = [x for ok, x in results if ok]
    #     return item
