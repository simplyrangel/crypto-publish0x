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
from datetime import datetime,timedelta

# set local paths to enable imports:
from _path import setup_paths
setup_paths()

# plot setup:
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from styleguide import set_rcparams, add_markings, imghelper
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
dmcr_per_week = dmcr_per_week.loc["2021-01-01":].copy()
dmcr_per_week_p = dmcr_per_week_p.loc["2021-01-01":].copy()

# -------------------------------------------------------
# Data collection.
# -------------------------------------------------------
frames = []
for coin in coins_of_interest.index:
    
    # read price data:
    ticker = coins_of_interest.loc[coin,"ticker"]
    price_df = pd.read_csv(
        "bin/%s-usd-max.csv"%(ticker.lower()),
        index_col=[0],
        parse_dates=True,
        )
    
    # calculate rolling means and price ratios:
    price_df["30day_mean"] = price_df.price.rolling(30).mean()
    price_df["ratio_30day_mean"] = price_df.price / price_df["30day_mean"]
    
    # slice out 2021 data
    price_df = price_df["2021-01-01":].copy()
    
    # identify dates when daily price exceeded some multiple of the 
    # 30-day rolling mean:
    bound = 1.75
    dates_over_bound = list(price_df[price_df.ratio_30day_mean >= bound].index)
    first_dates = [dates_over_bound[0]]
    dates_of_interest = dates_over_bound[1:]
    for i in range(1,len(dates_of_interest)):
        db = dates_of_interest[i-1]
        dc = dates_of_interest[i]
        if db+timedelta(days=1) != dc:
            first_dates.append(dc)
    
    # remove tzinfo:
    first_dates = [x.replace(tzinfo=None) for x in first_dates]
    
    # identify weeks before each 'first date' where the coin's 
    # cmc rank change exceeded some tolerance:
    cmcr_bound = -0.2
    s = dmcr_per_week_p[coin]
    cmcr_over_bound = s[s<=cmcr_bound]
    coin_frames = []
    for date in first_dates:
        date = date.replace(tzinfo=None)
        before_date = [x for x in cmcr_over_bound.index if x < date]
        before_date = [x.replace(tzinfo=None) for x in before_date]
        df = pd.DataFrame(
            np.nan,
            columns=["cmc_rank_change_p","ndays"],
            index=before_date,
            )
        for d in before_date:
            df.loc[d,"cmc_rank_change_p"] = s[d]
            df.loc[d,"ndays"] = date - d
        coin_frames.append(df)
    coin_results = pd.concat(
        coin_frames,
        keys=first_dates,
        names=["30day_price_exceedance_event","cmc_rank_change_event"],
        )
    frames.append(coin_results)

# results for coins of interest:
results = pd.concat(
    frames,
    keys=coins_of_interest.index,
    names=["coin"],
    )
results.to_excel("bin/price-vs-rolling-mean.xlsx")

# consider specific coins and their cmcr change events 
# closest to each major price change:
highlight_coins = [
    "XYO",
    "Solana",
    "Kadena",
    "Terra",
    "Polygon",
    ]
highlight_frames = []
for coin in highlight_coins:
    coin_data = results.loc[coin
        ].groupby("30day_price_exceedance_event"
        ).ndays.min(
        )
    highlight_frames.append(coin_data)
highlight_results = pd.concat(
    highlight_frames,
    keys=highlight_coins,
    names=["coin","30day price exceedance event"],
   )
highlight_results.to_excel("bin/price-vs-rolling-mean-highlight.xlsx")

# -------------------------------------------------------
# Plot data.
# -------------------------------------------------------
img = imghelper(
    "bin",
    "results-hist",    
    )
with PdfPages("bin/coins-of-interest-3.pdf") as pdf:
    
    # consider only cmcr change events closest to each
    # major price change:
    all_coin_data = []
    for coin in results.index.levels[0]:
        try:
            coin_data = results.loc[coin
                ].groupby("30day_price_exceedance_event"
                ).ndays.min(
                )
            ll = coin_data.apply(lambda x: x.days).tolist()
            if len(ll) >= 1:
                all_coin_data += ll
        except:
            pass
    
    # plot histogram:
    fig, ax = plt.subplots()
    plt.figure()
    plt.title("""Number of days between a CMC rank change >20% and
an opening price jump 1.75x the 30-day rolling mean""")
    plt.hist(
        all_coin_data,
        bins=20,
        color="blue",
        )
    plt.xlabel("number of days")
    plt.ylabel("instances")
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()
    
    # plot histogram, but show highlight coins:
    stacked_colors = [
        "purple",
        "orange",
        "red",
        "green",
        "black",
        "blue",
        ]
    stacked_data = []
    for coin in highlight_coins:
        coin_data = results.loc[coin
            ].groupby("30day_price_exceedance_event"
            ).ndays.min(
            )
        stacked_data.append(coin_data.apply(lambda x: x.days).tolist())
    other_coins = [
        x for x in results.index.levels[0] 
        if x not in highlight_coins
        ]
    other_coin_data = []
    for coin in other_coins:
        try:
            coin_data = results.loc[coin
                ].groupby("30day_price_exceedance_event"
                ).ndays.min(
                )
            ll = coin_data.apply(lambda x: x.days).tolist()
            if len(ll) >= 1:
                other_coin_data += ll
        except:
            pass
    stacked_data.append(other_coin_data)
    stacked_labels = highlight_coins + ["others"]
    fig, ax = plt.subplots()
    plt.title("""Number of days between a CMC rank change >20% and
an opening price jump 1.75x the 30-day rolling mean""")
    plt.hist(
        stacked_data,
        label=stacked_labels,
        color=stacked_colors,
        histtype="barstacked",
        bins=20,
        )
    plt.xlabel("number of days")
    plt.ylabel("instances")
    plt.legend(fontsize=10)
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()
    
    # show only highlight coins:
    fig,ax = plt.subplots()
    plt.title("""Number of days between a CMC rank change >20% and
an opening price jump 1.75x the 30-day rolling mean""")
    plt.hist(
        stacked_data[:-1],
        label=stacked_labels[:-1],
        color=stacked_colors[:-1],
        histtype="barstacked",
        bins=20,
        )
    plt.xlabel("number of days")
    plt.ylabel("instances")
    plt.legend(fontsize=10)
    plt.ylim([0,15])
    plt.yticks([0,5,10,15])
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()

    # cumulative histogram:
    fig,ax = plt.subplots()
    plt.title("""Number of days between a CMC rank change >20% and
an opening price jump 1.75x the 30-day rolling mean""")
    plt.hist(
        all_coin_data,
        cumulative=True,
        density=True,
        bins=20,
        color="blue",
        #histtype="step",
        linewidth=3,
        )
    plt.ylim([0,1.2])
    plt.xlabel("number of days")
    plt.ylabel("cumulative instances (norm)")
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()




