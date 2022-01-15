import numpy as np
import pandas as pd
import json
from datetime import datetime
from subprocess import Popen, PIPE

# -----------------------------------------------------
# Local functions.
# -----------------------------------------------------
# function to query the API via curl:
def governance_api_query(offset,verbose=True):
    url = [
        "https://governance.algorand.foundation/api",
        "periods/governance-period-2/governors",
        "?ordering=-registration_datetime&limit=100&offset=%d"%offset,
        ]
    url = "/".join(url)
    if verbose:
        print(url)
    cmd = [
        "curl",
        url,
        "--header",
        "Accept: application/json",
        "--header",
        "Content-Type: application/json",
        ]
    p = Popen(cmd,stdout=PIPE,stderr=PIPE)
    stdout,stderr = p.communicate()
    return json.loads(stdout)["results"]

# function to extract governance data we care about from the
# 'results' object returned by the API:
def extract_governor_data(
    query_results,
    data_list,
    ):
    address = query_results["account"]["address"]
    committed_algos = query_results["committed_algo_amount"]
    eligible_flag = query_results["is_eligible"]
    registration_datetime = query_results["registration_datetime"]
    data_list.append([
        address,
        registration_datetime,
        committed_algos,
        eligible_flag,
        ])

# -----------------------------------------------------
# Query API.
# -----------------------------------------------------
max_number_of_pages = 700
current_page = 0
data_list = []
while current_page < max_number_of_pages:
    results = governance_api_query(current_page*100)
    [extract_governor_data(x,data_list) for x in results]
    if len(results) < 100:
        print("final page: %d"%current_page)
        break
    else:
        current_page += 1

# -----------------------------------------------------
# Save data.
# -----------------------------------------------------
# convert to pandas dataframe:
df = pd.DataFrame(
    data_list,
    columns=["address","registration","committed_algos","eligible"],
    )

# format data where applicable and save:
df.loc[:,"committed_algos"] = df.committed_algos.apply(float)/10e6
df.loc[:,"registration"] = pd.to_datetime(df.registration)
df.to_hdf("bin/algorand-governance-period-2.hdf","w",mode="w")





