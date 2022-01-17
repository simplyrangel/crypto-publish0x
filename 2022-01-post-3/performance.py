"""Assess performance of the Large Cap Crypto Fund."""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

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

# -----------------------------------------------------
# Read data and extract information.
# -----------------------------------------------------
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

# extract current metrics on each coin:
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
    "bin/%s-coin-metrics.xlsx"%datetime.today().strftime("%Y-%m-%d"),
    )

# -----------------------------------------------------
# Plot setup.
# -----------------------------------------------------
pdf = PdfPages("bin/lcc-plots.pdf")
img = imghelper(
    save_dir="bin",
    img_series="lcc",
    save_flag=False,    
    )

# local functions:
def show_metrics(
    xpoint,
    ypoint,
    dd=lcc.index[-1],
    current_value=current_value,
    current_deposit_sum=current_deposit_sum,
    current_return=current_return,
    zorder=12,    
    ):
    plt.scatter(
        xpoint,
        ypoint,
        color="red",
        s=100,
        zorder=zorder,
        label="metrics on %s\nvalue difference: $%.2f\nreturn: %.2fx" %(
            lcc.index[-1].strftime("%Y-%m-%d"),
            current_value - current_deposit_sum,
            current_return,
            ),
        )

# colorwheel:
top5_colorwheel = {
    0: "green",
    1: "red",
    2: "blue",
    3: "purple",
    4: "orange",    
    }
bottom5_colorwheel = top5_colorwheel

# benchmark colors:
benchmark_colorwheel = {
    "btc": "red",
    "eth": "blue",    
    }

# -----------------------------------------------------
# Plot entire portfolio performance.
# -----------------------------------------------------
# portfolio value vs deposits value:
fig,ax = plt.subplots()
plt.title("""Large Cap Coin (LCC) Portfolio
aggregate 28 coin peformance""")
plt.plot(
    lcc.index,
    lcc.coin_usd_value,
    color="blue",
    label="portfolio value: $%.2f"%(current_value),
    zorder=10,
    )
plt.plot(
    lcc.index,
    lcc.deposits_usd,
    color="black",
    label="cumulative deposits: $%.2f"%(current_deposit_sum),
    )
plt.xticks(
    lcc.index[::7],
    rotation=45,
    ha="right",
    )
show_metrics(lcc.index[-1],current_value)
plt.legend(fontsize=12)
plt.grid()
plt.xlabel("date")
plt.ylabel("USD value [$]")
add_markings(ax)
plt.tight_layout()
img.savefig()
pdf.savefig()
plt.close()

# portfolio returns:
fig,ax = plt.subplots()
plt.title("""Large Cap Coin (LCC) Portfolio
aggregate 28 coin performance""")
plt.plot(
    lcc.index,
    lcc.performance,
    color="blue",
    label="portfolio value: $%.2f"%(current_value),
    zorder=10,
    )
plt.axhline(
    1.0,
    color="black",
    label="cumulative deposits: $%.2f"%(current_deposit_sum),
    )
plt.xticks(
    lcc.index[::7],
    rotation=45,
    ha="right",
    )
show_metrics(lcc.index[-1],current_return)
plt.legend(fontsize=12)
plt.grid()
plt.xlabel("date")
plt.ylabel("portfolio value / cumulative deposits")
plt.ylim([0.7,1.5])
add_markings(ax)
plt.tight_layout()
img.savefig()
pdf.savefig()
plt.close()

# -----------------------------------------------------
# Plot top 5 performing coins.
# -----------------------------------------------------
top5_coins = coin_metrics.index[:5]
top5_iter = 0

# plot:
fig,ax = plt.subplots()
plt.title("""Large Cap Coin (LCC) Portfolio
constituent coin performances with top-5 highlighted""")
for coin in coin_metrics.index:
    df = allcoin_data.loc[idx[coin,:],].reset_index()
    if coin in top5_coins:
        color=top5_colorwheel[top5_iter]
        label="%s (%.2fx return)"%(coin.upper(),coin_metrics.loc[coin,"performance"])
        linewidth=3
        zorder=10
        top5_iter += 1
    else:
        color="gray"
        label=""
        linewidth=1
        zorder=1
    plt.plot(
        df.date,
        df.performance,
        color=color,
        label=label,
        linewidth=linewidth,
        zorder=zorder,
        )
plt.axhline(
    1,
    color="black",
    label="deposit value",    
    )
plt.xticks(
    lcc.index[::7],
    rotation=45,
    ha="right",
    )
plt.legend(fontsize=12,loc="upper left")
plt.grid()
plt.xlabel("date")
plt.ylabel("coin account value / coin USD purchase value")
plt.ylim([0.0,6])
add_markings(ax)
plt.tight_layout()
img.savefig()
pdf.savefig()
plt.close()

# -----------------------------------------------------
# Plot bottom 5 performing coins.
# -----------------------------------------------------
bottom5_coins = coin_metrics.index[-5:]
bottom5_iter = 0

# plot:
fig,ax = plt.subplots()
plt.title("""Large Cap Coin (LCC) Portfolio
constituent coin performances with bottom-5 highlighted""")
for coin in coin_metrics.index:
    df = allcoin_data.loc[idx[coin,:],].reset_index()
    if coin in bottom5_coins:
        color=bottom5_colorwheel[bottom5_iter]
        label="%s (%.2fx return)"%(coin.upper(),coin_metrics.loc[coin,"performance"])
        linewidth=3
        zorder=10
        bottom5_iter += 1
    else:
        color="gray"
        label=""
        linewidth=1
        zorder=1
    plt.plot(
        df.date,
        df.performance,
        color=color,
        label=label,
        linewidth=linewidth,
        zorder=zorder,
        )
plt.axhline(
    1,
    color="black",
    label="deposit value",    
    )
plt.xticks(
    lcc.index[::7],
    rotation=45,
    ha="right",
    )
plt.legend(fontsize=12,loc="upper left")
plt.grid()
plt.xlabel("date")
plt.ylabel("coin account value / coin USD purchase value")
plt.ylim([0.0,6])
add_markings(ax)
plt.tight_layout()
img.savefig()
pdf.savefig()
plt.close()

# -----------------------------------------------------
# Plot BTC and ETH.
# -----------------------------------------------------
# plot:
fig,ax = plt.subplots()
plt.title("""Large Cap Coin (LCC) Portfolio
Bitcoin (BTC) and Ethereum (ETH) performances""")
for coin in ["btc","eth"]:
    df = allcoin_data.loc[idx[coin,:],].reset_index()
    plt.plot(
        df.date,
        df.performance,
        color=benchmark_colorwheel[coin],
        label="%s (%.2fx return)"%(coin.upper(),coin_metrics.loc[coin,"performance"]),
        zorder=10,
        )
plt.plot(
    lcc.index,
    lcc.performance,
    color="gray",
    label="LCC Portfolio (%.2fx return)"%(current_return),
    zorder=1,
    alpha=0.5,
    )
plt.axhline(
    1,
    color="black",
    label="deposit value",    
    )
plt.xticks(
    lcc.index[::7],
    rotation=45,
    ha="right",
    )
plt.legend(fontsize=12,loc="upper right")
plt.grid()
plt.xlabel("date")
plt.ylabel("coin account value / coin USD purchase value")
plt.ylim([0.7,1.5])
add_markings(ax)
plt.tight_layout()
img.savefig()
pdf.savefig()
plt.close()

# -----------------------------------------------------
# Close pdf.
# -----------------------------------------------------
pdf.close()







