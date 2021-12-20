"""Consider several coins of interest."""
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
from styleguide import set_rcparams, imghelper, add_markings
set_rcparams()

# pandas index slices:
idx = pd.IndexSlice

# -------------------------------------------------------
# Market cap rank changes per month.
# -------------------------------------------------------
cmc_history = pd.read_hdf("bin/cmc-scrape-results-thru-2021-12-19.hdf")
rankings = pd.read_hdf("bin/cmc-rank-histories-thru-2021-12-19.hdf")
dmc_per_month = rankings.resample("4W"
    ).first(
    ).fillna(value=np.nan
    ).diff(
    )
cmc_today = cmc_history.loc[idx["2021-12-12",:],].reset_index()
df = cmc_today.set_index("name")

# coin comparisons:
# these coins identified by past market price response to 
# large coin market cap ranking jumps:
known_cmc_movers = [
    "XYO",
    "Solana",
    "Kadena",    
    ]

# coins of interested identified through several iterations
# of data-explorer.py with different parameters:
coins_of_interest = [
    "JUST",
    "inSure DeFi",
    #"Proton",
    "Function X",
    "Phantasma",
    #"Orchid",    
    ]

# colorwheel:
colorwheel = {
    "JUST": "blue",
    "inSure DeFi": "orange",
    "Proton": "purple",
    "Function X": "green",
    "Phantasma": "red",
    "Orchid": "fuchsia",    
    }

# -------------------------------------------------------
# Plot known movers.
# -------------------------------------------------------
img = imghelper(
    "bin",
    "img",
    True,    
    )
with PdfPages("bin/known-movers.pdf") as pdf:
    for coin in known_cmc_movers:
        fig,ax1 = plt.subplots()
        plt.title("%s market cap changes and price"%coin)
        ax1.set_xlabel("week")
        ax1.set_ylabel("market cap rank change per month",color="red")
        ax1.tick_params(axis="y",labelcolor="red")
        plt.xticks(ticks=dmc_per_month.index[::2],rotation=45)
        ax1.scatter(
            dmc_per_month.index,
            dmc_per_month[coin],
            label=coin,
            color="red",
            marker="v",
            s=100,
            )
        ax1.plot(
            dmc_per_month.index,
            dmc_per_month[coin],
            label="",
            color="red",
            alpha=0.7,
            )
        plt.legend(loc="upper left")
        plt.axhline(0,color="black",label="")
        
        # plot price history:
        prices = pd.read_csv(
            "bin/%s-price-history.csv"%coin,
            index_col=[0],
            parse_dates=True,
            infer_datetime_format=True,
            )
        ax2 = ax1.twinx()
        ax2.plot(
            prices.index,
            prices.Open,
            color="gray",
            )
        ax2.set_ylabel("USD open price")
        add_markings(ax1)
        fig.tight_layout()
        pdf.savefig()
        img.savefig()
        plt.close()

# -------------------------------------------------------
# Plot coins of interest.
# -------------------------------------------------------
with PdfPages("bin/coins-of-interest.pdf") as pdf:
    for coin in coins_of_interest:
        fig,ax1 = plt.subplots()
        plt.title("""%s market cap change per month
2020-01-01 through 2021-12-19"""%coin)
        plt.scatter(
            dmc_per_month.index,
            dmc_per_month[coin],
            label="%s\ncurrent rank: %d"%(coin,df.loc[coin,"cmc_rank"]),
            color=colorwheel[coin],
            marker="v",
            s=100,
            )
        plt.plot(
            dmc_per_month.index,
            dmc_per_month[coin],
            label="",
            color=colorwheel[coin],
            alpha=0.7,
            )
        plt.legend(loc="upper left")
        plt.grid()
        plt.xticks(ticks=dmc_per_month.index[::2],rotation=45)
        plt.axhline(0,color="black",label="")
        plt.xlabel("week")
        plt.ylabel("market cap rank change per month")
        plt.ylim([-400,250])
        plt.tight_layout()
        add_markings(ax1)
        pdf.savefig()
        img.savefig()
        plt.close()





