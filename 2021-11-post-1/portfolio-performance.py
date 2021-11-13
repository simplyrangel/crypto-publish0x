"""Evaluate Large Cap Coin portfolio performance from creation 
(Sep. 19, 2021) through post publication weekend (Nov. 10, 2021).

Submodule dependencies:
    -   crypto-api @84b00c3

Note on IOTX:
I exited my IOTX position because of the price discrepency between
Coinbase and the rest of the market. I haven't implemented sells 
or withdrawal handling in crypto-api yet, so I have to hand-code IOTX
data after the withdrawal date. The withdrawal date was Nov. 3, 
2021. 

Note on FIL and ICP:
I exited my FIL and ICP positions after further research into their
respective use cases and backgrounds made me lose confidence in their
midterm and longterm values. I haven't implemented sells or withdrawal
handling in crypto-api yet, so I have to hand-code FIL and ICP data
after their withdrawal dates. FIL coin withdrawal date was Nov. 8, 
2021. ICP withdrawal date was Oct. 30, 2021.

"""
import numpy as np
import pandas as pd
import pickle as pkl
from datetime import datetime

# set local paths to enable imports:
from _path import setup_paths
setup_paths()

# Coinbase API:
from cbpro.portfolio import portfolio

# plot setup:
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from styleguide import set_rcparams, imghelper

# Pandas' index slices:
idx = pd.IndexSlice

# -------------------------------------------------
# Read data.
# Data queried from Coinbase API in data.py. 
# -------------------------------------------------
# Coinbase portfolio:
pfi = "2021-11-post-1/bin/2021-11-12T14-35-04-myportfolio.pkl"
with open(pfi,"rb") as of:
    myportfolio = pkl.load(of)

# Market data:
market_data = pd.read_hdf("2021-11-post-1/bin/market-history.hdf")
market_data = market_data[:"2021-11-10"]

# -------------------------------------------------
# Portfolio performance.
# -------------------------------------------------
# extract USD deposits from the coinbase pro ledger:
coin_usd_deposits = myportfolio.return_usd_deposits()
coin_usd_deposits = coin_usd_deposits[:"2021-11-10"]

# extract coins in the ledger:
ledger = myportfolio.return_ledger()
coins = ledger.index.levels[0].tolist()
coins = [
    x for x in coins 
    if "USD" not in x
    and "XLM" not in x
    ]

# extract USD transactions per market pair from the
# coinbase pro ledger:
new_ledger_index = [
    "product_id",
    "order_id",
    "created_at",
    ]
keep_cols = [
    "amount",
    "balance",
    "type",
    "transaction_no",    
    ]
ledger = ledger.reset_index(
    ).set_index(new_ledger_index
    ).sort_index(
    )
usd_transactions = ledger[ledger.coin=="USD"]
usd_transactions = usd_transactions.loc[
    idx[:,:,:],
    keep_cols,
    ].copy(
    )

# extract cumulative USD deposits into each coin 
# in the ledger:
for coin in coins:
    pair = "%s-USD"%coin
    cdf = usd_transactions.loc[idx[pair,:,:],"amount"]
    cdf = cdf.resample("D",level="created_at").sum()
    coin_usd_deposits[coin] = cdf.cumsum()

# remove 'total' column from coin_usd_deposits, because
# it represents ledger-wide USD deposits, not coin-specific
# USD deposits:
coin_usd_deposits = coin_usd_deposits.drop(columns=["total"])
coin_usd_deposits = coin_usd_deposits.loc[:"2021-11-10"]

# handle IOTX withdrawal:
iotx_usd_deposits = coin_usd_deposits.loc["2021-11-03","IOTX"]
coin_usd_deposits.loc["2021-11-04":, "IOTX"] = iotx_usd_deposits

# negative coin_usd_deposits currently represent deposits,
# aka USD purchases of a given coin. Multiply the entire
# dataframe by (-1) to make purchases positive:
coin_usd_deposits *= -1.0

# calculate daily coin-specific performance throughout
# the entire portfolio. 
# remember to handle IOTX withdrawal:
daily_history = myportfolio.return_daily_history()
daily_history = daily_history.loc[:"2021-11-10"]
final_iotx_value = daily_history.loc["2021-11-03","IOTX"]
daily_history.loc["2021-11-04":,"IOTX"] = final_iotx_value
value_per_coin = daily_history*market_data

# handle IOTX withdrawal:
final_iotx_value = value_per_coin.loc["2021-11-04","IOTX"]
final_usd_value = value_per_coin.loc["2021-11-03","USD"]
value_per_coin.loc["2021-11-04":,"IOTX"] = final_iotx_value
value_per_coin.loc["2021-11-04":,"USD"] = final_usd_value
return_per_coin = value_per_coin / coin_usd_deposits

