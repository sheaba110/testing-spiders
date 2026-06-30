import scrapy
from scrapy_playwright.page import PageMethod
from itemloaders.processors import MapCompose
from ..items import ItemsCrawler
from scrapy.loader import ItemLoader
import re

infinite_scroll_script = """
    async () => {
        let lastCount = 0;
        let sameCountTimes = 0;
        let iterations = 0;
        const maxIterations = 400;

        while (iterations < maxIterations) {
            iterations++;

            window.scrollTo(0, document.body.scrollHeight);
            await new Promise(r => setTimeout(r, 2500));

            const btn = [...document.querySelectorAll('a')].find(
                a => a.textContent.includes('Load Next Products')
            );

            if (btn) {
                btn.scrollIntoView();
                await new Promise(r => setTimeout(r, 500));
                btn.click();
                await new Promise(r => setTimeout(r, 3500));
            }

            const products = document.querySelectorAll('.product-thumb, .product-layout').length;

            if (products === lastCount) {
                sameCountTimes++;
                if (sameCountTimes > 6) break; 
            } else {
                sameCountTimes = 0;
            }
            lastCount = products;
            console.log('products so far:', products, 'iteration:', iterations);
        }
        return lastCount;
    }
    """


def extract_price_number(text):
    if text:

        match = re.search(r"[\d,]+(?:\.\d+)?", text)
        if match:

            return match.group(0).replace(",", "")
    return text


class BadrgrbSpider(scrapy.Spider):
    name = "badrgrb"
    allowed_domains = ["elbadrgroupeg.store"]

    async def start(self):
        urls = [
            "https://elbadrgroupeg.store/index.php?route=product/catalog",
        ]
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_item,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod(
                            "wait_for_selector", "div.product-thumb", timeout=60000
                        ),
                        PageMethod(
                            "evaluate", infinite_scroll_script
                        ),
                    ],
                    "playwright_context": "default",
                },
            )

    def parse_item(self, response):
        items = response.css("div.product-layout")
        for product in items:
            l = ItemLoader(item=ItemsCrawler(), selector=product)
            l.add_css("title", "div.name a::text")
            l.add_css(
                "image", "img.img-responsive::attr(src)", MapCompose(response.urljoin)
            )
            l.add_css("url", "a::attr(href)", MapCompose(response.urljoin))
            l.add_value("vendor", "elbadr-group")
            l.add_css("price", "div.price *::text", MapCompose(extract_price_number))
            yield l.load_item()
