"""Explore the scraped data."""
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
cmc_history = pd.read_hdf("bin/cmc-scrape-results-thru-2021-12-19.hdf")
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

# restrict rankings to 2021:
rankings2021 = rankings.loc["2021-01-01":].copy()

# calculate rank changes per month:
dmc_per_month = rankings2021.resample("4W"
    ).first(
    ).fillna(value=np.nan
    ).diff(
    )

# -------------------------------------------------------
# Plot coin of interest ranks through 2021.
# -------------------------------------------------------
def make_label(df,coin,tyd):
    s = df[coin].dropna()
    di,de = s.index[0],s.index[-1]
    ri,re = s.values[0],s.values[-1]
    dr = re-ri
    sdi,sde = di.strftime("%Y-%m-%d"), de.strftime("%Y-%m-%d")
    return """%s
rank on %s: %d
rank on %s: %d
rank change: %d
YTD value change: %.2f percent"""%(coin,sdi,ri,sde,re,dr,ytd)
    
def make_title_0(df,coin):
    return """%s (%s)
coin market cap rank through 2021"""%(coin,df.loc[coin,"ticker"])

def make_title_1(df,coin):
    return """%s (%s)
coin market cap rank change per month through 2021""" %(coin,df.loc[coin,"ticker"])

# plot to pdf:
with PdfPages("bin/coin-of-interest-0.pdf") as pdf:
    for coin in coins_of_interest.index:
        print(coin)
        
        # set up labels:
        ytd = coins_of_interest.loc[coin,"YTD percent change"]
        label = make_label(rankings2021,coin,ytd)
        title_0 = make_title_0(coins_of_interest,coin)
        
        # plot rank vs time:
        plt.figure()
        plt.title(title_0)
        plt.plot(
            rankings2021.index,
            rankings2021[coin],
            label=label,
            color="blue",
            )
        plt.legend(fontsize=8)
        plt.grid()
        plt.xlabel("week")
        plt.ylabel("CMC rank")
        plt.xticks(ticks=rankings2021.index[::2],rotation=45,ha="right")
        plt.tight_layout()
        pdf.savefig()
        plt.close()
        
        # plot rank change per month vs time:
        title_1 = make_title_1(coins_of_interest,coin)
        plt.figure()
        plt.title(title_1)
        plt.scatter(
            dmc_per_month.index,
            dmc_per_month[coin],
            label=label,
            color="blue",
            marker="v",
            s=100,
            )
        plt.plot(
            dmc_per_month.index,
            dmc_per_month[coin],
            label="",
            color="blue",
            alpha=0.5,
            )
        plt.axhline(
            0.0,
            color="black",
            label="no change",
            )
        plt.legend(fontsize=8)
        plt.grid()
        plt.xlabel("week")
        plt.ylabel("CMC rank change per month")
        plt.xticks(ticks=dmc_per_month.index[::2],rotation=45,ha="right")
        yt = dmc_per_month[coin].max()*1.5
        yb = dmc_per_month[coin].min()*1.25
        plt.ylim([yb,yt])
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # plot rank change percent per month vs time:
        title_1 = make_title_1(coins_of_interest,coin)
        plt.figure()
        plt.title(title_1)
        plt.scatter(
            dmc_percent.index,
            dmc_percent[coin],
            label=label,
            color="blue",
            marker="v",
            s=100,
            )
        plt.plot(
            dmc_percent.index,
            dmc_percent[coin],
            label="",
            color="blue",
            alpha=0.5,
            )
        plt.axhline(
            0.0,
            color="black",
            label="no change",
            )
        plt.legend(fontsize=8)
        plt.grid()
        plt.xlabel("week")
        plt.ylabel("CMC rank change percent per month")
        plt.xticks(ticks=dmc_percent.index[::2],rotation=45,ha="right")
        yt = dmc_percent[coin].max()*1.5
        yb = dmc_percent[coin].min()*1.25
        plt.ylim([yb,yt])
        plt.tight_layout()
        pdf.savefig()
        plt.close()


