"""Generate potential OlympusDAO rebase reward rate dispersions through 2023 
based on OIP-18 and OIP-63. Rebase reward rate dispersions saved as .csv files
in bin/. 

Rebase reward rates change every epoch (every 8 hours) in response to market
conditions. An epoch's rebase reward rate however must fall into a range of
potential values. OIP-18 and OIP-63 define the range of potential rebase 
reward rate values according to the current Ohm supply. 

OIP-63 codifies the following actions while the Ohm supply remains below 1e7:
    -   Adjust the rebase reward rate from its current levels down to 
        0.1587 percent over four weeks starting 2022-01-03. The rates before
        OIP-63's implementation ranged on [0.1587, 0.400] based on anecdotal
        observation. 
    -   Four weeks from 2022-01-03 is 2022-01-31. This matches well with the 
        estimated date where the Ohm supply will exceed 10mil. 

After the Ohm supply exceeds 1e7, OIP-63 prescribes the following actions until
the Ohm supply exceeds 1e8:
    -   Rebase reward rates will be chosen such that the equivalent APY
        falls on the range [500,1000] percent. 
"""
import numpy as np
import pandas as pd
from numpy.random import default_rng
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
# Create rebase rewards bin.
# -------------------------------------------------------
# create results pandas dataframe with index of rebase
# events:
results_index = pd.date_range(
    start=datetime.today(), #today
    freq="8h",
    periods=int(3*365), #one year from today
    )
results = pd.DataFrame(
    np.nan,
    columns=["rebase_rate"],
    index=results_index,     
    )
results["rebase_count"] = range(0,len(results_index))

# -------------------------------------------------------
# Estimate rebase rewards rate during the 
# rewards rampdown.
# -------------------------------------------------------
# According to OlympusDAO subreddit mods, the epoch rewards
# rate ramp down that OIP-63 stipulates will end four
# weeks after OIP-63 started, or 2022-01-31. The current
# rewards have hovered around 5k percent APY, and by 
# 2022-01-31 they must be at 1k percent APY:
e0_index = results[(results.index <= "2022-02-01")].index
last_e0_rebase = results.loc[e0_index[-1], "rebase_count"]

# define the function to fit:
# let's assume a linear regression from current APY to 
# target APY:
current_rebase_rate = 0.003082
coeff = np.polyfit(
    [0,last_e0_rebase],
    [current_rebase_rate,0.003058],
    deg=1, 
    )
results.loc[e0_index,"rebase_rate"] = results.loc[
    e0_index,
    "rebase_count",
    ].apply(lambda x: coeff[0]*x + coeff[1]
    )

# -------------------------------------------------------
# Estimate rebase rewards rate once Ohm supply
# exceeds 10 million.
# -------------------------------------------------------
# 500 to 1000 percent APY:
apy_upper_bound = 10.0
apy_lower_bound = 5.0

# Let's create three different possible rebase reward
# rate sets:
#   -   The first is the "best-case" set where the rebase
#       reward rate is always its max
#   -   The second is the "worst-case" set where the
#       rebase reward rate is always its min
#   -   The third is a uniform distribution between the two
#
# define second epoch dates:
e1_index = results[(results.index > "2022-02-01")].index

# create the best-case set:
results["best_case_rates"] = results.rebase_rate.copy()
results.loc[e1_index, "best_case_rates"] = pow(apy_upper_bound, 1.0/1095.0) - 1.0

# create the worst-case set:
results["worst_case_rates"] = results.rebase_rate.copy()
results.loc[e1_index,"worst_case_rates"] = pow(apy_lower_bound, 1.0/1095.0) - 1.0

# create the uniform distribution:
results["uniform_distr_rates"] = results.rebase_rate.copy()
uniform_distr = default_rng().uniform(
    low=pow(apy_lower_bound, 1.0/1095.0) - 1.0,
    high=pow(apy_upper_bound, 1.0/1095.0) - 1.0,
    size=len(e1_index),    
    )
results.loc[e1_index,"uniform_distr_rates"] = uniform_distr

# save results:
results.to_csv("bin/rebase-rate-estimates.csv")

# -------------------------------------------------------
# Plot.
# -------------------------------------------------------
img = imghelper(
    save_dir="bin",
    img_series="rebase-rates",
    save_flag=True,    
    )
with PdfPages("bin/plots.pdf") as pdf:

    # through Feb. 2022:
    results_sub = results[results.index <= "2022-03-01"]
    fig,ax = plt.subplots()
    plt.title("Estimated OlympusDAO rebase reward rates")
    plt.plot(
        results_sub.index,
        results_sub.best_case_rates*100,
        color="gray",
        linestyle="--",
        label="equiv. APY: 1000 percent",
        )
    plt.plot(
        results_sub.index,
        results_sub.worst_case_rates*100,
        color="black",
        linestyle="--",
        label="equiv. APY: 500 percent",
        )
    plt.scatter(
        results_sub.index,
        results_sub.uniform_distr_rates*100,
        color="black",
        alpha=0.5,
        s=10,
        label="uniform distr."
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("rebase reward percent")
    plt.xticks(
        results_sub.index[::2*3],
        rotation=45,
        ha="right",
        )
    plt.tight_layout()
    plt.ylim([0.0, 0.4])
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()
    
    # Through 2023:
    fig,ax = plt.subplots()
    plt.title("Estimated OlympusDAO rebase reward rates")
    plt.plot(
        results.index,
        results.best_case_rates*100,
        color="gray",
        linestyle="--",
        label="equiv. APY: 1000 percent",
        )
    plt.plot(
        results.index,
        results.worst_case_rates*100,
        color="black",
        linestyle="--",
        label="equiv. APY: 500 percent",
        )
    plt.scatter(
        results.index,
        results.uniform_distr_rates*100,
        color="black",
        alpha=0.5,
        s=10,
        label="uniform distr."
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("rebase reward percent")
    plt.xticks(
        results.index[::2*7*3],
        rotation=45,
        ha="right",
        )
    plt.tight_layout()
    plt.ylim([0.0, 0.4])
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()




