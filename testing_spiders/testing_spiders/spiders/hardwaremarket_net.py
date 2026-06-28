import scrapy
from scrapy.loader import ItemLoader
from collections.abc import Iterable
from typing import Any
from scrapy_playwright.page import PageMethod
from ..items import ItemsCrawler
import re


class HardwaremarketNetSpider(scrapy.Spider):
    name = "hardwaremarket"
    allowed_domains = ["hardwaremarket.net"]

    def start_requests(self) -> Iterable[Any]:
        urls = ["https://hardwaremarket.net/shop/"]
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_item,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod(
                            "wait_for_selector", "span.woocommerce-Price-amount"
                        ),
                        PageMethod(
                            "evaluate",
                            """
                        async () => {
                            for (let i = 0; i <= 55; i++) {
                                window.scrollBy(0, document.body.scrollHeight);
                                await new Promise(resolve => setTimeout(resolve, 3000));
                            }
                        }
                    """,
                        ),
                        PageMethod("wait_for_timeout", 3000),
                    ],
                    "playwright_context": "default",
                },
            )

    def parse_item(self, response):
        products = response.css("div.wd-products div.wd-col")
        for product in products:
            l = ItemLoader(item=ItemsCrawler(), selector=product)
            l.add_css(
                "image", "div.wd-product-wrapper img.attachment-large::attr(data-src)"
            )
            l.add_css("title", "h3.wd-entities-title a::text")
            raw_price_texts = product.css(".price *::text").getall()
            numbers = [
                int(re.sub(r"[^\d]", "", text))
                for text in raw_price_texts
                if re.sub(r"[^\d]", "", text)
            ]
            if numbers:
                l.add_value("price", str(min(numbers)))
            l.add_value("vendor", "hardware-market")
            l.add_css(
                "url",
                "div.wd-product-thumb.product-element-top.wd-quick-shop a::attr(href)",
            )

            yield l.load_item()