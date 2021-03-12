import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankaudi.items import Article


class BankaudiSpider(scrapy.Spider):
    name = 'bankaudi'
    start_urls = ['https://www.bankaudi.fr/france/about-the-bank/press-releases']

    def parse(self, response):
        articles = response.xpath('//div[@class="listingItem"]')
        for article in articles:
            link = article.xpath('.//div[@class="listingLink"]/a/@href').get()
            date = article.xpath('.//div[@class="listingDate"]/text()').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//title/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="pageContent redirectiondv"]/div[1]//text()').getall() or \
                  response.xpath('//div[@class="pageContent redirectiondv"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
