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

# extract coins that experienced a monthly coin market
# cap rank jump forward of at least some cutoff value, and
# are still within some current market cap cutoff:
cmc_today = cmc_history.loc[idx["2021-12-12",:],].reset_index()
df = cmc_today.set_index("name")
top_rank_filter = 50
bottom_rank_filter = 500
cmc_today_filter = cmc_today[
    (cmc_today.cmc_rank >= top_rank_filter)
    & (cmc_today.cmc_rank <= bottom_rank_filter)
    ]
cutoff = [
    -25,
    -50,
    -75,
    -100,
    -150,
    -200, 
    -300,   
    #-400,
    ]
filtered_coins = {}
for cc in cutoff:
    df_filtered = dmc_per_month[
        dmc_per_month<=cc
        ].dropna(
            how="all",
            axis=1,
        )
    coins_of_interest = df_filtered.columns
    coins_of_interest = [
        x for x in coins_of_interest 
        if x in cmc_today_filter.name.tolist()
        and (len(dmc_per_month[x].dropna().tolist()) > 4)
        and (abs(dmc_per_month[x].min()) > 1.5*dmc_per_month[x].max())
        and (dmc_per_month[x].sort_values(ascending=True).iloc[2] <= 0.5*cc )
        ]
    print(len(coins_of_interest))
    filtered_coins[cc] = coins_of_interest

# -------------------------------------------------------
# Plot.
# -------------------------------------------------------
def fig_title(jump,fi,fe):
    return """CMC movers with at least one %d jump forward 
within [%d,%d] current market cap"""%(jump,fi,fe)

# plot flag:
plot_flag = False

# plot each cutoff:
if plot_flag:
    for cc in cutoff:
        pdf_fi = "bin/dmc-filtered-%d.pdf"%(abs(cc))
        title = fig_title(cc,top_rank_filter,bottom_rank_filter)
        with PdfPages(pdf_fi) as pdf:
            for coin in filtered_coins[cc]:
                try:
                    plt.figure()
                    plt.title(title)
                    plt.scatter(
                        dmc_per_month.index,
                        dmc_per_month[coin],
                        label="%s\ncurrent rank: %d"%(coin,df.loc[coin,"cmc_rank"]),
                        color="red",
                        marker="v",
                        s=100,
                        )
                    plt.plot(
                        dmc_per_month.index,
                        dmc_per_month[coin],
                        label="",
                        color="red",
                        alpha=0.7,
                        )
                    plt.legend()
                    plt.grid()
                    plt.legend(loc="upper left")
                    plt.axhline(0,color="black",label="",linewidth=1)
                    plt.xticks(ticks=dmc_per_month.index[::2],rotation=45)
                    plt.tight_layout()
                    pdf.savefig()
                    plt.close()
                except:
                    print("coin %s failed"%coin)





