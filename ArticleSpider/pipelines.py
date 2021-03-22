# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from contextlib import suppress

class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value["path"]
        item["front_image_path"] = image_file_path

        # 必须返回item，供其他pipeline处理
        return item

    # def item_completed(self, results, item, info):
    #     with suppress(KeyError):
    #         ItemAdapter(item)[self.images_result_field] = [x for ok, x in results if ok]
    #     return item