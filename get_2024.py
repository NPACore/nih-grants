#!/usr/bin/env python
"""
also see
https://github.com/neonwatty/pynih/blob/main/pynih/apis.py
"""
import requests
import time
import pickle
APIURL = "https://api.reporter.nih.gov/v2/projects/search"

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
        # TODO: check meta['total'] < 15000 if i == 0
        fy2024.extend(res)
        last_pi = res[-1]['contact_pi_name']
        print(f"{i} ({i*limit}/{meta.get('total')} in {state}) {last_pi}")
        if(len(res)) < 500:
            print(f"  {state} total={(i-1)*limit + len(res)}")
            break

        i = i+1
        time.sleep(.5) # dont hammer the server
     # TODO: warn if we have exactly limit in len(res)

with open('2024.pkl', 'wb') as pkl:
    pickle.dump(fy2024, pkl)
