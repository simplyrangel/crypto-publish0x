"""Coin market cap rankings analysis.

Data used throughout this analysis is collected via scrap-cmc.py.
"""
import numpy as np
import pandas as pd
from datetime import datetime

# set local paths to enable imports:
from _path import setup_paths
setup_paths()

# plot setup:
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from styleguide import set_rcparams, imghelper

# Pandas' index slices:
idx = pd.IndexSlice

# plot setup:
set_rcparams()
img = imghelper(
    save_dir="bin/",
    img_series = "cmc-analysis",    
    )

# -------------------------------------------------------
# Load and process data.
# -------------------------------------------------------
# I deferred completing this analysis by a few weeks, 
# so I need to concat the scrape results to update:
mdf1 = pd.read_hdf("cmc-scrape-results-top-1000.hdf")
mdf2 = pd.read_hdf("cmc-scrape-results-top-1000-2021-12-05.hdf")
mdf = pd.concat([mdf1,mdf2])

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
current_cmc = mdf.loc[idx["2021-12-05",:],:].reset_index(level=1)
ignore_coins_id = current_cmc.index.isin(ignore_coins)
current_cmc = current_cmc[~ignore_coins_id]

# create bin for market cap rankings per coin:
rankings = pd.DataFrame(
    np.nan,
    index=mdf.index.levels[0],
    columns=mdf.reset_index(level=1)["name"].unique(),    
    )

# extract each coin's market cap ranking time history:
coins = mdf.reset_index(level=0).sort_index()
coins = coins.rename(columns={"level_0": "week"})
for col in rankings.columns:
    data = coins.loc[col,["week","cmc_rank"]]
    if len(data.shape) < 2:
        rows = data.week
        entries = data.cmc_rank
    else:
        rows = data.week.tolist()
        entries = data.cmc_rank.values
    rankings.loc[rows,col] = entries

# -------------------------------------------------------
# Look at coin ranking changes per week:
# -------------------------------------------------------
rankings2021 = rankings["2021-01-01":]
dcmc = rankings.diff()["2021-01-01":]

# extract coins that have experienced the most 4-week 
# cmc changes that are still in the top-X coins today:
cutoff = 6
coins_of_interest = []
for coin in dcmc:
    monthly_changes = dcmc[coin].resample("4W").sum()
    filtered = monthly_changes[monthly_changes<0]
    if (len(filtered.values) > cutoff 
        and coin not in ignore_coins
        and coin not in current_cmc.name[:50].tolist()
        #and not rankings2021[coin].isna().any()
        and rankings2021[coin].min() >= 50
        ):
        coins_of_interest.append(coin) 

print(len(coins_of_interest))

# plot 2021 results:
# Note: Some coins such as (XinFin Network, or XDC Network)
# changed their coin names. This is why XinFin Network 
# appears in some iterations of this plot, but then suddenly
# goes NaN. 
plt.figure()
plt.title("Filtered gainers")
for col in coins_of_interest:
    plt.plot(
        rankings2021.index,
        rankings2021[col],
        label=col,
        linewidth=1,
        )
plt.xlabel("week")
plt.xticks(ticks=rankings2021.index[::2],rotation=45)
plt.ylabel("market cap ranking")
plt.legend(fontsize=8)
plt.grid()
plt.tight_layout()
img.savefig()
plt.close()













