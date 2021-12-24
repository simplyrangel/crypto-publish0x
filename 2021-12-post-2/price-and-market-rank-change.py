"""Investigate market cap rank change and its relation to price.

To investigate:
    -   How many times did the cmc rank change exceed -20 percent before 
        the daily open price exceeded twice the 30-day rolling mean price? 
        We should also look at the number of days between these signals and
        the 2x 30-day rolling mean exceedence. This will generate a dataset
        that looks like: 
        
        -   First multiindex level is an instance the daily open price  
            exceeded multiple of the 30-day rolling mean. 
        -   Second multiindex level represents the dates when the coin's 
            cmc rank changed at least some percent relative to its previous
            week. At first glance, it seems a good cmc rank percent change
            is 20 percent or more. 
        -   The columns include: cmc rank percent change, number of days
            before daily open price exceedence, etc

"""
import numpy as np
import pandas as pd
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
set_rcparams()

# pandas index slices:
idx = pd.IndexSlice

# -------------------------------------------------------
# Read data.
# -------------------------------------------------------
rankings = pd.read_hdf("bin/cmc-rank-histories-thru-2021-12-19.hdf")
coins_of_interest = pd.read_excel(
    "coins-of-interest.xlsx",
    comment="#",
    index_col=[0],
    )
coins_of_interest = coins_of_interest.sort_values(
    by="YTD percent change",
    ascending=False,
    )

# -------------------------------------------------------
# Rank change calculations.
# -------------------------------------------------------
# market cap ranks every first Sunday of the month:
mcr_first_sunday = rankings[~rankings.index.to_period("m").duplicated()]

# market cap rank changes per month:
dmcr_per_month = mcr_first_sunday.diff()

# market cap rank change percent per month:
mcr_first_sunday_shift = mcr_first_sunday.copy()
new_index = mcr_first_sunday.index.tolist()
mcr_first_sunday_shift.index = new_index[1:] + ["dropme"]
dmcr_per_month_p = dmcr_per_month / mcr_first_sunday_shift
dmcr_per_month_p = dmcr_per_month_p.iloc[:-1]
dmcr_per_month_p.index = pd.to_datetime(dmcr_per_month_p.index)

# market cap rank changes per week, and percent change
# per week:
dmcr_per_week = rankings.diff()
rankings_shift = rankings.copy()
new_rankings_index = rankings.index.tolist()
rankings_shift.index = new_rankings_index[1:] + ["dropme"]
dmcr_per_week_p = dmcr_per_week / rankings_shift
dmcr_per_week_p = dmcr_per_week_p[:-1]
dmcr_per_week_p.index = pd.to_datetime(dmcr_per_week_p.index)

# restrict rankings to 2021:
rankings2021 = rankings.loc["2021-01-01":].copy()
dmcr_per_month = dmcr_per_month.loc["2021-01-01":].copy()
dmcr_per_month_p = dmcr_per_month_p.loc["2021-01-01":].copy()
dmcr_per_week = dmcr_per_week.loc["2021-01-01":].copy()
dmcr_per_week_p = dmcr_per_week_p.loc["2021-01-01":].copy()

# -------------------------------------------------------
# Plot prep.
# -------------------------------------------------------
def mark_cmcr_changes(
    s,
    interval,
    yloc,
    tframe,
    linestyle,
    textstyle,
    ):
    s0 = s[
        (s <= interval[0])
        & (s > interval[1])
        ]
    for date in s0.index:
        plt.axvline(
            date,
            **linestyle,
            )
        plt.text(
            date,
            yloc,
            "%.1f percent %s rank change"%(s0[date]*100,tframe),
            **textstyle,
            )

# define linestyle:
l0style = {
    "color": "black",
    "alpha": 1.0,
    "linestyle": "--",
    "zorder": 9,
    "linewidth":1,
    }
t0style = {
    "color": "black",
    "fontsize": 10,
    "rotation": 90,
    "ha": "right",
    "va": "bottom",
    "alpha": 1.0,
    "zorder":9,
    }
l1style = {
    "color": "black",
    "alpha": 1.0,
    #"linestyle": "--",
    "zorder": 10,
    "linewidth": 1.0,
    }
t1style = {
    "color": "black",
    "fontsize": 10,
    "rotation": 90,
    "ha": "right",
    "va": "bottom",
    "alpha": 1.0,
    "zorder":9,
    }


