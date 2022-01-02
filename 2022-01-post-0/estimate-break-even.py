import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
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
results = pd.DataFrame(
    np.nan,
    columns=["rebase_interest"],
    index=results_index,    
    )

# generate random 

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
    plt.close()
    
    
    
    
    
