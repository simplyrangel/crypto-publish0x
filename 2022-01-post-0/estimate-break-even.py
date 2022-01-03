"""Estimate the 1-Ohm minimum value necessary to break even if a user
purchases 1-Ohm today (2022-01-02) at about $350.0 USD and cashes out 
at the start of next year (2023-01-02). 

The accrued Ohm from 2021-01-02 to 2023-01-02 was simulated with eight-hour
rebase compound interest events every day during the time range. Potential 
rebase compound interest rates were taken from the OlympusDAO OIP-18 document:

https://forum.olympusdao.finance/d/77-oip-18-reward-rate-framework-and-reduction

The potential rebase rate range will change when the total Ohm supply 
exceeds 10 million. The date when the total Ohm supply exceeds 10 million
was estimated by extrapolating a near-linear Ohm supply growth based on the
last few months of total Ohm token supply. The Ohm supply per day was 
manually taken from:

https://dune.xyz/queries/285132

and saved to a .csv file in bin/. 

"""
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from numpy.random import default_rng
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

# -------------------------------------------------------
# Ohm supply.
# -------------------------------------------------------
# Ohm token supply data manually copied into a 
# spreadsheet from: 
# https://dune.xyz/queries/285132
ohm_supply = pd.read_csv(
    "bin/ohm-supply-2022-01-02-thru-2021-05-30.csv",
    index_col=[0],
    parse_dates=True,
    comment="#",
    )

# fit an exponential curve to the ohm supply to 
# extrapolate future growth. Not sure how Numpy
# polyfit() would handle datetimes, so we'll extrapolate
# by number of days from the first data point.
ohm_supply = ohm_supply.sort_index(ascending=True)
ohm_supply["days_since_start"] = range(0,ohm_supply.shape[0])
def func(x,m,b):
    return m*x + b

# The exponential emission rate appears to slow midway 
# through 2021, so let's restrict the curvefit algorithm
# to some subjective start date within the data date range: 
popt,pcov = curve_fit(
    func,
    ohm_supply.days_since_start[120:],
    ohm_supply.total_supply[120:],
    )

# define the extrapolation end date:
est_index = pd.date_range(
    start=ohm_supply.index[0],
    end="2022-12-31",
    freq="d",    
    )
ohm_supply_est = pd.DataFrame(
    np.nan,
    columns=[0],
    index=est_index,
    )

# extrapolate ohm emissions:
ohm_supply_est["days_since_start"] = range(0,ohm_supply_est.shape[0])
ohm_supply_est["total_supply"] = func(ohm_supply_est.days_since_start,*popt)

# identify date where extrapolated Ohm supply
# passes 10e6 tokens:
new_epoch_start = ohm_supply_est[
    (ohm_supply_est.total_supply>=10e6)
    ].index[0]

# -------------------------------------------------------
# Rebase compound interest.
# -------------------------------------------------------
# According to OIP-18, the rebase compound interest
# is adjusted according to the total Ohm token supply.
# The two "epochs" we care about, and their corresponding
# min and max rebase compound interest values, are:
#
# [1e6,10e6] Ohm -> [0.1587, 0.3058] rebase percent
# [10e6, 100e6] Ohm -> [0.1186,0.1587] rebase interest
#
# OIP-18 link:
# https://forum.olympusdao.finance/d/77-oip-18-reward-rate-framework-and-reduction
#
# The discrete rebase interest rate will vary with every
# rebase. Rebases occur every eight hours (3x per day). 
# Let's assume uniform distributions across the rebase 
# rate ranges and randomly choose discrete rates per 
# rebase event.
#
# create results pandas dataframe with index of rebase
# events:
results_index = pd.date_range(
    start="2022-01-02",
    freq="8h",
    periods=int(3*365),    
    )
results_oip18 = pd.DataFrame(
    np.nan,
    columns=["ohms","rebase_rate"],
    index=results_index,    
    )

# generate random rebase rates for the first epoch:
e0_dates = results_oip18[results_oip18.index<=new_epoch_start].index
e0_rebase_rate = default_rng().uniform(
    low=0.1587e-2,
    high=0.3058e-2,
    size=len(e0_dates),    
    )
results_oip18.loc[e0_dates,"rebase_rate"] = e0_rebase_rate

# generate random rebase reates for the next epoch:
e1_dates = results_oip18[results_oip18.index>new_epoch_start].index
e1_rebase_rate = default_rng().uniform(
    low=0.1186e-2,
    high=0.1587e-2,
    size=len(e1_dates),    
    )
results_oip18.loc[e1_dates,"rebase_rate"] = e1_rebase_rate

# assume we buy one Ohm today (2022-01-02) at the first 
# rebase instance:
results_oip18.iloc[0].loc["ohms"] = 1.0

# simulate Ohm accumulating interest according to the
# randomized rebase rates:
for rebase_id in range(1, len(results_oip18.index)):
    ohm0 = results_oip18.iloc[rebase_id-1].ohms
    r = results_oip18.iloc[rebase_id].rebase_rate
    results_oip18.iloc[rebase_id].loc["ohms"] = ohm0*(1.0+r)
    
# repeat the same analysis, with best-case max rebase
# rate for both epochs:
results_max_oip18 = pd.DataFrame(
    np.nan,
    columns=["ohms","rebase_rate"],
    index=results_index,    
    )
results_max_oip18.iloc[0].loc["ohms"] = 1.0
results_max_oip18.loc[e0_dates,"rebase_rate"] = 0.3058e-2
results_max_oip18.loc[e1_dates,"rebase_rate"] = 0.1587e-2
for rebase_id in range(1, len(results_max_oip18.index)):
    ohm0 = results_max_oip18.iloc[rebase_id-1].ohms
    r = results_max_oip18.iloc[rebase_id].rebase_rate
    results_max_oip18.iloc[rebase_id].loc["ohms"] = ohm0*(1.0+r)

