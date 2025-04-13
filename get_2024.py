#!/usr/bin/env python
"""
also see
https://github.com/neonwatty/pynih/blob/main/pynih/apis.py
"""
import requests
import time
import pickle
import os
APIURL = "https://api.reporter.nih.gov/v2/projects/search"

REQ_LIMIT=500 #: max allowed per request
QUERY_MAX=14999 #: max results in total for query

#  83170 results in web. expect 117 requests (500 at a time)
# >14999 so need to break up. try by state.
# this may create duplicates (MPI in mulitple states?)

US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC", "PR"
]

def nih_query_all(payload:dict, msg="") -> list:
    """
    Increment offset and resubmit payload until either
    results are exhausted or the max results allowed is hit

    :param payload: dict (json) to send to `APIURL`
    :param msg: message describing payload for printing status updates
    :return: list of dict: json results appended together
    """
    collected_data = []
    i = 0
    limit=payload['limit']
    while i*limit <= QUERY_MAX:
        payload['offset'] = i*limit
        resp = requests.post(APIURL,json=payload)
        try:
            json = resp.json()
        except Exception as e:
            print(resp)
            print(resp.reason)
            print(resp.raw.read())
            raise(e)

        res = json.get('results')
        meta = json.get('meta')

        if len(res) <= 0:
            print(f"no results in {msg})")
            break

        collected_data.extend(res)

        # progress reporting
        last_pi = res[-1]['contact_pi_name']
        print(f"{i} ({i*limit}/{meta.get('total')} in {msg}) {last_pi}")
        if(len(res)) < 500:
            print(f"  {msg} total={(i*limit) + len(res)}")
            break

        i = i+1
        time.sleep(.5) # dont hammer the server

    if len(contact_pi_name) >= QUERY_MAX:
        print(f"  {msg} total={len(collected_data)} at query maximum. truncated results?")
    return collected_data



for year in reversed(range(2010,2025)): # last year not in range
    pkl_fname = f'{year}.pkl'
    if os.path.isfile(pkl_fname):
        print(f"# have {pkl_fname} mv or rm to redo")
        continue

    year_data = []
    for state in US_STATES:
        print(f"## {state} {year}")
        payload = {"criteria": {"fiscal_years":[year],
                                'org_states':[state]},
                   'offset': 0,
                   'limit': REQ_LIMIT, # 500
                   }
        state_year = nih_query_all(payload, msg=f"{state} {year}")
        year_data.extend(state_year)

    # have now combined all stats of this year into giant list
    # save out as pickle
    with open(pkl_fname, 'wb') as pkl:
        pickle.dump(year_data, pkl)
