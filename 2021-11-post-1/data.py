"""Fetch and setup data used for this Publish0x post.

Evaluate Large Cap Coin portfolio performance from creation 
(Sep. 19, 2021) through post publication weekend (Nov. 10, 2021).

Submodule dependencies:
    -   crypto-api @84b00c3
"""
import pandas as pd
import numpy as np
import pickle as pkl
from datetime import datetime

# set local paths to enable imports:
from _path import setup_paths
setup_paths()

# Coinbase API:
from cbpro.portfolio import portfolio
from cbpro.markets import markets

# Pandas' index slices:
idx = pd.IndexSlice

# -------------------------------------------------
# Read Coinbase ledger.
# -------------------------------------------------
setup_portfolio = False
if setup_portfolio:
    myportfolio = portfolio(
        "myportfolio",
        save_loc="2021-11-post-1/bin",
        )
    myportfolio.read_keyfile("bin/large-cap-coins-key.secret")
    myportfolio.auto_setup()
    myportfolio.save()
else:
    pfi = "2021-11-post-1/bin/2021-11-12T14-35-04-myportfolio.pkl"
    with open(pfi,"rb") as of:
        myportfolio = pkl.load(of)

# -------------------------------------------------
# Read market data.
# -------------------------------------------------
# create markets object:
m = markets("m")

# get daily price history for every coin in the 
# ledger from portfolio start to the Publish0x
# post publication date:
coin_history = myportfolio.return_daily_history()
di = coin_history.index[0]
de = datetime(year=2021,month=11,day=11)
days_index = pd.date_range(
    start=di,
    end=de,
    freq="D",
    )
market_history = pd.DataFrame(
    np.nan,
    index=days_index,
    columns=coin_history.columns,
    )
coins = [
    x for x in market_history.columns 
     if "USD" not in x
    ]
for coin in coins:
    print("Querying %s market history..."%coin)
    df = m.price_history(
        "%s-USD" %coin,
        start=di,
        end=de,
        granularity=86400, #daily
        )
    market_history.loc[:,coin] = df.close.tolist()
    
# set USD and USD backed stablecoin values equal
# to 1.0:
market_history.loc[:,"USD"] = 1.0
market_history.loc[:,"USDC"] = 1.0
    
# save coin market history:
market_history.to_hdf(
    "2021-11-post-1/bin/market-history.hdf",
    "w",
    mode="w",    
    )



