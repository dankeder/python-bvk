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

```
# Get water consumption data from the specified date to now
date_from = parser.parse('2020-08-01').date()
data = bvk.getWaterConsumption(date_from);

# Get water consumption data for a date interval
date_from = parser.parse('2020-08-01').date()
date_to = parser.parse('2020-08-11').date()
data = bvk.getWaterConsumption(date_from, date_to);

# Get water consumption data for a specific date (just 1 day)
date = parser.parse('2020-08-01').date()
data = bvk.getWaterConsumption(date, date);
```

Keep in mind the library is using [Scrapy](https://scrapy.org) internally which means it is
scraping the BVK customer portal to get the data. If BVK comes to think you are
abusing the website they may block your IP address and/or account.


# License

See [LICENSE](./LICENSE).
