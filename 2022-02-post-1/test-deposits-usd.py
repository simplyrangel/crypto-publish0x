import numpy as np
import pandas as pd
import sys
from datetime import datetime

# set local paths to enable imports:
from _path import setup_paths
setup_paths()

# KuCoin API:
from kucoin.account import account as kuaccount

# Coinbase API:
from cbpro._api import apiwrapper
from cbpro.account import account as cbaccount

# generic portfolio:
from portfolio import portfolio

# ----------------------------------------------------------------
# Coinbase portfolio USD deposits.
# ----------------------------------------------------------------
# extract coinbase pro account id's:
coinbase_api_key = "bin/coinbase-pro-system76-laptop.secret"
cbapi = apiwrapper()
cbapi.read_keyfile(coinbase_api_key)
cb_accounts = cbapi.query("/accounts")
cb_accounts = pd.DataFrame(cb_accounts).set_index("currency")

# extract USD deposits to the coinbase pro portfolio:
# right now I do not have a straightforward way to implement getting
# the USD deposits into the portfolio, so we'll hardcode it here:
#
# TODO: cbpro has a pagination limit of 1000 entries. The USD 
#       ledger now has more than 1000 entries, but my code does
#       not account for pagination yet. Update the code to 
#       account for pagination.
usd_account_id = cb_accounts.loc["USD","id"]
usd_account = cbaccount(
    "USD",
    usd_account_id,
    coinbase_api_key,
    )

# extract the USD ledger:
usd_account.get_ledger()
usd_account_ledger = usd_account.return_ledger()
usd_account_ledger.to_excel("bin/cbpro-data/cbpro-usd-ledger.xlsx")

# the ledger shows USD deposits as transfers from my default portfolio.
# let's extract these transfers as the LCC portfolio's deposits. Visual
# inspection of the USD account's ledger shows my default account's 
# USD address is: 
# f3616669-0ad8-4376-ad07-f72301b17b0c
#
# We need to query the LCC portfolio USD account's ledger for transfers
# from this address. 
default_usd_address = "f3616669-0ad8-4376-ad07-f72301b17b0c"

# TODO: EXTRACT ONLY DEFAULT USD ADDRESSES
cbpro_usd_deposits = usd_account_ledger[
    (usd_account_ledger.type=="transfer")
    ].resample("D"
    ).sum(
    )

# save data:
cbpro_usd_deposits.to_excel("bin/cbpro-data/cbpro-usd-deposits.xlsx")

# ----------------------------------------------------------------
# KuCoin portfolio USD deposits.
# ----------------------------------------------------------------
# get kucoin accounts and add to the large cap coin portfolio:
kucoin_api_key = "bin/kucoin-system76-personal-laptop.secret"
di = "2021-11-01"
de = datetime.today().strftime("%Y-%m-%d")

# KuCoin deposits are made with either Solana (SOL) or 
# Stellar Lumens (XLM) from my Coinbase Pro account. These
# are then converted to USDT before DCA purchases:
usdt_account = kuaccount("USDT",kucoin_api_key)
usdt_account.set_date_range(di,de)
usdt_account.get_ledger()
usdt_ledger = usdt_account.return_ledger()

# extract the exchange pairs:
usdt_ledger["exchange_pair"] = usdt_ledger.context.apply(
    lambda x: str(x.split(",")[0].split(":")[-1].replace('"',"")) 
    )

# calculate the deposits:
kucoin_usd_deposits = usdt_ledger[
    (usdt_ledger.exchange_pair=="SOL-USDT")
    | (usdt_ledger.exchange_pair=="XLM-USDT")    
    ].resample("D"
    ).sum(
    )

# save data:
usdt_ledger.to_excel("bin/kucoin-data/usdt-ledger.xlsx")
kucoin_usd_deposits.to_excel("bin/kucoin-data/kucoin-usd-deposits.xlsx")



