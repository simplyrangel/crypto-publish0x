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
gov15 = pd.read_hdf("bin/2022-01-15-algorand-governance-period-2.hdf")
gov17 = pd.read_hdf("bin/2022-01-18-algorand-governance-period-2.hdf")
gov_period1 = pd.read_hdf("bin/2022-01-15-algorand-governance-period-1.hdf")

# extract eligible accounts:
gov15_eligible = gov15[gov15.eligible==True].copy()
gov17_eligible = gov17[gov17.eligible==True].copy()
gov_period1_eligible = gov_period1[gov_period1.eligible==True].copy()

# set indices:
gov15 = gov15.set_index("address",drop=False)
gov17 = gov17.set_index("address",drop=False)
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
    gov15_eligible.shape[0],
    gov15_eligible.committed_algos.sum()/1e6,
    edgecolor="blue",
    facecolor="none",
    s=200,
    label="Gov. period 2 (eligible 2022-01-15)",    
    )
plt.scatter(
    gov17_eligible.shape[0],
    gov17_eligible.committed_algos.sum()/1e6,
    color="blue",
    s=200,
    label="Gov. period 2 (eligible 2022-01-17)",    
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









