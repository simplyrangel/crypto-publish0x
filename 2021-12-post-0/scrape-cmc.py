"""Scrape coinmarketcap's historical coin market cap rankings found at:
https://coinmarketcap.com/historical/

Scraped via the web api. For example: 
https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/historical?convert=USD,USD,BTC&date=2021-08-29&limit=300&start=1

Web API URL identified by inspecting developer tools page of one of the 
historical snapshot webpages. On the developer tools page, under "Network", 
we can click "load more" and watch the requests made by the internet browser. 
The URL above was the request URL made by the browser. 

Stackexchange research on web scraping led me to this blog post, which
identified the steps outlined above:
https://www.zyte.com/blog/scrapy-tips-from-the-pros-june-2016/
"""
import numpy as np 
import pandas as pd
import time
from datetime import datetime,date

# pandas' index slices:
idx = pd.IndexSlice

# personal modules:
import utilities as utils

# define time range:
today = date.today()
sun2021 = pd.date_range(
    start=datetime(year=2020,month=1,day=1),
    end=today,
    freq="W-SUN",
    )

# exclude today:
sun2021 = sun2021[:-1]

# scrape historical data:
pause_seconds=3
frames = []
for suni in sun2021:
    print("scraping %s..."%(suni.strftime("%Y-%m-%d")))
    output = utils.scrape_cmc_historical(suni,300)
    df = utils.process_json(output)
    frames.append(df)
    time.sleep(pause_seconds)

# save:
results = pd.concat(frames,keys=sun2021)
results.to_hdf("2021-12-post-0/cmc-scrape-results.hdf","w",mode="w")









