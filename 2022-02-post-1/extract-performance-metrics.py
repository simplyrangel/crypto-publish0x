"""Extract performance metrics from the LCC portfolio data."""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# set local paths to enable imports:
from _path import setup_paths
setup_paths()

# pandas index slices:
idx = pd.IndexSlice

# -----------------------------------------------------
# Create multiindex dataframe for each
# coin portfolio.
# -----------------------------------------------------
# Large Cap Portfolio data:
lcc = pd.read_excel(
    "bin/lcc-portfolio-performance.xlsx",
    index_col=[0],
    parse_dates=True,    
    )

# calculate current portfolio return:
current_value = lcc.coin_usd_value.iloc[-1]
current_deposit_sum = lcc.deposits_usd.iloc[-1]
current_return = current_value / current_deposit_sum

# read active coins:
lcc_coins = pd.read_csv(
    "bin/all-accounts.csv",
    comment="#",
    index_col=[0,1]
    )
cbpro_coins = lcc_coins.loc[idx["coinbase pro",:],"coin"].tolist()
kucoin_coins = lcc_coins.loc[idx["kucoin",:],"coin"].tolist()
cbpro_frames = []
kucoin_frames = []
for coin in cbpro_coins:
    df = pd.read_excel(
        "bin/cbpro-data/%s-cbpro-data.xlsx"%(coin.upper()),
        sheet_name="portfolio_performance",
        index_col=[0],
        parse_dates=True,
        )
    cbpro_frames.append(df)
for coin in kucoin_coins:
    df = pd.read_excel(
        "bin/kucoin-data/%s-kucoin-data.xlsx"%(coin.upper()),
        sheet_name="portfolio_performance",
        index_col=[0],
        parse_dates=True,
        )
    kucoin_frames.append(df)

# concatenate into multiindex dataframes:
cbpro_data = pd.concat(
    cbpro_frames,
    keys=cbpro_coins,
    names=["coin","date"],
    )
kucoin_data = pd.concat(
    kucoin_frames,
    keys=kucoin_coins,
    names=["coin","date"],
    )
allcoin_data = pd.concat(
    [cbpro_data,kucoin_data],    
    )

# save: 
allcoin_data.to_hdf(
    "bin/%s-all-coin-data.hdf"%(datetime.today().strftime("%Y-%m-%d")),
    "w",
    mode="w",
    )

# -----------------------------------------------------
# extract current metrics on each coin:
# -----------------------------------------------------
coin_metrics = pd.concat(
    [
        cbpro_data.groupby("coin").last(),
        kucoin_data.groupby("coin").last(),
        ],    
    )

# calculate coin USD value ratio against total
# portfolio USD value:
coin_metrics["portfolio_value_ratio"] = (
    coin_metrics.coin_usd_value 
    / current_value
    )

# calculate coin USD deposit ratio against total
# portfolio USD deposit value:
coin_metrics["portfolio_deposit_ratio"] = (
    coin_metrics.usd_deposits 
    / current_deposit_sum
    )

# calculate raw USD value difference between
# deposits and current coin USD value:
coin_metrics["gain_or_loss_usd"] = (
    coin_metrics.coin_usd_value 
    - coin_metrics.usd_deposits
    )

# sort by performance:
coin_metrics = coin_metrics.sort_values(
    by="performance",
    ascending=False,
    )

# round to three decimal places:
coin_metrics = coin_metrics.round(3)

# save coin metrics:
coin_metrics.to_excel(
    "bin/%s-coin-metrics.xlsx"%(datetime.today().strftime("%Y-%m-%d")),
    )







