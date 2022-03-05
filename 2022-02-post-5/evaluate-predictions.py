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
# Read data.
# -------------------------------------------------------
# predictions:
ohm_accrual = pd.read_hdf("bin/ohm-accrual-sim.hdf")
full_rate_prediction = pd.read_csv(
    "bin/rebase-rate-estimates.csv",
    index_col=[0],
    parse_dates=True,
    )

# data:
full_rate_history = pd.read_excel(
    "bin/staking-reward-rate-history.xlsx",
    index_col=[0],
    comment="#",    
    parse_dates=True,
    )
full_rate_history.loc[:,"reward_rate"] = full_rate_history.reward_rate.apply(
    lambda x: float(x.replace("%",""))*1e-2    
    )

# restrict dates:
di = "2022-01-23"
de = "2022-03-01"
rate_prediction = full_rate_prediction[full_rate_prediction.index<=de]
rate_history = full_rate_history[
    (full_rate_history.index>=di) 
    & (full_rate_history.index<=de)
    ]

# current data:
current_ohm = 3.1176
current_date = datetime.today()
current_price = 58.69 #USD

# -------------------------------------------------------
# Plot.
# -------------------------------------------------------
# define plot styles:
local_styles = {
    "best_case_rates": ["gray","--", "equiv. 1000 percent APY"],
    "worst_case_rates": ["black","--", "equiv. 500 percent APY"],
    "uniform_distr_rates": ["black", "-", "uniform distr."],
    }
rate_columns = [
    "best_case_rates",
    "worst_case_rates",
    "uniform_distr_rates",
    ]

# plot:
img = imghelper(
    save_dir="bin",
    img_series="results",
    save_flag=True,    
    )
with PdfPages("bin/plots-1.pdf") as pdf:

    # show my personal account Ohm growth:
    fig,ax = plt.subplots()
    plt.title("""OlympusDAO Ohm accrual estimate
compared to simplyrangel's current Ohm accrual""")
    for col in rate_columns:
        df = ohm_accrual.loc[col].reset_index().set_index("rebase")
        df = df[df.index<=de]
        c,l,label = local_styles[col]
        plt.plot(
            df.index,
            df.ohms,
            color=c,
            linestyle=l,
            label=label,
            )
    plt.scatter(
        df.index[0],
        2.6,
        color="black",
        marker="x",
        s=100,
        label="2.6 Ohm purchase\n at $293.57/Ohm",
        zorder=10,
        )
    plt.scatter(
        current_date,
        current_ohm,
        marker="x",
        color="red",
        s=100,
        label="%.2f Ohm currently in account"%current_ohm,
        zorder=10,
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("Ohm")
    plt.xticks(
        rate_prediction.index[::2*3],
        rotation=45,
        ha="right",
        )
    plt.tight_layout()
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()

    # show my personal account Ohm growth, full year:
    fig,ax = plt.subplots()
    plt.title("""OlympusDAO Ohm accrual estimate
compared to simplyrangel's current Ohm accrual""")
    for col in rate_columns:
        df = ohm_accrual.loc[col].reset_index().set_index("rebase")
        c,l,label = local_styles[col]
        plt.plot(
            df.index,
            df.ohms,
            color=c,
            linestyle=l,
            label=label,
            )
    plt.scatter(
        df.index[0],
        2.6,
        color="black",
        marker="x",
        s=100,
        label="2.6 Ohm purchase\n at $293.57/Ohm",
        zorder=10,
        )
    plt.scatter(
        current_date,
        current_ohm,
        marker="x",
        color="red",
        s=100,
        label="%.2f Ohm currently in account"%current_ohm,
        zorder=10,
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("Ohm")
    plt.xticks(
        full_rate_prediction.index[::2*7*3],
        rotation=45,
        ha="right",
        )
    plt.tight_layout()
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()

    # show my personal account breakeven prices:
    fig,ax = plt.subplots()
    plt.title("""OlympusDAO Ohm accrual estimate
simplyrangel's 1-year account break-even prices""")
    for col in rate_columns:
        df = ohm_accrual.loc[col].reset_index().set_index("rebase")
        c,l,label = local_styles[col]
        plt.plot(
            df.index,
            df.break_even_usd,
            color=c,
            linestyle=l,
            label=label,
            )
    plt.scatter(
        df.index[0],
        293.57,
        color="black",
        marker="x",
        s=100,
        label="2.6 Ohm purchase\n at $293.57/Ohm",
        zorder=10,
        )
    plt.axhline(
        current_price, #USD; current 1-Ohm price
        color="red",
        label="",
        )
    plt.text(
        df.index[0],
        current_price,
        "2022-02-19 price: $%.2f/Ohm"%current_price,
        ha="left",
        va="bottom",
        color="red",
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("USD break even price")
    plt.xticks(
        full_rate_prediction.index[::2*7*3],
        rotation=45,
        ha="right",
        )
    plt.tight_layout()
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()
    





