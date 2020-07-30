from twisted.internet import reactor
from scrapy.settings import Settings
from scrapy.crawler import CrawlerRunner

from .spiders.water_consumption import WaterConsumptionSpider


class Bvk:
    def __init__(self, bvk_username, bvk_password, log_enabled=None, log_level=None):
        self._bvk_username = bvk_username
        self._bvk_password = bvk_password

        # NOTE: We create settings "manually", not using
        # "scrapy.utils.project.get_project_settings" so we don't have to
        # bundle scrapy.cfg with the bvk package.
        self._settings = Settings()
        self._settings.setmodule('bvk.settings', priority='project')

        # Override settings if needed
        if log_enabled is not None:
            self._settings["LOG_ENABLED"] = log_enabled
        if log_level is not None:
            self._settings["LOG_LEVEL"] = log_level

    def getWaterConsumption(self, date_from, date_to=None):
        """ Get water consumption for the specified time period.  If `date_to`
            is not specified return consumption data from `date_from` till today.

            `date_from` and `date_to` must be datetime.date-compatible objects.
        """
        items = []

        def _item_scraped(item):
            items.append(item)

        runner = CrawlerRunner(self._settings)
        deferred = runner.crawl(
            WaterConsumptionSpider,
            bvk_username=self._bvk_username,
            bvk_password=self._bvk_password,
            date_from=date_from,
            date_to=date_to,
            cb_item_scraped=_item_scraped,
        )
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run(installSignalHandlers=False)  # the script will block here until the crawling is finished

        return {item["date"].isoformat(): item["consumption"] for item in items}
