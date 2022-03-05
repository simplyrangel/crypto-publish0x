"""Write difference from last week."""
import numpy as np
import pandas as pd

# read data:
gov_last = pd.read_hdf("bin/2022-02-23-algorand-governance-period-2.hdf")
gov_current = pd.read_hdf("bin/2022-03-03-algorand-governance-period-2.hdf")

# extract eligible accounts:
gov_last = gov_last[gov_last.eligible==True].copy()
gov_current = gov_current[gov_current.eligible==True].copy()

# set indices:
gov_last = gov_last.set_index("address",drop=False)
gov_current = gov_current.set_index("address",drop=False)

# exract committed algos count:
current_algos = gov_current.committed_algos.sum()/1e6
last_algos = gov_last.committed_algos.sum()/1e6

# calculate reward rate:
p2_reward = 70.5 #millions
current_reward_rate = 1.0 + p2_reward/current_algos
last_reward_rate = 1.0 + p2_reward/last_algos

# define latex table:
table_header = """%
\\begin{longtable}[c]{ l c c c }
\caption{Governance period 2's eligible governors and their total committed Algo vs last week (March 3 vs Feb. 23)} \\\\
\hline
\\textbf{parameter} & \\textbf{P2 (Feb. 23)} & \\textbf{P2 (March 3)} & \\textbf{Difference} \\\\
\hline
"""
table_data = """
Eligible governors & {c00} & {c01} & {c02} \\\\
Committed algos [millions] & {c10} & {c11} & {c12} \\\\
Period reward rate & {c20} & {c21} & {c22} \\\\
\hline
""".format(
    c00=gov_last.shape[0],
    c10=round(last_algos,2),
    c20=round(last_reward_rate,3),
    c01=gov_current.shape[0],
    c11=round(current_algos,2),
    c21=round(current_reward_rate,3),
    c02=gov_current.shape[0]-gov_last.shape[0],
    c12=round(current_algos-last_algos,2),
    c22=round(current_reward_rate-last_reward_rate,4),
    )
with open("table-last-week-diff.tex","w") as of:
    of.write(table_header)
    of.write(table_data)
    of.write("\end{longtable} \n")
    
    
    
    
    
