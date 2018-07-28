import scrapy


class UserSpider(scrapy.Spider):
    name = 'user'

    auth_template = 'http://fanfics.me/user'
    start_urls = [
        'http://fanfics.me/user50460',
        'http://fanfics.me/user57735'
    ]

    def parse(self, response):
        author = {}
        author['id'] = response.url[len(self.auth_template):]
        author['nickname'] = response.css('div.Profile_Head_SecondTd h1 a::text').extract_first()

        table = response.css('#data-container > table.ProfileInfo')
        profile_keys = table.css('td.first::text').extract()
        profile_values = table.css('td.second')
        profile_data = dict(zip(profile_keys, profile_values))

        author['location'] = profile_data.get('Откуда:')
        if author['location'] is not None:
            author['location'] = author['location'].xpath('text()').extract_first()
        author['registered'] = profile_data.get('Зарегистрирован:')
        if author['registered'] is not None:
            author['registered'] = author['registered'].xpath('text()').extract_first()

        yield author

        yield response.follow('?action=rec_authors', self.parse_recommendations)

    def parse_recommendations(self, response):
        for recommended_author in response.css('.UsersList a.user').xpath('@href').extract():
            yield response.follow(recommended_author, self.parse)