"""Show Ohm accrual throughout the year was the dispersed rebase rewards
estimated in generate-dispersions.py.
"""
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

# -------------------------------------------------------
# Read data.
# -------------------------------------------------------
rebase_rates = pd.read_csv(
    "bin/2022-02-25-rebase-rate-estimates.csv",
    index_col=[0],
    parse_dates=True,
    )

# -------------------------------------------------------
# Accrue Ohm.
# -------------------------------------------------------
def ohm_accrual_sim(
    ohmi, #number of Ohm purchased
    purchase_usd, #price of 1 Ohm
    rebase_rates=rebase_rates,
    ):
    df = pd.DataFrame(
        np.nan,
        columns=["ohms"],
        index=rebase_rates.index,
        )
    df.iloc[0].loc["ohms"] = ohmi
    for rebase_id in range(1, len(df.index)):
        ohm0 = df.iloc[rebase_id-1].ohms
        r = rebase_rates.iloc[rebase_id].uniform_distr_rates
        df.iloc[rebase_id].loc["ohms"] = ohm0*(1.0+r)
    df["break_even_usd"] = purchase_usd / df.ohms
    return df

# current Ohm as of 2022-02-25: 
current_ohm = 3.2349 
current_usd_spent = 763.2893 #USD

# simulate purchases at 1-Ohm price as of 2022-02-25:
ohm_price = 45.37 #USD; 2022-02-25:20:57:00
ohm_purchase_mesh = [0] + [2*x for x in range(1,21)]
frames = []
for op in ohm_purchase_mesh:
    print(op)
    ohmi = current_ohm + op
    purchase_usd = current_usd_spent + op*ohm_price
    ohm_accrued = ohm_accrual_sim(ohmi,purchase_usd)
    frames.append(ohm_accrued)
results = pd.concat(frames,keys=ohm_purchase_mesh)

# -------------------------------------------------------
# Plot.
# -------------------------------------------------------
alpha_mesh = np.linspace(0.5,1.0,len(ohm_purchase_mesh))

# break even points:
plt.figure()
for alpha,op in zip(alpha_mesh,ohm_purchase_mesh):
    df = results.loc[op]
    plt.plot(
        df.index,
        df.break_even_usd,
        color="black",
        #alpha=alpha,      
        linewidth=1,  
        )
#plt.legend(fontsize=8)
plt.grid()
plt.xlabel("date")
plt.ylabel("break even USD")
plt.xticks(
    df.index[::14*3],
    rotation=45,
    ha="right",
    )
plt.tight_layout()

# accrued Ohm:
plt.figure()
for alpha,op in zip(alpha_mesh,ohm_purchase_mesh):
    df = results.loc[op]
    plt.plot(
        df.index,
        df.ohms,
        color="black",
        alpha=alpha,      
        linewidth=1,  
        )
#plt.legend(fontsize=8)
plt.grid()
plt.xlabel("date")
plt.ylabel("accrued Ohm")
plt.xticks(
    df.index[::14*3],
    rotation=45,
    ha="right",
    )
plt.tight_layout()



plt.show()













        
