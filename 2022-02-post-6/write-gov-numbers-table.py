import numpy as np
import pandas as pd

# read data:
gov_period2 = pd.read_hdf("bin/2022-02-23-algorand-governance-period-2.hdf")
gov_period1 = pd.read_hdf("bin/2022-01-15-algorand-governance-period-1.hdf")

# extract eligible accounts:
gov_period2 = gov_period2[gov_period2.eligible==True].copy()
gov_period1 = gov_period1[gov_period1.eligible==True].copy()

# set indices:
gov_period2 = gov_period2.set_index("address",drop=False)
gov_period1 = gov_period1.set_index("address",drop=False)

# exract committed algos count:
p1_algos = gov_period1.committed_algos.sum()/1e6
p2_algos = gov_period2.committed_algos.sum()/1e6

# calculate reward rate:
p1_reward = 60.0 #millions
p2_reward = 70.5 #millions
p1_reward_rate = 1.0 + p1_reward/p1_algos
p2_reward_rate = 1.0 + p2_reward/p2_algos

# define latex table:
table_header = """%
\\begin{longtable}[c]{ l c c c }
\caption{Governance period 2's eligible governors and their total committed Algo vs Governance period 1. Period 2 data queried 2022-02-23.} \\\\
\hline
\\textbf{parameter} & \\textbf{Period 1} & \\textbf{Period 2 (Feb. 23)} & \\textbf{P2/P1} \\\\
\hline
"""
table_data = """
Eligible governors & {c00} & {c01} & {c02} \\\\
Committed algos [millions] & {c10} & {c11} & {c12} \\\\
Rewards pool [millions] & 60 & 70.5 & 1.175 \\\\
Period reward rate & {c30} & {c31} & {c32} \\\\
\hline
""".format(
    c00=gov_period1.shape[0],
    c10=round(p1_algos,2),
    c01=gov_period2.shape[0],
    c11=round(p2_algos,2),
    c02=round(gov_period2.shape[0]/gov_period1.shape[0], 2),
    c12=round(p2_algos/p1_algos,2),
    c30=round(p1_reward_rate,4),
    c31=round(p2_reward_rate,4),
    c32=round(p2_reward_rate/p1_reward_rate,4),
    )
with open("table-gov-numbers.tex","w") as of:
    of.write(table_header)
    of.write(table_data)
    of.write("\end{longtable} \n")
    
