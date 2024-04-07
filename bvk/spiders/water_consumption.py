from datetime import date
from urllib.parse import unquote, urlencode, urljoin

import scrapy
from dateutil import rrule
from scrapy.loader import ItemLoader

from ..items import WaterConsumptionItem


class WaterConsumptionSpider(scrapy.Spider):
    name = "water_consumption"

    def __init__(self, bvk_username, bvk_password, date_from, date_to=None, cb_item_scraped=None, *args, **kwargs):
        """ Get the water consumption from BVK. It will scrape the BVK website
            using the provided username/password and get daily consumption values
            for the given interval specified by `date_from` and `date_to`
            (which are datetime.date-compatible objects). If `date_to` is
            not provided it will scrape data starting from `date_from` till
            today.

            The `cb_item_scraped` is a callback accepting one argument "item"
            that will be called for each item (consumption data for the given
            month) scraped.
        """
        super().__init__(*args, **kwargs)

        # BVK username/password
        self._bvk_username = bvk_username
        self._bvk_password = bvk_password

        # Year/month to scrape
        self._date_from = date_from
        self._date_to = date_to if date_to is not None else date.today()

        # Output callback - will be called for each item scraped
        self._cb_item_scraped = cb_item_scraped

    def start_requests(self):
        url = "https://zis.bvk.cz/"
        yield scrapy.Request(url=url, callback=self.handle_login)

    def handle_login(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formid="ctl00_ctl00_lvLoginForm_LoginDialog1_PanelLogin",
            headers={"X-MicrosoftAjax": "Delta=true"},
            formdata={
                "ctl00$ctl00$lvLoginForm$LoginDialog1$edEmail": self._bvk_username,
                "ctl00$ctl00$lvLoginForm$LoginDialog1$edPassword": self._bvk_password,
                "ctl00$ctl00$lvLoginForm$LoginDialog1$btnLogin": "Login",
            },
            callback=self.handle_login_response,
        )

    def handle_login_response(self, response):
        response_parts = response.text.split('|')
        if response_parts[5] == "pageRedirect":
            redirect_url = "/Userdata/MainInfo.aspx"
            main_info_url = urljoin(response.url, redirect_url)
            return scrapy.Request(url=main_info_url, callback=self.handle_main_info_response)
        else:
            raise Exception(f"Login to BVK failed (status {response.status}): {response.text}")

    def handle_main_info_response(self, response):
        suezsmartsolutions_login_url = response.css(
            "a#ctl00_ctl00_ctl00_ContentPlaceHolder1Common_ContentPlaceHolder1_UserDataContentPlaceHolder_btnPortalEmis"
        ).attrib["href"]
        return scrapy.Request(url=suezsmartsolutions_login_url, callback=self.handle_suezsmartsolutions_login_response)

    def handle_suezsmartsolutions_login_response(self, response):
        # Iterate over years/months between `date_from` and `date_to` and get
        # the daily consumption for the respective months
        #
        # We need to set the day in `dtstart` to the first day of month because
        # otherwise if the day is greater than the day in `until` the last
        # month would not be included. For example for dtstart 2020-03-09 and
        # until 2020-08-01 would skip 2020-08 because 2020-08-09 comes after
        # 2020-08-01.
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=self._date_from.replace(day=1), until=self._date_to):
            qs = urlencode(
                {
                    "Affichage": "ConsoJour",  # consumption by day
                    "Annee": dt.year,  # for this year
                    "Mois": dt.month,  # and this month
                }
            )
            consumption_url = urljoin(response.url, f"/eMIS.SE_BVK/Site_Energie.aspx?{qs}")
            yield scrapy.Request(
                url=consumption_url,
                callback=self.handle_suezsmartsolutions_consumption_response,
                cb_kwargs={
                    "year": dt.year,
                    "month": dt.month,
                    "not_before": self._date_from,
                    "not_after": self._date_to,
                },
            )

    def handle_suezsmartsolutions_consumption_response(self, response, year, month, not_before, not_after):
        table_rows = response.css("table#ctl00_PHZonePrincipale_ctl01_TableTableau tr")
        for row in table_rows[1:]:  # Skip table header
            loader = ItemLoader(item=WaterConsumptionItem(), selector=row)
            loader.add_css("date", "td.TableauEnergieLabel::text")
            loader.add_css("consumption", "td.TableauEnergie span::text")
            item = loader.load_item()

            # Check if the date in consumption data is within our time frame;
            # if it is, yield the consumption data, otherwise continue with the
            # next item
            if not_before <= item["date"] <= not_after:
                if self._cb_item_scraped is not None:
                    self._cb_item_scraped(item)
                yield item
