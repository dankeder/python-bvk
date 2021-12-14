# python-bvk

Water conspmution scraper for BVK (Brnenské vodárny a kanalizace, bvk.cz)

Note that you need to have the "smart" water-gauge installed. If you don't know
what that is you probably don't have one. If you don't have one you have to ask
them (BVK) to install it for you and you may have to wait a potentially long
time - they are rolling them out gradually.


## Install

```
pip install python-bvk
```

## Usage

To create the client object you need to provide your BVK username/password
(the one you use on the customer portal https://zis.bvk.cz/).

```
from bvk import Bvk
from dateutil import parser

# Create client
bvk = Bvk('username', 'password')
```

Use `getwaterConsumption()` method to get the water consumption data. It accepts
a `date_from` and optionally a `date_to`, both of which have to be a
[datetime.date](https://docs.python.org/3/library/datetime.html#datetime.date)
object. If `date_to` is not specified the method returns data to today.

Examples:

```
# Get water consumption data from the specified date to now
date_from = parser.parse('2020-08-01').date()
deferred_data = bvk.getWaterConsumption(date_from);

# Get water consumption data for a date interval
date_from = parser.parse('2020-08-01').date()
date_to = parser.parse('2020-08-11').date()
deferred_data = bvk.getWaterConsumption(date_from, date_to);

# Get water consumption data for a specific date (just 1 day)
date = parser.parse('2020-08-01').date()
deferred_data = bvk.getWaterConsumption(date, date);
```

You may call `getWaterConsumption` multiple times with different parameters. It
returns a
[twisted.internet.defer.Deferred](https://twistedmatrix.com/documents/current/core/howto/defer.html)
object that can be used to retrieve the price data in the future using a
callback you need to provide.

```
def process_consumption(consumption)
  print(consumption)

deferred_data.addCallback(process_consumption)
```

If you have multiple `Deferred`s from multiple calls to `getWaterConsumption`
you can use `Bvk.join()` to get a `Deferred` that will be resolved after all
crawlers are finished.

The last callback should stop the reactor so it's shut down cleanly. Reactor
should be stopped after all crawlers are done so the `join()` method comes in
handy. Note that the reactor cannot be restarted so make sure this is the last
thing you do:

```
from twisted.internet import reactor

d = bvk.join()
d.addBoth(lambda _: reactor.stop())
```

The last thing you need to do is run the reactor. The script will block until
the crawling is finished and all configured callbacks executed.

```
reactor.run(installSignalHandlers=False)
```

Keep in mind the library is using [Scrapy](https://scrapy.org) internally which means it is
scraping the BVK customer portal to get the data. If BVK comes to think you are
abusing the website they may block your IP address and/or account.


# License

See [LICENSE](./LICENSE).
