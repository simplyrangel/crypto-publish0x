import numpy as np 
import pandas as pd
from datetime import datetime
from subprocess import Popen, PIPE
import time
import matplotlib.pyplot as plt

def html_filter(stdout):
    
    # decode bytestring into UTF-8:
    s = stdout.decode("UTF-8")
    
    # extract relevant section of HTML string output:
    l = s.find("listingHistorical")
    sdata = s[l:]
    
    # remove coins based on other blockchains:
    sdata = sdata.split("name")[1:]
    sdata = [
        x for x in sdata 
        if "num_market_pairs" in x
        ]
    return sdata
    
def extract_data(l):

    # remove needless characters:
    needless_chars = [
        "{",
        "}",
        "[",
        "]",
        '"',
    ]
    for c in needless_chars:
        l = l.replace(c,"")
    symbol = l.split(",")[1].replace("symbol:","")
    name = l.split(",")[2].replace("slug:","")
    result = [symbol, name]
    return result

def scrape(
    sunday_range,
    pause_seconds=5, #s
    ):
    
    # iterate over each date:
    frames = []
    url_template = "https://coinmarketcap.com/historical/%s/"
    for date in sunday_range:
        
        # create URL:
        url = url_template%(date.strftime("%Y%m%d"))
        print("scraping %s..."%url)
        
        # query URL via CURL:
        cmd = ["curl",url]
        p = Popen(cmd,stderr=PIPE,stdout=PIPE)
        stdout,stderr = p.communicate()
        
        # extract coin market cap data:
        coin_symbols = []
        coin_names = []
        output = html_filter(stdout)
        for l in output:
            symbol,name = extract_data(l)
            coin_symbols.append(symbol)
            coin_names.append(name)
        
        # store market cap data in a Pandas Dataframe:
        num_coins = len(coin_symbols) + 1
        df = pd.DataFrame(
            [coin_symbols,coin_names],
            index=["symbol","name"],
            columns=range(1,num_coins)
            ).transpose()
        df.index.names=["rank"]
        frames.append(df)
        
        # wait several seconds to avoid website query 
        # limits:
        time.sleep(pause_seconds) 

    # return data as multiindex dataframe:
    return pd.concat(frames,keys=sunday_range)






