import numpy as np
import pandas as pd
import json
from datetime import datetime
from subprocess import Popen, PIPE

# -----------------------------------------------------
# Local functions.
# -----------------------------------------------------
# function to query the API via curl:
def governance_api_query(
    governance_period, #integer
    offset, #integer
    verbose=True,
    ):
    url = [
        "https://governance.algorand.foundation/api",
        "periods/governance-period-%d/governors"%governance_period,
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
    results_item,
    data_list,
    ):
    address = results_item["account"]["address"]
    committed_algos = results_item["committed_algo_amount"]
    eligible_flag = results_item["is_eligible"]
    registration_datetime = results_item["registration_datetime"]
    data_list.append([
        address, #wallet public address
        registration_datetime, #datetime Zulu (UTC)
        committed_algos, #micro-algos
        eligible_flag, #governance eligibility 
        ])

# -----------------------------------------------------
# Query API.
# -----------------------------------------------------
# define an upper bound for the number of API
# calls so that we don't run forever:
max_number_of_pages = 800

# itervate over each governance period: 
for governance_period in [1,2]:
    current_page = 0
    data_list = []
    
    # query each page until all results are returned,
    # or we reach the max number of pages specified
    # by the user:
    while current_page < max_number_of_pages:
        results = governance_api_query(
            governance_period,
            current_page*100,
            )
        
        # list concatenation provides better efficiency:
        [extract_governor_data(x,data_list) for x in results]
        
        # break if no more pages:
        if len(results) < 100:
            print("final page: %d"%current_page)
            break
        else:
            current_page += 1

    # convert to pandas dataframe:
    df = pd.DataFrame(
        data_list,
        columns=[
            "address",
            "registration",
            "committed_algos",
            "eligible",
            ],
        )

    # format data where applicable and save.
    # the api returns algos as 'microalgos'; divide 
    # by 1e6 to get the number of actual algos:
    df.loc[:,"committed_algos"] = df.committed_algos.apply(float)/10e6
    df.loc[:,"registration"] = pd.to_datetime(df.registration)
    output_fi = "bin/%s-algorand-governance-period-%d.hdf"%(
        datetime.today().strftime("%Y-%m-%d"),
        governance_period,
        )
    df.to_hdf(output_fi,"w",mode="w")





