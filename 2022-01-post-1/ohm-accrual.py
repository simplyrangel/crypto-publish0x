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
    "bin/rebase-rate-estimates.csv",
    index_col=[0],
    parse_dates=True,
    )

# -------------------------------------------------------
# Accrue Ohm.
# -------------------------------------------------------
rate_columns = [
    "best_case_rates",
    "worst_case_rates",
    "uniform_distr_rates",
    ]
def ohm_accrual_sim(
    ohmi,
    purchase_usd,
    rebase_rates=rebase_rates,
    rate_columns=rate_columns,
    ):
    frames = []
    for rate_set in rate_columns:
        df = pd.DataFrame(
            np.nan,
            columns=["rebase_rate","ohms"],
            index=rebase_rates.index,
            )
        df.loc[:,"rebase_rate"] = rebase_rates[rate_set]
        df.iloc[0].loc["ohms"] = ohmi
        for rebase_id in range(1, len(df.index)):
            ohm0 = df.iloc[rebase_id-1].ohms
            r = df.iloc[rebase_id].rebase_rate
            df.iloc[rebase_id].loc["ohms"] = ohm0*(1.0+r)
        
        df["break_even_usd"] = (purchase_usd*ohmi) / df.ohms
        frames.append(df)
    return pd.concat(frames,keys=rate_columns,names=["rate_type","rebase"])

# My personal account:
personal_results = ohm_accrual_sim(
    0.9378,
    321.0, #USD  
    )

# baseline account of 1-Ohm purchase at current market:
baseline_results = ohm_accrual_sim(
    1.0,
    263.0,    
    )

# summary of results:
df0 = personal_results.loc[
    idx[:,"2023-01-08 00:00:00"],
    ["ohms","break_even_usd"],
    ]
df1 = baseline_results.loc[
    idx[:,"2023-01-08 00:00:00"],
    ["ohms","break_even_usd"],
    ]
output = pd.concat([df0,df1],keys=["simplyrangel","baseline"])
output.to_excel("bin/one-year-output.xlsx")

# -------------------------------------------------------
# Plot.
# -------------------------------------------------------
# define plot styles:
local_styles = {
    "best_case_rates": ["gray","--", "equiv. 1000 percent APY"],
    "worst_case_rates": ["black","--", "equiv. 500 percent APY"],
    "uniform_distr_rates": ["black", "-", "uniform distr."],
    }

# plot:
img = imghelper(
    save_dir="bin",
    img_series="ohm-accrual",
    save_flag=True,    
    )
with PdfPages("bin/plots-1.pdf") as pdf:
    
    # show my personal account Ohm growth:
    fig,ax = plt.subplots()
    plt.title("""OlympusDAO Ohm accrual estimate
simplyrangel's 1-year account growth""")
    for col in rate_columns:
        df = personal_results.loc[col].reset_index().set_index("rebase")
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
        0.9378,
        color="red",
        marker="x",
        s=100,
        label="0.9378 Ohm purchase\n for 321.0USD",
        zorder=10,
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("Ohm")
    plt.xticks(
        rebase_rates.index[::2*7*3],
        rotation=45,
        ha="right",
        )
    plt.ylim([0,12])
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
        df = personal_results.loc[col].reset_index().set_index("rebase")
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
        321.0,
        color="red",
        marker="x",
        s=100,
        label="0.9378 Ohm purchase\n for 321.0USD",
        zorder=10,
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("USD break even price")
    plt.xticks(
        rebase_rates.index[::2*7*3],
        rotation=45,
        ha="right",
        )
    plt.ylim([0,400])
    plt.tight_layout()
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()

    # show baseline account Ohm growth:
    fig,ax = plt.subplots()
    plt.title("""OlympusDAO Ohm accrual estimate
baseline 1-year account growth""")
    for col in rate_columns:
        df = baseline_results.loc[col].reset_index().set_index("rebase")
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
        1.0,
        color="red",
        marker="x",
        s=100,
        label="1.0 Ohm purchase\n for 263.0USD",
        zorder=10,
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("Ohm")
    plt.xticks(
        rebase_rates.index[::2*7*3],
        rotation=45,
        ha="right",
        )
    plt.ylim([0,12])
    plt.tight_layout()
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()

    # show my baseline breakeven prices:
    fig,ax = plt.subplots()
    plt.title("""OlympusDAO Ohm accrual estimate
baseline 1-year account break-even prices""")
    for col in rate_columns:
        df = baseline_results.loc[col].reset_index().set_index("rebase")
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
        263.0,
        color="red",
        marker="x",
        s=100,
        label="1.0 Ohm purchase\n for 263.0USD",
        zorder=10,
        )
    plt.legend()
    plt.grid()
    plt.xlabel("date")
    plt.ylabel("USD break even price")
    plt.xticks(
        rebase_rates.index[::2*7*3],
        rotation=45,
        ha="right",
        )
    plt.ylim([0,300])
    plt.tight_layout()
    add_markings(ax)
    pdf.savefig()
    img.savefig()
    plt.close()


















        
