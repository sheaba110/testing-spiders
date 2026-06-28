import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags
import re


def filter_price(value):
    if value.isdigit():
        return value


def clean_price(value):
    if value:
        
        cleaned = re.sub(r"[^\d.]", "", value)
        return cleaned
    return value


class ItemsCrawler(scrapy.Item):
    id = scrapy.Field()
    
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst(),
    )
    image = scrapy.Field(
        output_processor=TakeFirst(),
    )
    url = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst(),
    )
    vendor = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst(),
    )
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, filter_price, clean_price),
        output_processor=TakeFirst(),
    )
