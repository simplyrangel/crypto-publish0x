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
gov1 = pd.read_hdf("bin/2022-01-15-algorand-governance-period-1.hdf")
gov2 = pd.read_hdf("bin/2022-01-15-algorand-governance-period-2.hdf")

# extract eligible accounts:
gov1_eligible = gov1[gov1.eligible==True].copy()
gov2_eligible = gov2[gov2.eligible==True].copy()

# overlap:
overlap = gov2.merge(
    gov1,
    on="address",
    suffixes=("gov2","gov1"),
    )
overlap_eligible = gov2.merge(
    gov1_eligible,
    on="address",
    suffixes=("gov2","gov1"),
    )

# set indices:
gov1 = gov1.set_index("address",drop=False)
gov2 = gov2.set_index("address",drop=False)

# calculate each account's committed algo percentage 
# of the total committed Algo per governance period:
gov1["committed_ratio"] = gov1.committed_algos / gov1.committed_algos.sum()
gov2["committed_ratio"] = gov2.committed_algos / gov2.committed_algos.sum()
gov1_eligible["committed_ratio"] = (
    gov1_eligible.committed_algos 
    / gov1_eligible.committed_algos.sum()
    )
gov2_eligible["committed_ratio"] = (
    gov2_eligible.committed_algos
    / gov2_eligible.committed_algos.sum()
    )

# -----------------------------------------------------
# By-the-numbers.
# -----------------------------------------------------
# open excel file:
with pd.ExcelWriter("bin/governance.xlsx") as writer:
    
    # extract data per period:
    for period_id,gov in enumerate([gov1, gov2]):
        frames = []
        eligible_gov = gov[gov.eligible==True]
        for df in [gov, eligible_gov]:
            frames.append(df.describe())
        
        # save data per period to different sheets
        # of the same excel file:
        results = pd.concat(frames,keys=["all","only eligible"])
        results.to_excel(writer,sheet_name="period %d summary"%(period_id+1))
    
    # do the same data extraction, but this time ignore
    # addresses with less than 1.0 Algo:
    for period_id,gov in enumerate([gov1, gov2]):
        frames = []
        gov_lt1 = gov[gov.committed_algos>1.0]
        eligible_gov = gov_lt1[gov_lt1.eligible==True]
        for df in [gov_lt1, eligible_gov]:
            frames.append(df.describe())
        results = pd.concat(frames,keys=["all","only eligible"])
        results.to_excel(writer,sheet_name="period %d summary gt 1Algo"%(period_id+1))

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

# governance period 1 (all accounts):
plt.scatter(
    gov1.shape[0],
    gov1.committed_algos.sum()/1e6,
    edgecolor="green",
    facecolor="none",
    linewidth=3,
    s=200,
    label="Gov. period 1 (all accounts)",    
    )

# governance period 1 (accounts eligible at end):
plt.scatter(
    gov1_eligible.shape[0],
    gov1_eligible.committed_algos.sum()/1e6,
    color="green",
    s=200,
    label="Gov. period 1 (eligible at end)",    
    )

# governance period 2 (all accounts):
plt.scatter(
    gov2.shape[0],
    gov2.committed_algos.sum()/1e6,
    edgecolor="blue",
    facecolor="none",
    linewidth=3,
    s=200,
    label="Gov. period 2 (all accounts)",    
    )
plt.scatter(
    gov2_eligible.shape[0],
    gov2_eligible.committed_algos.sum()/1e6,
    color="blue",
    s=200,
    label="Gov. period 2 (eligible Jan. 15, 2022)",    
    )

# finish plot:
plt.legend(fontsize=12)
plt.grid()
plt.xlabel("number of governors")
plt.ylabel("total committed Algos [millions]")
plt.xlim([45e3,80e3])
plt.ylim([100,430])
img.savefig()
plt.close()

# -----------------------------------------------------
# Plot committed distribution beneath 1 Algo.
# -----------------------------------------------------
gov1_below1algo = gov1[gov1.committed_algos <= 1.0]
gov2_below1algo = gov2[gov2.committed_algos <= 1.0]
fig, ax = plt.subplots()
plt.hist(
    gov1_below1algo.committed_algos,
    bins=20,    
    color="green",
    histtype="step",
    zorder=10,
    linewidth=3,
    label="Gov. period 1 accounts\nwith 1Algo or less committed: %d"%(
        len(gov1_below1algo.committed_algos)),
    )
plt.hist(
    gov2_below1algo.committed_algos,
    bins=20,    
    color="gray",
    label="Gov. period 2 accounts\nwith 1Algo or less committed: %d"%(
        len(gov2_below1algo.committed_algos)),
    )
plt.legend(fontsize=12)
img.savefig()
plt.close()

