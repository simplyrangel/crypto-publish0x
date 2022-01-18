"""Calculate baseline dollar cost average (DCA) curves using BTC."""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# pandas index slices:
idx = pd.IndexSlice

# -----------------------------------------------------
# Read data.
# -----------------------------------------------------
# we could query an API to get BTC price data or 
# extract it manually from an online source, but its 
# more straightforward to just read in the BTC portfolio
#  spreadsheet created in  lcc-portfolio-data.py and 
# grab the daily prices from it:
btc_portfolio = pd.read_excel(
    "bin/cbpro-data/BTC-cbpro-data.xlsx",
    sheet_name="portfolio_performance",
    index_col=[0],
    parse_dates=True,
    )

# -----------------------------------------------------
# Create DCA baseline portfolio.
# -----------------------------------------------------
bp = pd.DataFrame(
    np.nan,
    index=btc_portfolio.index,
    columns=["deposits_usd","number_of_coins"],    
    )
bp["coin_price"] = btc_portfolio.coin_price.copy()

# simulate deposits every Thursday:
deposit_value = 10.0 #USD 
deposit_dates = pd.date_range(
    start="2021-09-23", #first Thur. on portfolio date range
    end=bp.index[-1], #last date on portfolio date range
    freq="7D", #every seven days
    )
bp.loc[deposit_dates,"deposits_usd"] = [
    deposit_value*x for x 
    in range(1,len(deposit_dates)+1)
    ]

# simulate dollar cost averaging:
coin_counter = 0
for dca_date in deposit_dates:
    purchased_coin = deposit_value / bp.loc[dca_date,"coin_price"]
    coin_counter += purchased_coin
    bp.loc[dca_date,"number_of_coins"] = coin_counter

# save baseline portfolio:
bp = bp.ffill()
bp["coin_usd_value"] = bp.number_of_coins*bp.coin_price
bp["performance"] = bp.coin_usd_value / bp.deposits_usd
bp.to_excel("bin/2022-01-16-btc-dca-baseline-portfolio.xlsx")



