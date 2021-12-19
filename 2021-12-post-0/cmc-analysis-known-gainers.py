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
    
# save for visual inspection and later use:
rankings.to_excel("rankings.xlsx")

# -------------------------------------------------------
# Consider known top gainers:
# -------------------------------------------------------
mcap_massive_changers = [
    "XYO",
    "Solana",    
    ]
mcap_moderate_changers = [
    "Avalanche",
    "Terra",
    "Algorand",
    ]
coins_of_interest = mcap_massive_changers+mcap_moderate_changers

# plot coins of interest coin marketcap rankings 
# through time:
for clist in [mcap_massive_changers,mcap_moderate_changers]:
    fig,ax=plt.subplots()
    plt.title("""Coin market cap rank through time
extracted from coinmarketcap.com/historical""")
    for coin in clist:
        plt.plot(
            rankings.index,
            rankings[coin],
            label=coin,
            )
    plt.xlabel("week")
    plt.xticks(ticks=rankings.index[::4],rotation=45)
    plt.ylabel("market cap ranking")
    plt.legend()
    plt.grid()
    #plt.ylim([0,450])
    plt.text(
        0.0,
        0.0,
        """publish0x.com/@simplyrangel
github.com/simplyrangel""",
        transform=ax.transAxes,
        fontsize=10,
        ha="left",
        va="bottom",
        color="gray",
        alpha=0.5,
        )
    plt.tight_layout()
    img.savefig()
    plt.close()

# plot the coin marketcap rank and price history
# on the same graph, sharing an x axis:
for coin in coins_of_interest:
    
    # load historical data:
    prices = pd.read_csv(
        "bin/%s-price-history.csv"%coin,
        index_col=[0],
        parse_dates=True,
        infer_datetime_format=True,
        )
    
    # constrain rankings data to the price data
    # date range:
    ri=rankings[prices.index[-1]:]
    
    # plot:
    fig,ax1 = plt.subplots()
    plt.title("%s market cap and price"%coin)
    ax1.plot(
        ri.index,
        ri[coin],
        color="red",
        )
    ax1.set_xlabel("week")
    ax1.set_ylabel("market cap ranking",color="red")
    ax1.tick_params(axis="y",labelcolor="red")
    plt.xticks(ticks=rankings.index[::2],rotation=45)
    ax2 = ax1.twinx()
    ax2.plot(
        prices.index,
        prices.Open,
        color="gray",
        )
    ax2.set_ylabel("USD open price")
    plt.text(
        1.0,
        0.0,
        """publish0x.com/@simplyrangel
github.com/simplyrangel""",
        transform=ax1.transAxes,
        fontsize=10,
        ha="right",
        va="bottom",
        color="gray",
        alpha=0.5,
        )
    fig.tight_layout()
    img.savefig()
    plt.close()

# calculate the mcap difference per 2 weeks and per month,
#  and plot that against the price as well:
markerwheel = {
    "2W": "x",
    "4W": "v",    
    }
alphawheel = {
    "2W": 0.25,
    "4W": 0.7,    
    }
for coin in coins_of_interest:
    prices = pd.read_csv(
        "bin/%s-price-history.csv"%coin,
        index_col=[0],
        parse_dates=True,
        infer_datetime_format=True,
        )
    fig,ax1 = plt.subplots()
    plt.title("%s market cap changes and price"%coin)
    ax1.set_xlabel("week")
    ax1.set_ylabel("market cap ranking change",color="red")
    ax1.tick_params(axis="y",labelcolor="red")
    plt.xticks(ticks=rankings.index[::2],rotation=45)
    for resample_rate in ["2W","4W"]:
        dcmc = rankings[coin
            ].resample(resample_rate
            ).first(
            ).fillna(value=np.nan
            ).apply(float
            ).diff(
            )
        ax1.plot(
            dcmc.index,
            dcmc.values,
            label="",
            color="red",
            alpha=alphawheel[resample_rate],
            )
        ax1.scatter(
            dcmc.index,
            dcmc.values,
            label="sample rate: %s"%resample_rate,
            color="red",
            alpha=alphawheel[resample_rate],
            marker=markerwheel[resample_rate],
            s=100,
            )
    plt.legend(loc="upper left",fontsize=10)
    plt.axhline(0,color="red",label="",linewidth=1)
    ax2 = ax1.twinx()
    ax2.plot(
        prices.index,
        prices.Open,
        color="gray",
        )
    ax2.set_ylabel("USD open price")
    plt.text(
        1.0,
        0.0,
        """publish0x.com/@simplyrangel
github.com/simplyrangel""",
        transform=ax1.transAxes,
        fontsize=10,
        ha="right",
        va="bottom",
        color="gray",
        alpha=0.5,
        )
    fig.tight_layout()
    img.savefig()
    plt.close()






