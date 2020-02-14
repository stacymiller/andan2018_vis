from logging import error

import scrapy
import datetime as dt


class IdSpider(scrapy.Spider):
    name = "id"
    fic_page_addr = "http://fanfics.me/fic"
    start_urls = [
        # "http://fanfics.me/find?section=find&fandom1=2&fandom2=0&pers1=0&pers2=0&pers3=0&pers4=0&pers5=0&pers6=0&size=0&reit=0&status=1&date=0&translate=0&original_language=0&reit1=3#fics",
        # "http://fanfics.me/find?section=find&fandom1=2&fandom2=0&pers1=0&pers2=0&pers3=0&pers4=0&pers5=0&pers6=0&size=0&reit=0&status=1&date=0&translate=0&original_language=0&reit1=1#fics",
        # "http://fanfics.me/find?section=find&fandom1=2&fandom2=0&pers1=0&pers2=0&pers3=0&pers4=0&pers5=0&pers6=0&size=0&reit=0&status=1&date=0&translate=0&original_language=0&reit1=2#fics",
        "http://fanfics.me/find?section=find&fandom1=2&fandom2=0&pers1=0&pers2=0&pers3=0&pers4=0&pers5=0&pers6=0&size=0&reit=0&status=1&date=0&translate=0&original_language=0&reit1=4#fics"
    ]

    def parse(self, response):
        for fic_page in response.css('.FicTable').css('.FicTable_Title a').xpath('@href').extract():
            yield response.follow(fic_page, self.parse_metadata)

        paginator = response.css("div.paginator")[0]
        current_page = int(paginator.css("span.this").xpath("text()").extract_first())
        next_page = paginator.xpath("span/a[text() = '{}']/@href".format(current_page + 1)).extract_first()

        print('seen {} fics on page {}; next page is {}'.format(len(response.css('.FicTable')), current_page, next_page))
        if next_page is not None:
            yield response.follow(next_page, self.parse, dont_filter=True)
        else:
            import random
            with open("last_page_{}.html".format(''.join(random.choices("abcdefghijklmn", k=4))), "wb") as f:
                f.write(response.body)

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
        category = table.css("h1>span::text").extract_first().replace("(", "").replace(")", "")
        views = response.css("#fic_info_content_stat table tr").xpath(
            "./td[contains(., \"Просмотров:\")]/parent::tr/td[last()]/text()").extract_first()
        subscribers = response.css("#fic_info_content_stat table tr").xpath(
            "./td[contains(., \"Читателей:\")]/parent::tr/td[last()]/span/text()").extract_first()
        recommendations = response.css("#fic_info_content_stat table tr").xpath(
            "./td[contains(., \"Рекомендаций:\")]/parent::tr/td[last()]/text()").extract_first()
        comments = response.css("#fic_info_content_stat table tr").xpath(
            "./td[contains(., \"Комментариев:\")]/parent::tr/td[last()]/text()").extract_first()

        metadata = {
            "id": fic_id,
            "title": table.css("h1::text").extract_first(),
            "published": dt.datetime.strptime(published, "%d.%m.%Y").date() if published else None,
            "last_update": dt.datetime.strptime(last_update, "%d.%m.%Y").date() if last_update else None,
            "category": category,
            "views": int(views.replace(" ", "")),
            "subscribers": int(subscribers),
            "recommendations": int(recommendations),
            "comments": int(comments)
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
            elif "Оригинал" in title:
                orig_content_table = content.css("table.translation_info tr")
                for orig_field in orig_content_table:
                    orig_title = orig_field.css("td.first").extract_first()
                    if "Название" in orig_title:
                        metadata["original_title"] = orig_field.css("td.second::text").extract_first()
                    elif "Автор" in orig_title:
                        metadata["authors"] = orig_field.css("td.second a::text").extract()
                    elif "Язык" in orig_title:
                        metadata["original_language"] = orig_field.css("td.second::text").extract_first()
                    else:
                        pass
            elif "Бет" in title:
                metadata["betas"] = content.xpath("./span/@data-show-member").extract()
            elif "Жанр" in title:
                genre = content.xpath("text()").extract_first()
                metadata["genre"] = genre.split(", ") if genre is not None else []
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
                characters = [pair.split('/') for pair in characters]
                characters.extend(content.xpath('a[contains(@href, "character")]/text()').extract())
                metadata['characters'] = characters
            elif not (("Фандом" in title) or ("Статус" in title)):
                error("Unmanadeg data at {}: {}".format(response.url, title))

        yield metadata
