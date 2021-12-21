"""Coin market cap rankings analysis.

Data used throughout this analysis is collected via scrap-cmc.py.
"""
import numpy as np
import pandas as pd
from datetime import datetime

# Pandas' index slices:
idx = pd.IndexSlice

# -------------------------------------------------------
# Load and process data.
# -------------------------------------------------------
scrape_file = "bin/cmc-scrape-results-thru-2021-12-19.hdf"
mdf = pd.read_hdf(scrape_file)

# get current coin market cap rankings and remove 
# stablecoins, wrapped coins, and memecoins:
ignore_coins = [
    # stablecoins:
    "Tether",
    "Binance USD",
    "USD Coin",
    "TerraUSD",
    "Neutrino USD",
    "Dai",
    "TrueUSD",
    "Gemini Dollar",
    
    # Bitcoin, Ethereum derivatives:
    # and wrapped coins:
    "Bitcoin BEP2",
    "Wrapped Bitcoin",
    "Ethereum Classic",
    "Wrapped BNB",
    "Huobi BTC",
    "RenBTC",
    "Bitcoin Cash ABC",
    
    # memecoins:
    "SHIBA INU",
    "Dogecoin",
    "Dogelon Mars",
    ]

# get unique coin names, and exclude the coins 
# we don't care about:
unique_coins = mdf.reset_index(level=1)["name"].unique()
unique_coins = [x for x in unique_coins if x not in ignore_coins]

# -------------------------------------------------------
# Extract coin rank histories.
# -------------------------------------------------------
# create empty dataframe for rank results:
rankings = pd.DataFrame(
    np.nan,
    index=mdf.index.levels[0],
    columns=unique_coins,    
    )

# create dataframe from multiindex scraped data 
# that is indexed by coin name:
coins = mdf.reset_index(level=0).sort_index()
coins = coins.rename(
    columns={"level_0": "week"},
    )

# extract rank over time:
for col in rankings.columns:
    data = coins.loc[col,["week","cmc_rank"]]
    if len(data.shape) < 2:
        rows = data.week
        entries = data.cmc_rank
    else:
        rows = data.week.tolist()
        entries = data.cmc_rank.values
    rankings.loc[rows,col] = entries

# save rank history data:
thru_date = scrape_file.split("thru-")[-1].split(".hdf")[0]
results_fi = "cmc-rank-histories-thru-%s.hdf"%thru_date
rankings.to_hdf("bin/%s"%results_fi,"w",mode="w")









