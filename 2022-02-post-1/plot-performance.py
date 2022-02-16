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

# BTC DCA baseline portfolio:
btc_baseline = pd.read_excel(
    "bin/2022-02-12-btc-dca-baseline-portfolio.xlsx",
    index_col=[0],
    parse_dates=True,    
    )

# all coin data:
allcoin_data = pd.read_hdf("bin/2022-02-12-all-coin-data.hdf")

# coin metrics:
coin_metrics = pd.read_excel(
    "bin/2022-02-12-coin-metrics.xlsx",
    index_col=[0],
    parse_dates=True,
    )

# -----------------------------------------------------
# Plot setup.
# -----------------------------------------------------
pdf = PdfPages("bin/lcc-plots.pdf")
img = imghelper(
    save_dir="bin",
    img_series="lcc",
    save_flag=True,    
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
aggregate 27 coin peformance""")
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
aggregate 27 coin performance""")
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
plt.ylim([0.5,1.5])
add_markings(ax)
plt.tight_layout()
img.savefig()
pdf.savefig()
plt.close()

# -----------------------------------------------------
# Plot top 5 performing coins.
# -----------------------------------------------------
# exclude theta because we just started investing in it:
top5_coins = coin_metrics.index[:6]
top5_coins = [x for x in top5_coins if x!="theta"]
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
# exclude coins that we dropped:
bottom5_coins = coin_metrics.index[-8:]
bottom5_coins = [x for x in bottom5_coins if x not in ["opul","qnt","poly"]]
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
# Plot LCC BTC and baseline BTC performances.
# -----------------------------------------------------
# plot:
fig,ax = plt.subplots()
plt.title("""Large Cap Coin (LCC) Portfolio
Bitcoin (BTC) LCC and baseline DCA performances""")
for coin in ["btc"]:
    df = allcoin_data.loc[idx[coin,:],].reset_index()
    plt.plot(
        df.date,
        df.performance,
        color=benchmark_colorwheel[coin],
        label="%s LCC (%.2fx return)"%(coin.upper(),coin_metrics.loc[coin,"performance"]),
        zorder=10,
        )
plt.plot(
    btc_baseline.index,
    btc_baseline.performance,
    color="black",
    label="BTC baseline (%.2fx return)"%(btc_baseline.performance.iloc[-1]),
    zorder=1,
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
plt.ylim([0.5,1.5])
add_markings(ax)
plt.tight_layout()
img.savefig()
pdf.savefig()
plt.close()

# -----------------------------------------------------
# Close pdf.
# -----------------------------------------------------
pdf.close()







