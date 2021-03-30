#! /bin/bash

__author__ = 'zzj'

from elasticsearch_dsl import DocType, Text, Date, Keyword, Integer, Completion
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections

# 创建于es服务的连接，hosts可以连接多个服务器
conn = connections.create_connection(hosts=['localhost'])


# 因为5.1.1的es中Completion对ik分词器支持有问题，所以需要将该分词器伪装
class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        # 为了不报错，返回空字典
        return {}


ik_analyzer = CustomAnalyzer('ik_max_word', filter=['lowercase'])


class ArticleType(DocType):
    # 伯乐在线文章类型
    title = Text(analyzer='ik_max_word')
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    read_nums = Integer()
    content = Text(analyzer='ik_max_word')
    tags = Text(analyzer='ik_max_word')
    # 因为5.1.1的es中Completion对ik分词器支持有问题，所以需要将该分词器伪装为用户分析器
    suggest = Completion(analyzer=ik_analyzer)

    class Meta:
        # es中的index
        index = "jobbole"
        # es中的type
        doc_type = "article"


if __name__ == '__main__':
    # init()方法会根据类的定义，直接生成mapping
    ArticleType.init()
