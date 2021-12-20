import numpy as np 
import pandas as pd
import json
from datetime import datetime
from subprocess import Popen, PIPE
import time
import matplotlib.pyplot as plt

def scrape_cmc_historical(
    date,
    limit,
    convert="USD",
    pause_seconds=5, #s
    ):
    # define base url:
    base_url = [
        "https://web-api.coinmarketcap.com/v1",
        "cryptocurrency/listings/historical",
        ]
    base_url = "/".join(base_url)
    
    # create query URL:
    date_str = date.strftime("%Y-%m-%d")
    options = "convert=%s&date=%s&limit=%d&start=1"%(
        convert,
        date_str,
        limit,
        )
    query = "%s?%s"%(base_url,options)
    
    # query via CURL:
    cmd = ["curl",query]
    p = Popen(cmd,stderr=PIPE,stdout=PIPE)
    stdout,stderr = p.communicate()
    
    # return stdout:
    return stdout

def process_json(stdout):
    output = json.loads(stdout)
    data = output["data"]
    frames = []
    
    # list comprehension for faster extraction:
    [_process_data_entry(entry,frames) for entry in data]
    
    # concatenate results into a Pandas' dataframe 
    # and return:
    results = pd.concat(
        frames,axis=1,
        ).transpose(
        ).set_index("name"
        )
    return results

def _process_data_entry(entry,frames):
    quote = entry["quote"]["USD"]
    s = pd.Series(quote)
    s["name"] = entry["name"]
    s["symbol"] = entry["symbol"]
    s["cmc_rank"] = entry["cmc_rank"]
    frames.append(s)














