#!/usr/bin/env python
"""
also see
https://github.com/neonwatty/pynih/blob/main/pynih/apis.py
"""
import requests
import time
import pickle
import pandas as pd
APIURL = "https://api.reporter.nih.gov/v2/projects/search"
def extract_pi(pi: dict) -> str:
    """
    principal_investigators element to strings
    """
    return(str(pi.get("profile_id", "")) + ":" + pi.get("full_name", ""))

def contact_pi(pi_array) -> str:
    """
    get contact from principal_investigators
    """
    for pi in pi_array:
        return extract_pi(pi)
    return ""

limit=500 #: max allowed
fy2024 = []

#  83170 results in web. expect 117 requests (500 at a time)
# >14999 so need to break up. try by state.
# this may create duplicates (MPI in mulitple states?)

us_states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC", "PR"
]

for state in us_states:
    print(f"## {state}")
    i = 0
    while i*limit <= 14999:
        payload = {"criteria": {"fiscal_years":[2024],
                                'org_states':[state]},
                   'offset': i*limit,
                   'limit': 500,
                   }
        resp = requests.post(APIURL,json=payload)
        json = resp.json()
        res = json.get('results')
        meta = json.get('meta')
        fy2024.extend(res)
        last_pi = res[-1]['contact_pi_name']
        print(f"{i} ({i*limit}/{meta.get('total')} in {state}) {last_pi}")
        if(len(res)) < 500:
            print(f"  {state} total={(i-1)*limit + len(res)}")
            break

        i = i+1
        time.sleep(.5) # dont hammer the server

with open('2024.pkl', 'wb') as pkl:
    pickle.dump(fy2024, pkl)



keep = ['project_num','award_type','budget_start','budget_end','direct_cost_amt','indirect_cost_amt','project_start_date','project_end_date', 'award_amount', ]
per_pi = []
for grant in fy2024:
    pis_dict = grant['principal_investigators']
    n = len(pis_dict)
    contact = contact_pi(pis_dict)
    pis = [extract_pi(pi) for pi in pis_dict]
    ginfo = {k:v for k,v in grant.items() if k in keep}
    for pi in pis:
        pi_row = {"pi": pi, 'contact_pi': contact, **ginfo}
        # slow! but 'per_pi.extend(pi_row)' only takes keys?
        per_pi = per_pi + [pi_row]
d = pd.DataFrame(per_pi)
d.to_csv("FY2024_PI-repeat.csv")
