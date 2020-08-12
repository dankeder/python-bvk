# python-bvk

Water conspmution scraper for BVK (Brnenské vodárny a kanalizace, bvk.cz)


## Install

```
pip install python-bvk
```

## Usage

```
from bvk import Bvk
from dateutil import parser

# Create client
bvk = Bvk('username', 'password')

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