# -------------------------------------------------------
# Plot.
# -------------------------------------------------------
with PdfPages("bin/coins-of-interest-2.pdf") as pdf:
    for coin in coins_of_interest.index:
        
        # read price data:
        ticker = coins_of_interest.loc[coin,"ticker"]
        price_df = pd.read_csv(
            "bin/%s-usd-max.csv"%(ticker.lower()),
            index_col=[0],
            parse_dates=True,
            )
        
        # calculate rolling averages:
        price_df["1week_mean"] = price_df.price.rolling(7).mean()
        price_df["2week_mean"] = price_df.price.rolling(14).mean()
        price_df["30day_mean"] = price_df.price.rolling(30).mean()
        
        # slice out 2021 data
        price_df = price_df["2021-01-01":].copy()
        
        # -----------------------------------------------
        # plot price history:
        plt.figure()
        plt.title("%s (%s)"%(coin,ticker))
        plt.plot(
            price_df.index,
            price_df.price,
            color="blue",
            label="Opening price",
            alpha=0.5,
            )
        plt.plot(
            price_df.index,
            price_df["2week_mean"],
            color="red",
            alpha=1.0,
            linewidth=2,
            linestyle="--",
            label="14-day rolling mean",
            )
        plt.plot(
            price_df.index,
            price_df["30day_mean"],
            color="blue",
            alpha=1.0,
            linewidth=2,
            linestyle="--",
            label="30-day rolling mean",
            )
        
        # show coin market cap rank changes on the 
        # interval [0.25,0.5] and [0.5,1.0]:
        s = dmcr_per_week_p[coin]
        mark_cmcr_changes(
            s, 
            [-0.25,-0.5],
            price_df.price.min(),
            "weekly",
            l0style,
            t0style,
            )
        mark_cmcr_changes(
            s, 
            [-0.5,-1.0],
            price_df.price.min(),
            "weekly",
            l1style,
            t1style,
            )
        
        # finish plot:
        plt.xticks(
            price_df.index[::14], #every 14 days
            rotation=45,
            ha="right",
            )
        plt.xlabel("week")
        plt.ylabel("open price [$]")
        plt.legend(fontsize=8)
        plt.grid()
        plt.tight_layout()
        pdf.savefig()
        plt.close()
        
        # -----------------------------------------------
        # plot same data, but this time divide the
        # daily price by the 14-day rolling mean and 
        # the 30-day rolling mean:
    for coin in coins_of_interest.index:
    
        # read price data:
        ticker = coins_of_interest.loc[coin,"ticker"]
        price_df = pd.read_csv(
            "bin/%s-usd-max.csv"%(ticker.lower()),
            index_col=[0],
            parse_dates=True,
            )
        
        # calculate rolling averages:
        price_df["1week_mean"] = price_df.price.rolling(7).mean()
        price_df["2week_mean"] = price_df.price.rolling(14).mean()
        price_df["30day_mean"] = price_df.price.rolling(30).mean()
        
        # slice out 2021 data
        price_df = price_df["2021-01-01":].copy()
        data14 = price_df.price/price_df["2week_mean"]
        data30 = price_df.price/price_df["30day_mean"]
        
        # plot:
        plt.figure()
        plt.title("%s (%s)"%(coin,ticker))
        plt.plot(
            price_df.index,
            data14,
            color="red",
            label="Opening price / 14-day mean",
            alpha=1.0,
            linewidth=2,
            )
        plt.plot(
            price_df.index,
            data30,
            color="blue",
            label="Opening price / 30-day mean",
            alpha=1.0,
            linewidth=2,
            )
        
        # show weekly coin market cap rank changes on the 
        # interval [0.25, 0.5]:
        s = dmcr_per_week_p[coin]
        mark_cmcr_changes(
            s, 
            [-0.2,-0.5],
            data14.min(),
            "weekly",
            l0style,
            t0style,
            )
        
        # show weekly coin market cap rank changes on the 
        # interval [0.5,1.0]:
        mark_cmcr_changes(
            s, 
            [-0.5,-1.0],
            data14.min(),
            "weekly",
            l1style,
            t1style,
            )
        
        # finish plot:
        plt.xticks(
            price_df.index[::14], #every 14 days
            rotation=45,
            ha="right",
            )
        plt.xlabel("week")
        plt.ylabel("open price / rolling mean")
        plt.ylim([0.3,6.0])
        plt.legend(fontsize=8)
        plt.grid()
        plt.tight_layout()
        pdf.savefig()
        plt.close()










