import numpy as np
import pandas as pd

# read data:
df = pd.read_excel("bin/whale-control.xlsx",index_col=[1])

# prep table:
table_header = """%
\\begin{longtable}[c]{ c c }
\caption{Governance period 2's largest eligible whale commitments relative to the total eligible commitment on 2022-02-02.} \\\\
\hline
\\textbf{Top whales cutoff} & \\textbf{Whale commitment ratio} \\\\
\hline
"""
with open("table-whale-control.tex","w") as of:
    of.write(table_header)
    for ci in [1,5,25,50,75,100]:
        row = "%d & %.3f \\\\ \n" %(ci,df.loc[ci,"ratio"])
        of.write(row)
    of.write("\hline \n")
    of.write("\end{longtable} \n")

