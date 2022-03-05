"""Plot governance data."""
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
# Data read and extraction.
# -----------------------------------------------------
# read data:
gov_period2 = pd.read_hdf("bin/2022-02-23-algorand-governance-period-2.hdf")
gov_period1 = pd.read_hdf("bin/2022-01-15-algorand-governance-period-1.hdf")

# extract eligible accounts:
gov_period2_eligible = gov_period2[gov_period2.eligible==True].copy()
gov_period1_eligible = gov_period1[gov_period1.eligible==True].copy()

# set indices:
gov_period2 = gov_period2.set_index("address",drop=False)
gov_period1 = gov_period1.set_index("address",drop=False)

# -----------------------------------------------------
# Plot setup.
# -----------------------------------------------------
img = imghelper(
    save_dir="bin",
    img_series="gov",
    save_flag=True,    
    )

# -----------------------------------------------------
# Gov. accounts and committed value.
# -----------------------------------------------------
fig,ax = plt.subplots()
plt.title("""Algorand Governance period 2
total committed algos vs number of eligible governors""")

# governance period 2:
plt.scatter(
    gov_period2_eligible.shape[0],
    gov_period2_eligible.committed_algos.sum()/1e6,
    color="blue",
    s=200,
    label="Gov. period 2 (eligible 2022-02-23)",    
    )

# final gov period 1 numbers:
plt.scatter(
    gov_period1_eligible.shape[0],
    gov_period1_eligible.committed_algos.sum()/1e6,
    color="green",
    s=200,
    label="Gov. period 1 (final eligible count)",    
    )

# finish plot:
add_markings(ax)
plt.legend(fontsize=12)
plt.grid()
plt.xlabel("number of governors")
plt.ylabel("total committed Algos [millions]")
plt.xlim([45e3,75e3])
plt.ylim([1000,4000])
img.savefig()
plt.close()

# -----------------------------------------------------
# Top remaining whales.
# -----------------------------------------------------
cutoff = 25
gov_period2_eligible_whales = gov_period2_eligible.sort_values(
    by="committed_algos",
    ascending=False,
    ).iloc[:cutoff,:].copy(
    )
gov_period2_total = gov_period2_eligible.committed_algos.sum()
gov_period2_eligible_whales["ratio"] = (
    gov_period2_eligible_whales.committed_algos
    / gov_period2_total
    )

# plot:
fig,ax = plt.subplots()
plt.title("""Algorand Governance Period 2
top %d whales Algo commitments"""%cutoff)
plt.scatter(
    gov_period2_eligible_whales.committed_algos/1e6,
    gov_period2_eligible_whales.ratio,    
    color="blue",
    s=200,
    label="Largest %d account commitments" %cutoff,
    )

# finish plot:
add_markings(ax)
plt.legend(fontsize=12)
plt.grid()
plt.xlabel("committed Algos [millions]")
plt.ylabel("committed Algos / total period commitment")
img.savefig()
plt.close()

# -----------------------------------------------------
# Top whale cutoff percentage control.
# -----------------------------------------------------
gov_period1_total = gov_period1_eligible.committed_algos.sum()
gov_period2_total = gov_period2_eligible.committed_algos.sum()
cutoff_list = [1,2,3,4]+[5*x for x in range(1,60)]
ratio_list_p1 = []
ratio_list_p2 = []
for ci in cutoff_list:
    dfi1 = gov_period1_eligible.sort_values(
        by="committed_algos",
        ascending=False,
        ).iloc[:ci,:].copy(
        )
    dfi2 = gov_period2_eligible.sort_values(
        by="committed_algos",
        ascending=False,
        ).iloc[:ci,:].copy(
        )
    ratio1 = dfi1.committed_algos.sum() / gov_period1_total
    ratio2 = dfi2.committed_algos.sum() / gov_period2_total
    ratio_list_p1.append(ratio1)
    ratio_list_p2.append(ratio2)
fig,ax = plt.subplots()
plt.title("""Algorand Governance Period 2
eligible whale commitments relative to total committed""")
plt.plot(
    cutoff_list,
    ratio_list_p2,
    color="blue",    
    zorder=10,
    label="Period 2 ( 2022-02-23)",
    )
plt.plot(
    cutoff_list,
    ratio_list_p1,
    color="red",
    alpha=0.5,    
    linestyle="--",
    label="Period 1 (final)",
    )
# finish plot:
add_markings(ax)
plt.legend(fontsize=12)
plt.grid()
plt.xlabel("Number of whales")
plt.ylabel("Eligible whale commitments\nrelative to total eligible committed")
img.savefig()
plt.close()

# save data for use in write-latex-tables.py:
df = pd.DataFrame(
    [cutoff_list,ratio_list_p1,ratio_list_p2],
    index=["cutoff","ratio_p1", "ratio_p2"],    
    ).transpose(
    )
df.to_excel("bin/whale-control.xlsx")


