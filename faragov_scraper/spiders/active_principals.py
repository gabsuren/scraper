# -*- coding: utf-8 -*-
import scrapy

# HTML parsing constants
WORKSHEET_TABLE = "apexir_WORKSHEET_DATA"
COUNTRY_LINK = "LINK BREAK_COUNTRY_NAME"
COUNTRY_NAME = "FP_NAME BREAK_COUNTRY_NAME"
COUNTRY_STATE = "STATE BREAK_COUNTRY_NAME"
REG_NUMBER = "REG_NUMBER BREAK_COUNTRY_NAME"
ADDRESS = "ADDRESS_1 BREAK_COUNTRY_NAME"
FOREIGN_PRINCIPAL = "FP_NAME BREAK_COUNTRY_NAME"
REG_DATE = "REG_DATE BREAK_COUNTRY_NAME"
REG_NAME = "REGISTRANT_NAME BREAK_COUNTRY_NAME"


class AcrtivePrincipal(scrapy.Item):
    """
    Active Principal Item class
    """
    url = scrapy.Field()
    country = scrapy.Field()
    state = scrapy.Field()
    reg_num = scrapy.Field()
    address = scrapy.Field()
    foreign_principal = scrapy.Field()
    date = scrapy.Field()
    registrant = scrapy.Field()
    exhibit_url = scrapy.Field()


class ActivePrincipalsSpider(scrapy.Spider):
    """
    Entry point class for spider:ActivePrincipals
    """
    name = "ActivePrincipals"
    base_url = "https://efile.fara.gov/pls/apex/"

    # Temporary Used direct link here
    tail_url = "f?p=171:130:0::NO:RP,130:P130_DATERANGE:N"
    start_urls = [base_url + tail_url]

    # These are hard coded values for POST request.
    post_data = {'p_request': 'APXWGT',
                 'p_flow_id': '171',
                 'p_flow_step_id': '130',
                 'p_widget_num_return': '15',
                 'p_widget_name': 'worksheet',
                 'p_widget_mod': 'ACTION',
                 'p_widget_action': 'PAGE',
                 'x01': '80340213897823017',
                 'x02': '80341508791823021'}
    """
    # Used in POST request to get next page result
     (incremented by 15 after parsing current page)
    """
    pgR_min_row = 1

    def parse(self, response):
        """
        Parses the response from the initial request.
        Constructs ActivePrincipal object and calls appropriate requests.
        :param response:
        :return FormRequest generator:
        """
        work_sheet_table = response.xpath(
                                    "//table[@class='" +
                                    WORKSHEET_TABLE + "']")
        count = 0
        if (work_sheet_table is not None):
            for tr in work_sheet_table.xpath(
                                    ".//tr[@class='odd' or @class='even']"):
                count += 1
                item = self.get_item_from_tr(tr)

                # Request to the href in the row and gets the document url
                yield scrapy.Request(item['url'], callback=self.parse_profile,
                                     meta={'item': item})

                # When page parsed completely sends request to get next page
                if count == 15:
                    self.pgR_min_row += count
                    self.post_data['p_widget_action_mod'] = 'pgR_min_row=' +\
                        str(self.pgR_min_row) +\
                        'max_rows=15rows_fetched=15'
                    yield scrapy.FormRequest(
                          url="https://efile.fara.gov/pls/apex/wwv_flow.show",
                          formdata=self.post_data,
                          method="post",
                          callback=self.parse)

    def get_item_from_tr(self, tr):
        """
        Takes as an argument the <tr> selector,
        then parses the inner <td>tags and creates AcrtivePrincipal item object
        :param tr:
        :return: AcrtivePrincipal Item object
        """
        item = AcrtivePrincipal()
        item['url'] = self.base_url + tr.xpath(
                            ".//td[contains(@headers,'" +
                            COUNTRY_LINK + "')]/a/@href").extract_first()
        item['country'] = tr.xpath(
                            ".//td[contains(@headers,'" +
                            COUNTRY_NAME + "')]/text()").extract_first()
        item['state'] = tr.xpath(
                            ".//td[contains(@headers,'" +
                            COUNTRY_STATE + "')]/text()").extract_first()
        item['reg_num'] = tr.xpath(
                            ".//td[contains(@headers,'" +
                            REG_NUMBER + "')]/text()").extract_first()
        item['address'] = tr.xpath(
                            ".//td[contains(@headers,'" +
                            ADDRESS + "')]/text()").extract_first()
        item['foreign_principal'] = tr.xpath(
                            ".//td[contains(@headers,'" +
                            FOREIGN_PRINCIPAL + "')]/text()").extract_first()
        item['date'] = tr.xpath(
                            ".//td[contains(@headers,'" +
                            REG_DATE + "')]/text()").extract_first()
        item['registrant'] = tr.xpath(
                            ".//td[contains(@headers,'" +
                            REG_NAME + "')]/text()").extract_first()
        return item

    def parse_profile(self, response):
        """
        Parses and gets href of document link(DOCLINK) from response,
        then sets that value to exhibit_url of AcrtivePrincipal item object
        :param response:
        :return ActivePrincipal Item object generator:
        """
        exhibit_url = response.xpath(
                        "//td[@headers='DOCLINK']/a/@href").extract_first()
        item = response.meta['item']
        item['exhibit_url'] = exhibit_url
        yield item
