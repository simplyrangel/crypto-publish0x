"""Write LaTeX tables."""
import numpy as np
import pandas as pd
from datetime import datetime
import textemplates

# pandas index slices:
idx = pd.IndexSlice

# -----------------------------------------------------
# Read data and extract information.
# -----------------------------------------------------
# Large Cap Portfolio data:
lcc = pd.read_excel(
    "../bin/lcc-portfolio-performance.xlsx",
    index_col=[0],
    parse_dates=True,    
    )

# calculate current portfolio return:
current_value = lcc.coin_usd_value.iloc[-1]
current_deposit_sum = lcc.deposits_usd.iloc[-1]
current_return = current_value / current_deposit_sum

# BTC DCA baseline portfolio:
btc_baseline = pd.read_excel(
    "../bin/2022-01-16-btc-dca-baseline-portfolio.xlsx",
    index_col=[0],
    parse_dates=True,    
    )

# all coin data:
allcoin_data = pd.read_hdf("../bin/2022-01-16-all-coin-data.hdf")

# coin metrics:
coin_metrics = pd.read_excel(
    "../bin/2022-01-16-coin-metrics.xlsx",
    index_col=[0],
    parse_dates=True,
    )

# datetime today string:
datestr = "2022-01-16"

# -----------------------------------------------------
# Write tables.
# -----------------------------------------------------
# performance summary:
textemplates.performance_summary(
    28,
    current_value,
    current_deposit_sum,
    current_return,
    "Large Cap Coin (LCC) Portfolio performance snapshot %s; summary."%datestr,
    "textables/summary.tex",
    )

# top 5 coins:
top5_coins = coin_metrics.index[:5]
top5_df = coin_metrics.loc[top5_coins,:]
textemplates.coin_performance_lite(
    top5_df,
    "Large Cap Coin (LCC) Portfolio performance snapshot %s; top 5 performing coins."%datestr,
    "textables/top5-lite.tex",
    )

# bottom 5 coins:
bottom5_coins = coin_metrics.index[-5:]
bottom5_df = coin_metrics.loc[bottom5_coins,:]
textemplates.coin_performance_lite(
    bottom5_df,
    "Large Cap Coin (LCC) Portfolio performance snapshot %s; bottom 5 performing coins."%datestr,
    "textables/bottom5-lite.tex",
    )

# most coins in portfolio:
largest_5_coins = coin_metrics.sort_values(
    by="portfolio_value_ratio",
    ascending=False,
    ).index[:5]
largest_5_df = coin_metrics.loc[largest_5_coins,:]
textemplates.coin_performance_lite(
    largest_5_df,
    "Large Cap Coin (LCC) Portfolio performance snapshot %s; five largest coin holdings by USD value."%datestr,
    "textables/largest-holdings-lite.tex",
    )

# all coins in portfolio:
textemplates.coin_performance_lite(
    coin_metrics.sort_values(by="portfolio_value_ratio",ascending=False),
    "Large Cap Coin (LCC) Portfolio performance snapshot %s; all holdings."%datestr,
    "textables/all-coins-lite.tex",
    )





