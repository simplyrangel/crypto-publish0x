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
            dmcr_per_month.index,
            dmcr_per_month[coin],
            label=label,
            color="blue",
            marker="v",
            s=100,
            )
        plt.plot(
            dmcr_per_month.index,
            dmcr_per_month[coin],
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
        plt.xticks(ticks=dmcr_per_month.index,rotation=45,ha="right")
        yt = dmcr_per_month[coin].max()*1.5
        yb = dmcr_per_month[coin].min()*1.25
        plt.ylim([yb,yt])
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # plot rank change percent per month vs time:
        title_1 = make_title_1(coins_of_interest,coin)
        plt.figure()
        plt.title(title_1)
        plt.scatter(
            dmcr_per_month_p.index,
            dmcr_per_month_p[coin],
            label=label,
            color="blue",
            marker="v",
            s=100,
            )
        plt.plot(
            dmcr_per_month_p.index,
            dmcr_per_month_p[coin],
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
        plt.ylabel("CMC monthly rank change /\nmonth's starting rank")
        plt.xticks(ticks=dmcr_per_month_p.index,rotation=45,ha="right")
        yt = dmcr_per_month_p[coin].max()*1.5
        yb = dmcr_per_month_p[coin].min()*1.25
        plt.ylim([yb,yt])
        plt.tight_layout()
        pdf.savefig()
        plt.close()

# plot only percent changes with constant Y axis range:
with PdfPages("bin/coin-of-interest-1.pdf") as pdf:
    for coin in coins_of_interest.index:
        title_1 = make_title_1(coins_of_interest,coin)
        plt.figure()
        plt.title(title_1)
        
        # monthly percent change:
        plt.scatter(
            dmcr_per_month_p.index,
            dmcr_per_month_p[coin],
            label="monthly percent change",
            color="blue",
            marker="v",
            s=200,
            zorder=10,
            )
        plt.plot(
            dmcr_per_month_p.index,
            dmcr_per_month_p[coin],
            label="",
            color="blue",
            alpha=1,
            zorder=9,
            )

        # weekly percent change:
        plt.scatter(
            dmcr_per_week_p.index,
            dmcr_per_week_p[coin],
            label="weekly percent change",
            color="red",
            marker="x",
            s=100,
            zorder=8,
            alpha=0.5,
            )
        plt.plot(
            dmcr_per_week_p.index,
            dmcr_per_week_p[coin],
            label="",
            color="red",
            alpha=0.5,
            zorder=7,
            )
        
        # horizontal lines:
        plt.axhline(
            0.0,
            color="black",
            label="no change",
            )
        for hline in [0.25,0.5]:
            plt.axhline(
                hline,
                color="black",
                linestyle="--",
                linewidth=1,
                label="",
                )
            plt.axhline(
                -hline,
                color="black",
                linestyle="--",
                linewidth=1,
                label="",
                )
            plt.text(
                dmcr_per_month_p.index[0],
                hline,
                "%d percent change"%(hline*100),
                color="black",
                ha="left",
                va="bottom",
                fontsize=8,
                )
            plt.text(
                dmcr_per_month_p.index[0],
                -hline,
                "%d percent change"%(-hline*100),
                color="black",
                ha="left",
                va="bottom",
                fontsize=8,
                )
        
        # finish plot:
        plt.legend(fontsize=8)
        plt.grid()
        plt.xlabel("week")
        plt.ylabel("CMC percent rank change")
        plt.xticks(ticks=dmcr_per_month_p.index,rotation=45,ha="right")
        plt.ylim([-1,1])
        plt.tight_layout()
        pdf.savefig()
        plt.close()