# replace Filecoin and Internet-Computer final values with 
# NaN instead of zeros to avoid plotting issues:
return_per_coin.loc["2021-10-30":,"ICP"] = np.nan
return_per_coin.loc["2021-11-08":,"FIL"] = np.nan

# calculate daily portfolio-wide performance:
total_portfolio_deposits = myportfolio.return_usd_deposits()
total_portfolio_deposits = total_portfolio_deposits[:"2021-11-10"]
total_portfolio_return = (
    value_per_coin.sum(axis=1) 
    / total_portfolio_deposits.total)

# extract best vs worst performing coins:
best2worst_coins = {}
for coin in coins:
    data = return_per_coin[coin].dropna()
    best2worst_coins[coin] = [data.iloc[-1]]
best2worst_coins = pd.DataFrame(best2worst_coins).transpose()
best2worst_coins.columns = ["return"]
best2worst_coins = best2worst_coins.sort_values(
    by="return",
    ascending=False,    
    )
best2worst_coins.to_excel("2021-11-post-1/bin/best2worst-coins.xlsx")

# -------------------------------------------------
# Plot.
# -------------------------------------------------
# standardize x-axis setup:
def setup_xaxis(df=return_per_coin):
    di = df.index[0]
    de = df.index[-1]
    plt.xlim(di,de)
    plt.xticks(df.index[::7],rotation=45) #weekly
    plt.xlabel("week")

# standardize break even line:
def show_breakeven():
    plt.axhline(
        1.0,
        color="black",
        label="break even",
        )

# create image object for .png file saves:
img = imghelper(
    save_dir="2021-11-post-1/bin",
    img_series="portfolio-perfomance",    
    )

# open pdf file and start plotting:
pdf_fi = "2021-11-post-1/bin/portfolio-performance.pdf"
with PdfPages(pdf_fi) as pdf:
    
    # total returns for entire portfolio:
    plt.figure()
    plt.title("""Large Cap Crypto fund
aggregate 26 coin performance thru Nov. 10, 2021""")
    plt.plot(
        total_portfolio_return,
        color="red",
        label="entire portfolio",
        )
    show_breakeven()
    setup_xaxis()
    plt.grid()
    plt.legend(fontsize=8)
    plt.ylabel("total USD value / cumulative USD deposits")
    plt.tight_layout()
    pdf.savefig()
    img.savefig()
    plt.close()
    
    # show all coin returns on the same plot,
    # and highlight the top 5 coins:
    top5 = best2worst_coins.index.tolist()[:5]
    not_top5 = [
        x for x in best2worst_coins.index 
        if x not in top5
        ]
    plt.figure()
    plt.title("""Large Cap Crypto fund
individual coin performance thru Nov. 10, 2021""")
    for coin in top5:
        plt.plot(
            return_per_coin.index,
            return_per_coin[coin],
            label=coin,
            zorder=10,
            )
    for coin in not_top5:
        if coin==not_top5[-1]:
            label="all others"
        else:
            label=""
        plt.plot(
            return_per_coin.index,
            return_per_coin[coin],
            color="gray",
            label=label,
            zorder=1,
            )
    show_breakeven()
    setup_xaxis()
    plt.grid()
    plt.legend(fontsize=8)
    plt.ylabel("USD value / cumulative deposits per coin")
    plt.ylim([0.5,2.5])
    plt.tight_layout()
    pdf.savefig()
    img.savefig()
    plt.close()
    
    # plot each coin individually:
    for coin in best2worst_coins.index:
        plt.figure()
        plt.title("""Large Cap Crypto fund
%s performance thru Nov. 10, 2021""" %coin)
        coin_label="%s (%.2fx)" %(
            coin,
            best2worst_coins.loc[coin,"return"],
            )
        portfolio_label="entire portfolio (%.2fx)"%(
            total_portfolio_return.iloc[-1],
            )
        plt.plot(
            return_per_coin.index,
            return_per_coin[coin],
            label=coin_label,
            color="blue",
            zorder=10,
            )
        plt.plot(
            total_portfolio_return,
            color="gray",
            label=portfolio_label,
            zorder=1,
            )
        show_breakeven()
        setup_xaxis()
        plt.legend(fontsize=8)
        plt.grid()
        plt.ylabel("USD value / cumulative deposits")
        plt.tight_layout()
        pdf.savefig()
        img.savefig()
        plt.close()






