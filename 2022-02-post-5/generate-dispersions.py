"""Generate potential OlympusDAO rebase reward rate dispersions through 2023 
based on OIP-18 and OIP-63. Rebase reward rate dispersions saved as .csv files
in bin/. 

This script generates the same rewards rate distribution used in the 
Publish0x post "OlympusDAO: my break-even price, and why I want to buy 
more despite massive losses". 

"""
import numpy as np
import pandas as pd
from numpy.random import default_rng
from scipy.optimize import curve_fit
from datetime import datetime, timedelta

# set local paths to enable imports:
from _path import setup_paths
setup_paths()

# pandas index slices:
idx = pd.IndexSlice

# -------------------------------------------------------
# Create rebase rewards bin.
# -------------------------------------------------------
# create results pandas dataframe with index of rebase
# events:
results_index = pd.date_range(
    start="2022-01-23", #today
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
results.to_csv("bin/2022-01-23-rebase-rate-estimates.csv")






