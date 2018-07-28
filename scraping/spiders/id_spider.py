import scrapy
import datetime as dt


class IdSpider(scrapy.Spider):
    name = "id"
    fic_page_addr = "http://fanfics.me/fic"
    start_urls = [
        "http://fanfics.me/find?section=find&fandom1=2&fandom2=0&pers1=0&pers2=0&pers3=0&pers4=0&pers5=0&pers6=0&size=0&reit=0&status=1&date=0&translate=0&original_language=0&reit1=0",
    ]

    def parse(self, response):
        for fic_page in response.css('.FicTable').css('.FicTable_Title a').xpath('@href').extract():
            yield response.follow(fic_page, self.parse_metadata)

        paginator = response.css("div.paginator")[0]
        current_page = int(paginator.css("span.this").xpath("text()").extract_first())
        next_page = paginator.xpath("span/a[text() = '{}']/@href".format(current_page + 1)).extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_metadata(self, response):
        try:
            table = response.css(".FicHead")[0]
        except IndexError:
            return []
        fic_id = response.url[len(self.fic_page_addr):]
        published = response.css("#fic_info_content_stat table tr").xpath(
                "./td[contains(., \"Опубликован:\")]/parent::tr/td[last()]/text()").extract_first()
        last_update = response.css("#fic_info_content_stat table tr").xpath(
            "./td[contains(., \"Изменен:\")]/parent::tr/td[last()]/text()").extract_first()
        metadata = {
            "id": fic_id,
            "title": table.css("h1::text").extract_first(),
            "published": dt.datetime.strptime(published, "%d.%m.%Y").date(),
            "last_update": dt.datetime.strptime(last_update, "%d.%m.%Y").date()
        }

        for field in table.css("div.tr"):
            title = field.css(".title").extract_first()
            content = field.css(".content")
            if "Рейтинг" in title:
                metadata["rating"] = content.css('::text').extract_first()
            elif "Автор" in title:
                metadata["authors"] = content.xpath("./span/@data-show-member").extract()
            elif "Переводчик" in title:
                metadata["translators"] = content.xpath("./span/@data-show-member").extract()
            elif "Жанр" in title:
                genre = content.xpath("text()").extract_first()
                genre = genre.replace("Hurt/comfort", "Hurt-Comfort")
                metadata["genre"] = genre.split("/")
            elif "События" in title:
                metadata["events"] = content.css("a::text").extract()
            elif "Предупреждение" in title:
                metadata["warnings"] = content.xpath("text()").extract_first().split(", ")
            elif "Размер" in title:
                size_cat = content.css('::text').extract_first()
                size_cat = 'small' if 'Мини' in size_cat else 'medium' if 'Миди' in size_cat else 'large'
                size_kb = content.css('#FicSize::text').extract_first()
                size_kb = int(size_kb.split()[0]) if size_kb else 0
                metadata['size_cat'] = size_cat
                metadata['size_kb'] = size_kb
            elif "Персонажи" in title:
                characters = content.xpath('a[contains(@href, "paring")]/text()').extract()
                characters = [pair.split('/', 1) for pair in characters]
                characters.append(content.xpath('a[contains(@href, "character")]/text()').extract())
                metadata['characters'] = characters
            else:
                pass

        yield metadata