# -----------------------------------------------------
# Plot committed algo per account vs the
# percentage of total committed algo.
# -----------------------------------------------------
fig, ax = plt.subplots()
plt.scatter(
    gov1.committed_algos/1e6,
    gov1.committed_ratio,
    edgecolor="green",
    facecolor="none",
    s=200,
    alpha=0.5,
    label="Gov. period 1 (all accounts)",
    )
plt.scatter(
    gov1_eligible.committed_algos/1e6,
    gov1_eligible.committed_ratio,
    edgecolor="green",
    facecolor="none",
    s=200,
    label="Gov. period 1 (eligible at end)",
    )
plt.scatter(
    gov2.committed_algos/1e6,
    gov2.committed_ratio,
    edgecolor="blue",
    facecolor="none",
    s=200,
    label="Gov. period 2 (all accounts)",
    )
plt.legend(fontsize=12,loc="lower right")
plt.grid()
plt.xlabel("committed algos per governor [millions]")
plt.ylabel("committed algos per gov. / all committed algos")
#plt.xlim([0,40])
#plt.ylim([0,0.1])
img.savefig()
plt.close()

# -----------------------------------------------------
# Plot committed algo per account vs the
# percentage of total committed algo.
# -----------------------------------------------------
fig, ax = plt.subplots()
plt.scatter(
    gov1.committed_algos/1e6,
    gov1.committed_ratio,
    edgecolor="green",
    facecolor="none",
    s=200,
    alpha=0.5,
    label="Gov. period 1 (all accounts)",
    )
plt.scatter(
    gov1_eligible.committed_algos/1e6,
    gov1_eligible.committed_ratio,
    edgecolor="green",
    facecolor="none",
    s=200,
    label="Gov. period 1 (eligible at end)",
    )
plt.scatter(
    gov2.committed_algos/1e6,
    gov2.committed_ratio,
    edgecolor="blue",
    facecolor="none",
    s=200,
    label="Gov. period 2 (all accounts)",
    )
plt.legend(fontsize=12,loc="lower right")
plt.grid()
plt.xlabel("committed algos per governor [millions]")
plt.ylabel("committed algos per gov. / all committed algos")
plt.xlim([0,40])
plt.ylim([0,0.1])
img.savefig()
plt.close()

# -----------------------------------------------------
# Plot overlap.
# -----------------------------------------------------
# all overlap:
fig,ax = plt.subplots()
plt.scatter(
    gov1.loc[overlap.address,"committed_algos"]/1e6,
    gov2.loc[overlap.address,"committed_algos"]/1e6,
    edgecolor="black",
    facecolor="none",
    s=200,
    label="overlap addresses\n(%d total)"%(len(overlap.address)),
    )
#plt.plot(
#    [0,20],
#    [0,20],
#    color="black",
#    label="1:1 ratio",    
#    )
plt.grid()
plt.legend()
#plt.xlim([0,12])
#plt.ylim([0,12])
plt.xlabel("committed algos per account in Gov. period 1 [millions]")
plt.ylabel("committed algos per account\nin Gov. period 2 [millions]")
img.savefig()
plt.close()

# all overlap, excluding the largest period 1 whale:
fig,ax = plt.subplots()
plt.scatter(
    gov1.loc[overlap.address,"committed_algos"]/1e6,
    gov2.loc[overlap.address,"committed_algos"]/1e6,
    edgecolor="black",
    facecolor="none",
    s=200,
    label="overlap addresses\n(%d total)"%(len(overlap.address)),
    )
plt.plot(
    [0,20],
    [0,20],
    color="black",
    label="1:1 ratio",    
    )
plt.grid()
plt.legend()
plt.xlim([0,20])
plt.ylim([0,20])
plt.xlabel("committed algos per account in Gov. period 1 [millions]")
plt.ylabel("committed algos per account\nin Gov. period 2 [millions]")
img.savefig()
plt.close()

# overlap of accounts that remained eligible in gov. period 1:
fig,ax = plt.subplots()
plt.scatter(
    gov1.loc[overlap_eligible.address,"committed_algos"]/1e6,
    gov2.loc[overlap_eligible.address,"committed_algos"]/1e6,
    edgecolor="black",
    facecolor="none",
    s=200,
    label="gov.1 eligible overlap addresses\n(%d total)"%(len(overlap_eligible.address)),
    )
plt.plot(
    [0,20],
    [0,20],
    color="black",
    label="1:1 ratio",    
    )
plt.grid()
plt.legend()
plt.xlim([0,12])
plt.ylim([0,12])
plt.xlabel("committed algos per eligible account in Gov. period 1 [millions]")
plt.ylabel("committed algos per account\nin Gov. period 2 [millions]")
img.savefig()
plt.close()









