
# initialize
scrapy startproject tutorial





# Code for spider
from pathlib import Path

import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            "https://quotes.toscrape.com/page/1/",
            "https://quotes.toscrape.com/page/2/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")



# crawl for data
scrapy crawl quotes

#scrapy shell
scrapy shell 'https://quotes.toscrape.com/page/1/'

# accessing response
response.css("title")
response.css("title::text").getall()
response.css("title").getall()
response.css("title::text").get()
response.css("title::text")[0].get()
response.css("noelement").get()
response.css("title::text").re(r"Quotes.*")
response.css("title::text").re(r"Q\w+")
response.css("title::text").re(r"(\w+) to (\w+)")


# extracting some data
scrapy shell 'https://quotes.toscrape.com'
response.css("div.quote")
quote = response.css("div.quote")[0]
text = quote.css("span.text::text").get()
author = quote.css("small.author::text").get()
tags = quote.css("div.tags a.tag::text").getall()

# printing quotes
for quote in response.css("div.quote"):
    text = quote.css("span.text::text").get()
    author = quote.css("small.author::text").get()
    tags = quote.css("div.tags a.tag::text").getall()
    print(dict(text=text, author=author, tags=tags))


# new spider
import scrapy

class QuotesSpider1(scrapy.Spider):
    name = "quotes1"
    start_urls = [
        "https://quotes.toscrape.com/page/1/",
        "https://quotes.toscrape.com/page/2/",
    ]

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("small.author::text").get(),
                "tags": quote.css("div.tags a.tag::text").getall(),
            }