# repeat the same analysis, with worst-case min rebase
# rate for both epochs:
results_min_oip18 = pd.DataFrame(
    np.nan,
    columns=["ohms","rebase_rate"],
    index=results_index,    
    )
results_min_oip18.iloc[0].loc["ohms"] = 1.0
results_min_oip18.loc[e0_dates,"rebase_rate"] = 0.1587e-2
results_min_oip18.loc[e1_dates,"rebase_rate"] = 0.1186e-2
for rebase_id in range(1, len(results_min_oip18.index)):
    ohm0 = results_min_oip18.iloc[rebase_id-1].ohms
    r = results_min_oip18.iloc[rebase_id].rebase_rate
    results_min_oip18.iloc[rebase_id].loc["ohms"] = ohm0*(1.0+r)

# -------------------------------------------------------
# Calculate break even points at the end of 2022, or
# start of 2023.
# -------------------------------------------------------
# price of 1 Ohm at 4:53pm CST 2022-01-02: 
# about $350.0 USD
ohm_usd_buy = 350.0 #USD 
be_best = ohm_usd_buy / results_max_oip18.iloc[-1].ohms
be_unif = ohm_usd_buy / results_oip18.iloc[-1].ohms
be_worst = ohm_usd_buy / results_min_oip18.iloc[-1].ohms
breakeven_df = pd.DataFrame(
    [be_best,be_unif,be_worst],
    columns=["Ohm USD value"],
    index=[
        "best-case break-even point",
        "uniform r distr. break-even point",
        "worst-case break-even point",
        ]
    )
breakeven_df["Ohms"] = [
    results_max_oip18.iloc[-1].ohms,
    results_oip18.iloc[-1].ohms,
    results_min_oip18.iloc[-1].ohms,
    ]
breakeven_df = breakeven_df.round(3)
breakeven_df.to_excel("bin/break-even-ohm-usd-values.xlsx")

# -------------------------------------------------------
# Plot.
# -------------------------------------------------------
img = imghelper(
    "bin",
    "results",    
    )
with PdfPages("bin/plots.pdf") as pdf:
    
    # plot ohm supply:
    plt.figure()
    plt.title("Ohm supply")
    plt.plot(
        ohm_supply.index,
        ohm_supply.total_supply/1e6,
        color="blue",
        label="Total Ohm supply",
        linewidth=8,
        alpha=0.3,
        zorder=9,
        )
    plt.plot(
        ohm_supply_est.index,
        ohm_supply_est.total_supply/1e6,
        color="black",
        linewidth=3,
        label="Total Ohm supply (extrapolated)",
        zorder=10,
        )
    plt.axhline(
        10,
        linestyle="--",
        color="red",
        label="",
        )
    plt.axvline(
        new_epoch_start,
        linestyle="--",
        color="red",
        label="",
        )
    plt.scatter(
        new_epoch_start,
        10,
        color="red",
        label="New emission epoch\nest start date: %s"%(
            new_epoch_start.strftime("%Y-%m-%d"),
            ),
        s=100,
        zorder=12,
        )
    plt.xticks(ohm_supply_est.index[::14],rotation=45,ha="right")
    plt.ylim([0,15])
    plt.xlim([
        ohm_supply.index[0], 
        datetime.strptime("2022-05-01", "%Y-%m-%d"),
        ])
    plt.grid()
    plt.legend(fontsize=10)
    plt.xlabel("date")
    plt.ylabel("Ohm supply [millions]")
    plt.tight_layout()
    pdf.savefig()
    img.savefig()
    plt.close()

    # plot estimated rebase rates:
    plt.figure()
    plt.title("Simulated Ohm rebase rates")
    plt.plot(
        results_max_oip18.index,
        results_max_oip18.rebase_rate*100.0,
        label="OIP-18 best-case",
        color="gray",
        linestyle="--",
        )
    plt.scatter(
        results_oip18.index,
        results_oip18.rebase_rate*100.0,
        label="OIP-18 with uniform distr.",
        color="black",
        alpha=0.5,
        s=10,
        )
    plt.plot(
        results_min_oip18.index,
        results_min_oip18.rebase_rate*100.0,
        label="OIP-18 worst-case",
        color="black",
        linestyle="--"
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("Rebase compound rate [%]")
    rebase_per_2weeks = int(14*3)
    plt.xticks(results_oip18.index[::rebase_per_2weeks],rotation=45,ha="right")
    plt.tight_layout()
    pdf.savefig()
    img.savefig()
    plt.close()
    
    # plot estimated Ohm accumulation:
    plt.figure()
    plt.title("Simulated Ohm accumulation")
    plt.plot(
        results_max_oip18.index,
        results_max_oip18.ohms,
        label="OIP-18 best-case",
        color="gray",
        linestyle="--",
        )
    plt.plot(
        results_oip18.index,
        results_oip18.ohms,
        label="OIP-18 with uniform distr.",
        color="black",
        )
    plt.plot(
        results_min_oip18.index,
        results_min_oip18.ohms,
        label="OIP-18 worst-case",
        color="black",
        linestyle="--"
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("Accrued Ohm tokens")
    rebase_per_2weeks = int(14*3)
    plt.xticks(results_oip18.index[::rebase_per_2weeks],rotation=45,ha="right")
    plt.tight_layout()
    pdf.savefig()
    img.savefig()
    plt.close()
    
    
    
    
