import json
import scrapy


class TextSpider(scrapy.Spider):
    name = "text"
    fic_page_addr = "http://fanfics.me/fic"
    start_urls = [
        "http://fanfics.me/find?section=find&fandom1=2&fandom2=0&pers1=0&pers2=0&pers3=0&pers4=0&pers5=0&pers6=0&size=0&reit=0&status=1&date=0&translate=0&original_language=0&reit1=0",
    ]

    def parse(self, response):
        for fic_page in response.css('.FicTable').css('.FicTable_Title a').xpath('@href').extract():
            yield response.follow(fic_page, self.open_reader)

        # paginator = response.css("div.paginator")[0]
        # current_page = int(paginator.css("span.this").xpath("text()").extract_first())
        # next_page = paginator.xpath("span/a[text() = '{}']/@href".format(current_page + 1)).extract_first()
        # if next_page is not None:
        #     yield response.follow(next_page, self.parse)

    def parse_text(self, response):
        """

        Parameters
        ----------
        response

        Returns
        -------

        """
        if bytes("Неправильные логин или пароль!", "utf8") in response.body:
            self.logger.error("Login failed")
            return

        chapters = response.css("div.ReadTextContainer div.ReadContent:nth-of-type(2)").xpath(
            ".//div["
            "contains(@class, 'chapter') and "
            "not(contains(@class, 'chapter1')) and "
            "not(contains(@class, 'right'))]"
        )

        if not chapters:
            return scrapy.FormRequest.from_response(
                response,
                formname="autent",
                formdata={'name': 'some_spider', 'pass': 'sN7dkZ'},
                callback=self.parse_text
            )

        text = "\n".join(chapters.xpath("string(.)").extract())
        fic_id = response.url.split("=")[-1]
        yield {
            "id": fic_id,
            "text": text
        }

    def open_reader(self, response):
        yield response.follow(response.xpath('//*[@id="FicReadLink"]/a/@href').extract_first(), self.open_reader)

