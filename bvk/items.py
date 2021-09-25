# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime

import scrapy
from itemloaders.processors import TakeFirst


def parse_date(values):
    return [datetime.strptime(value, "%m/%d/%Y").date() for value in values]


def parse_consumption(values):
    return [int(value) for value in values]


class WaterConsumptionItem(scrapy.Item):
    date = scrapy.Field(input_processor=parse_date, output_processor=TakeFirst())
    consumption = scrapy.Field(input_processor=parse_consumption, output_processor=TakeFirst())
