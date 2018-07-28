import json
import scrapy
import datetime as dt


class MetadataSpider(scrapy.Spider):
    name = "metadata"
    addr = "http://fanfics.me/fic"

    def start_requests(self):
        with open("data/fic_ids.json", "r") as f:
            for fic in json.load(f):
                yield scrapy.Request(url="{}{}".format(self.addr, fic["id"]), callback=self.parse)

    def parse(self, response):
        try:
            table = response.css(".FicHead")[0]
        except IndexError:
            return []
        fic_id = response.url[len(self.addr):]
        published = response.css("#fic_info_content_stat table tr").xpath(
                "./td[contains(., \"Опубликован:\")]/parent::tr/td[last()]/text()").extract_first()
        metadata = {
            "id": fic_id,
            "title": table.css("h1::text").extract_first(),
            "published": dt.datetime.strptime(published, "%d.%m.%Y").date()
        }
        for field in table.css("div.tr"):
            title = field.css(".title").extract_first()
            content = field.css(".content")
            if "Рейтинг" in title:
                metadata["rating"] = content.xpath("text()").extract_first()
            elif "Автор" in title:
                metadata["authors"] = content.xpath("./span/@data-show-member").extract()
            elif "Жанр" in title:
                genre = content.xpath("text()").extract_first()
                genre = genre.replace("Hurt/comfort", "Hurt-Comfort")
                metadata["genre"] = genre.split("/")
            elif "События" in title:
                metadata["events"] = content.css("a::text").extract()
            elif "Предупреждение" in title:
                metadata["warnings"] = content.xpath("text()").extract_first().split(", ")
            else:
                pass

        yield metadata
